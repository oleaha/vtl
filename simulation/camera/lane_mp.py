from __future__ import division
from multiprocessing import Process, Queue, Event
from simulation import settings

import pickle
import time

import cv2
import picamera
import numpy as np
import picamera.array
import logging


class LaneDetectionMP(Process):

    def __init__(self, measurements):
        super(LaneDetectionMP, self).__init__()
        self.exit = Event()
        self.exitFlag = False
        self.debug = settings.LANE_DEBUG
        self.camera = None
        self.rawCapture = None
        self.current_center_list = []
        self.measurements = measurements

    def init_camera(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = settings.CAMERA_RESOLUTION
        self.camera.framerate = settings.CAMERA_FRAME_RATE
        self.rawCapture = picamera.array.PiRGBArray(self.camera)
        time.sleep(0.1)

    def run(self):
        logging.debug("Process started")
        self.lane_detection()
        logging.debug("Process stopped")

    @staticmethod
    def gray_scale(image):
        """
        Takes an image and converts in from RGB to grayscale
        :param image:
        :return: Grayscaled image
        """
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    @staticmethod
    def gaussian_smoothing(image, kernel_size):
        """
        Takes an image and applies gaussian blur with given kernel size.
        Purpose is to reduce noise in the image
        :param image:
        :param kernel_size:
        :return: Blurred image
        """
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    @staticmethod
    def canny_detector(image, low, high):
        """
        Applies the Canny Edge Detector algorithm on the given image with given thresholds
        Rule: High = 3x low
        :param image:
        :param low:
        :param high:
        :return: Black/white image with multiple edged
        """
        return cv2.Canny(image, low, high)

    @staticmethod
    def region_selection(image):
        """
        Restricts the area to look for lanes
        :param image:
        :return: Masked and cropped image with only region of interest
        """
        mask = np.zeros_like(image)

        if len(image.shape) > 2:
            ignore_mask_color = (255,) * image.shape[2]
        else:
            ignore_mask_color = 255

        # rows = height, y 480
        # cols = width, x 752
        rows, cols = image.shape[:2]

        bottom_left = [0, 450]
        top_left = [230, 300]
        bottom_right = [720, 480]
        top_right = [540, 310]

        vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
        cv2.fillPoly(mask, vertices, ignore_mask_color)
        masked_image = cv2.bitwise_and(image, mask)

        return masked_image

    @staticmethod
    def hough_transform(image):
        """
        Applies the Hough Transform algorithm to convert edged to physical points (x, y)->(x, y)
        within given thresholds and parameters
        :param image:
        :return: An array of lines with points
        """
        rho = 1  # Distance resolution of the accumulator in pixels
        theta = np.pi / 180  # Angle resolution of the accumulator in radians
        threshold = 100  # Only lines greater than threshold will be returned
        minLineLength = 50  # Line segments shorter than this is rejected
        maxLineGap = 40  # Maximum allowes gap between two points on the same line to link them
        return cv2.HoughLinesP(image, rho=rho, theta=theta, threshold=threshold,
                               minLineLength=minLineLength, maxLineGap=maxLineGap)

    @staticmethod
    def draw_lines(image, lines, color=[255, 0, 0], thickness=2):
        """
        Draw lines on image to verify where what lines the algorithm finds
        Mainly for testing and debugging
        :param image:
        :param lines:
        :param color:
        :param thickness:
        :return:
        """
        image = np.copy(image)
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(image, (x1, y1), (x2, y2), color, thickness)
        return image

    @staticmethod
    def average_slope(lines):
        """
        Find left and right lanes and average their slopes in order to create one solid line for each lane
        :param lines:
        :return: Left and right lane with (x,y) start and (x, y) stop
        """
        left_lines = []
        left_weights = []
        right_lines = []
        right_weights = []
        if len(lines) > 0:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    if x1 == x2:
                        continue
                    slope = (y2 - y1) / (x2 - x1)
                    intercept = y1 - (slope * x1)
                    length = np.sqrt(((y2 - y1) ** 2) + ((x2 - x1) ** 2))
                    if slope < 0.1 and slope > -0.1:
                        continue
                    if slope < 0:
                        left_lines.append((slope, intercept))
                        left_weights.append((length))
                    else:
                        right_lines.append((slope, intercept))
                        right_weights.append((length))
            left_lane = np.dot(left_weights, left_lines) / np.sum(left_weights) if len(left_weights) > 0 else None
            right_lane = np.dot(right_weights, right_lines) / np.sum(right_weights) if len(right_weights) > 0 else None
            if left_lane is not None and left_lane[0] > -0.1:
                left_lane = None
            if right_lane is not None and right_lane[0] < 0.1:
                right_lane = None
            return left_lane, right_lane
        return 0, 0

    @staticmethod
    def pixel_points(y1, y2, line):
        """
        Find the pixel poins for each lane
        :param y1:
        :param y2:
        :param line:
        :return:
        """
        if line is None:
            return None
        slope, intercept = line
        if slope == 0.0:
            return None
        # logging.info("Slope: " + str(slope) + " Intercept: " + str(intercept))
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        y1 = int(y1)
        y2 = int(y2)
        return (x1, y1), (x2, y2)

    def lane_lines(self, image, lines):
        """
        Find left and right lane
        :param image:
        :param lines:
        :return:
        """
        if len(lines) > 0:
            left_lane, right_lane = self.average_slope(lines)
            y1 = image.shape[0]
            y2 = y1 * 0.6
            left_line = self.pixel_points(y1, y2, left_lane)
            right_line = self.pixel_points(y1, y2, right_lane)
            return left_line, right_line
        return None, None

    def draw_lane_lines(self, image, lines, color=[255, 0, 0], thickness=12):
        """
        Draw the lanes on the frame, or find the center point for the heading of the robot
        :param image:
        :param lines:
        :param color:
        :param thickness:
        :return:
        """
        top_center_x = 0

        if lines is not None:
            if lines[0] is not None and lines[1] is not None:
                top_center_x = (lines[0][1][0] + lines[1][1][0]) / 2
            elif lines[0] is None:
                top_center_x = 0
            elif lines[1] is None:
                top_center_x = 752

            if self.debug:
                cv2.putText(image, "Top center x: " + str(top_center_x), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            [0, 0, 255], 1)
        if self.debug:
            for line in lines:
                if line:
                    cv2.line(image, line[0], line[1], color, thickness)
            return image
        return top_center_x

    def lane_detection(self):

        self.init_camera()

        while not self.exitFlag:
            for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):

                with open("calibration_matrix.txt", 'r') as f:
                    calibration_matrix = pickle.load(f)

                img = frame.array

                undistorted = cv2.undistort(img, calibration_matrix['mtx'], calibration_matrix['dist'], None,
                                            calibration_matrix['mtx'])
                gray = self.gray_scale(img)
                blurred = self.gaussian_smoothing(gray, 3)
                edged = self.canny_detector(blurred, 50, 150)
                trimmed = self.region_selection(edged)
                houghlines = self.hough_transform(trimmed)

                if houghlines is None:
                    self.rawCapture.truncate()
                    self.rawCapture.seek(0)
                    continue

                if self.debug:
                    final = self.draw_lane_lines(img, self.lane_lines(img, houghlines))
                    cv2.line(final, (0, 450), (230, 300), [0, 255, 0], 2)
                    cv2.line(final, (720, 480), (540, 310), [0, 255, 0], 2)
                    cv2.line(final, (230, 300), (540, 310), [0, 255, 0], 2)
                    cv2.imshow("Lane Detection", final)

                    self.current_center_list.append(final)
                    if len(self.current_center_list) % 3 == 0:
                        self.measurements.put(self.current_center_list[-5:])

                    key = cv2.waitKey(1) & 0xFF
                    self.rawCapture.truncate()
                    self.rawCapture.seek(0)
                    if key == ord("q"):
                        break
                else:
                    current_center = self.draw_lane_lines(undistorted, self.lane_lines(img, houghlines))
                    self.rawCapture.truncate()
                    self.rawCapture.seek(0)

                    # logging.info("Adding new measurement to list - " + str(current_center))
                    self.current_center_list.append(current_center)

                    if len(self.current_center_list) % 3 == 0:
                        #logging.info("Adding new measurements to queue - " + str(self.current_center_list[-5:]))
                        self.measurements.put(self.current_center_list[-5:])

    def stop_process(self):
        self.exitFlag = True
        self.camera.close()
        self.exit.set()
