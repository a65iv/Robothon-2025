import cv2
import numpy as np
from modules.Camera import Cam 
from modules.EpsonController import EpsonController
from modules.ColorPerception import ColorPerception, ColorFilter


# Setting up color filters
RED_FILTER_ON = ColorFilter(
    "red",
    [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([160, 100, 100]), np.array([180, 255, 255]))
    ],
    brightness_threshold=10  # Only detect bright red (50 is the max)
)

RED_FILTER_OFF = ColorFilter(
    "red",
    [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([160, 100, 100]), np.array([180, 255, 255]))
    ],
    brightness_threshold=10  # Only detect bright red (50 is the max)
)

BLUE_FILTER_ON = ColorFilter(
    "blue",
    [
        (np.array([100, 150, 0]), np.array([140, 255, 255]))
    ],
    brightness_threshold=10  # Only detect bright blue (50 is the max)
)

BLUE_FILTER_OFF = ColorFilter(
    "blue",
    [
        (np.array([100, 150, 0]), np.array([140, 255, 255]))
    ],
    brightness_threshold=10  # Only detect bright blue (50 is the max)
)




cam = Cam(0)
epson = EpsonController()
colorPerception = ColorPerception()

# take picture from home point
cam.take_picture(filename="./local-frame.png")

# find red and blue buttons
colorPerception.set_filters([RED_FILTER_OFF, BLUE_FILTER_OFF])

# get the point values for right and left
print("Detecting red and blue buttons....")
image = cv2.imread("./local-frame.png")
_, points = colorPerception.detect_main_color_midpoints(image)


cam_point_A = points.get("red")
cam_point_B = points.get("blue")

print("Found buttons:", "blue button:", str(cam_point_B), "red button:", str(cam_point_A))

# get the world coordinate system
robot_point_A = epson.getWorldCoordinates(cam_point_A)
robot_point_B = epson.getWorldCoordinates(cam_point_B)

epson.setLocalFrame(robot_point_B, robot_point_A) 

epson.executeTask(EpsonController.Action.PEN_PICK)





