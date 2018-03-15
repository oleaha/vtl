from __future__ import division

import pickle
import time

import cv2
import picamera
import numpy as np
import picamera.array

camera = picamera.PiCamera()
camera.resolution = (752, 480)
camera.framerate = 5
camera.vflip = False
camera.hflip = False
rawCapture = picamera.array.PiRGBArray(camera)
time.sleep(0.1)

debug = True

def gray_scale(image):
    """
    Takes an image and converts in from RGB to grayscale
    :param image:
    :return: Grayscaled image
    """
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def gaussian_smoothing(image, kernel_size):
    """
    Takes an image and applies gaussian blur with given kernel size.
    Purpose is to reduce noise in the image
    :param image:
    :param kernel_size:
    :return: Blurred image
    """
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


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


def hough_transform(image):
    """
    Applies the Hough Transform algorithm to convert edged to physical points (x, y)->(x, y)
    within given thresholds and parameters
    :param image:
    :return: An array of lines with points
    """
    rho = 1  # Distance resolution of the accumulator in pixels
    theta = np.pi / 180  # Angle resolution of the accumulator in radians
    threshold = 20  # Only lines greater than threshold will be returned
    minLineLength = 50  # Line segments shorter than this is rejected
    maxLineGap = 40  # Maximum allowes gap between two points on the same line to link them
    return cv2.HoughLinesP(image, rho=rho, theta=theta, threshold=threshold,
                           minLineLength=minLineLength, maxLineGap=maxLineGap)


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

                if slope < 0:
                    left_lines.append((slope, intercept))
                    left_weights.append((length))
                else:
                    right_lines.append((slope, intercept))
                    right_weights.append((length))
        left_lane = np.dot(left_weights, left_lines) / np.sum(left_weights) if len(left_weights) > 0 else None
        right_lane = np.dot(right_weights, right_lines) / np.sum(right_weights) if len(right_weights) > 0 else None
        return left_lane, right_lane
    return 0, 0


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
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    y1 = int(y1)
    y2 = int(y2)
    return ((x1, y1), (x2, y2))


def lane_lines(image, lines):
    """
    Find left and right lane
    :param image:
    :param lines:
    :return:
    """
    if lines.all() and len(lines) > 0:
        left_lane, right_lane = average_slope(lines)
        y1 = image.shape[0]
        y2 = y1 * 0.6
        left_line = pixel_points(y1, y2, left_lane)
        right_line = pixel_points(y1, y2, right_lane)
        return left_line, right_line
    return None, None


def draw_lane_lines(image, lines, color=[255, 0, 0], thickness=12):
    """
    Draw the lanes on the frame, or find the center point for the heading of the robot
    :param image:
    :param lines:
    :param color:
    :param thickness:
    :return:
    """
    if len(lines) == 2:
        if lines[0] is not None and lines[1] is not None:
            top_center_x = (lines[0][1][0] + lines[1][1][0]) / 2
        elif lines[0] is None:
            top_center_x = 0
        elif lines[1] is None:
            top_center_x = 752

        if debug:
            cv2.putText(image, "Top center x: " + str(top_center_x), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        [0, 0, 255], 1)
    if debug:
        for line in lines:
            if line:
                cv2.line(image, line[0], line[1], color, thickness)
        return image
    return top_center_x


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    with open("calibration_matrix.txt", 'r') as f:
        dict = pickle.load(f)

    img = frame.array

    undistorted = cv2.undistort(img, dict['mtx'], dict['dist'], None, dict['mtx'])

    gray = gray_scale(undistorted)

    blurred = gaussian_smoothing(gray, 3)

    edged = canny_detector(blurred, 50, 150)

    trimmed = region_selection(edged)

    houghlines = hough_transform(trimmed)

    if debug:
        final = draw_lane_lines(undistorted, lane_lines(img, houghlines))
        cv2.line(final, (0, 450), (230, 300), [0, 255, 0], 2)
        cv2.line(final, (720, 480), (540, 310), [0, 255, 0], 2)
        cv2.line(final, (230, 300), (540, 310), [0, 255, 0], 2)
        cv2.imshow("Lane Detection", final)

        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate()
        rawCapture.seek(0)
        if key == ord("q"):
            break
    else:
        print draw_lane_lines(undistorted, lane_lines(img, houghlines))
        rawCapture.truncate()
        rawCapture.seek(0)

