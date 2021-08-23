import cv2.aruco as aruco
import numpy as np

default_cameraMatrix = np.array([[392.75533375, 0., 284.73851876],
                                 [0., 413.9101659, 254.38799118], [0., 0.,
                                                                   1.]])
default_distCoeffs = np.array(
    [[0.0290911, -1.24869976, -0.01714862, -0.02837211, 3.59261617]])

aruco_dict = aruco.custom_dictionary(10, 6)


class ArUcoDetector():
    def __init__(self, marker_size=0.06) -> None:
        self.marker_size = marker_size

    def detect(self, bgr):
        ret = False
        x, y, z = 0, 0, 0
        corners, ids, _ = aruco.detectMarkers(bgr, aruco_dict)
        if ids is not None:
            _, tvecs, _ = aruco.estimatePoseSingleMarkers(
                corners, self.marker_size, default_cameraMatrix,
                default_distCoeffs)
            x = tvecs[0][0][0].item()
            y = tvecs[0][0][1].item()
            z = tvecs[0][0][2].item()
            if z > 0.05:
                aruco.drawDetectedMarkers(bgr, corners, ids)
                ret = True
        return ret, x, y, z
