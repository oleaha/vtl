import numpy as np
import cv2
import glob
import matplotlib as mlp
import matplotlib.pyplot as plt


def camera_chessboards(glob_regex='test_images/chess*.jpg'):
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6 * 9, 3), np.float32)
    objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

    # Arrays to store object points and image points from all the images.
    objpoints = []  # 3d points in real world space
    imgpoints = []  # 2d points in image plane.
    chessboards = []  # array of chessboard images

    # Make a list of calibration images
    images = glob.glob(glob_regex)

    # Step through the list and search for chessboard corners
    for idx, fname in enumerate(images):
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find the chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

        # If found, add object points, image points
        if ret == True:
            objpoints.append(objp)
            imgpoints.append(corners)

            # Draw and display the corners
            cv2.drawChessboardCorners(img, (9, 6), corners, ret)
            chessboards.append(img)

    return objpoints, imgpoints, chessboards


objpoints, imgpoints, chessboards = camera_chessboards()

#plt.imshow(chessboards[0], cmap=plt.cm.gray_r, interpolation='nearest')
#plt.title('Chessboard: %d' % 0)
#plt.show()


def camera_calibrate(objpoints, imgpoint, img):
    img_size = img.shape[0:2]
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoint, img_size, None, None)
    dst = cv2.undistort(img, mtx, dist, None, mtx)
    return ret, mtx, dist, dst


img = cv2.imread("test_images/chess_1.jpg")
ret, mtx, dist, dst = camera_calibrate(objpoints, imgpoints, img)

f, axarr = plt.subplots(1, 2)
axarr[0].imshow(img)
axarr[1].imshow(dst)
plt.show()
