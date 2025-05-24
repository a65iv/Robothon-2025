from modules.Calibrator import Calibrator

import cv2
import pathlib
calibrator = Calibrator(calibrate=False)
path = pathlib.Path("./pic.png")

"""
    REAL_X_POS_END = -136.203
    REAL_Y_POS_END = 787.229
    REAL_Z_POS = 395.870 
    
    REAL_X_POS_START = 163.371
    REAL_Y_POS_START = 558.528
    REAL_Z_POS = 390.094
"""

# image = cv2.imread(filename=path)

# for i in 



calibrator.detect_circles(path)
# calibrator.fix_camera_points()