import cv2
import numpy as np
from modules.Camera import Cam 
from modules.EpsonController import EpsonController
from time import sleep
from modules.ColorDetector import ColorDetector, ColorFilter


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
colorPerception = ColorDetector()

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
epson.executeTask(EpsonController.Action.PRESS_RED_BLUE_RED)
sleep(7)
epson.executeTask(EpsonController.Action.PRESS_RED)
sleep(3)
#epson.executeTask(EpsonController.Action.PRESS_BLUE)
#sleep(1)
epson.executeTask(EpsonController.Action.PEN_PICK)
sleep(7)
epson.executeTask(EpsonController.Action.SCREEN_CAMERA)
sleep(3)
epson.executeTask(EpsonController.Action.DRAW_CIRCLE)
sleep(3)
# epson.executeTask(EpsonController.Action.DRAW_TRIANGLE)
# sleep(3)
# epson.executeTask(EpsonController.Action.DRAW_SQUARE)
# sleep(3)
# epson.executeTask(EpsonController.Action.TAP_A)
# sleep(3)
# epson.executeTask(EpsonController.Action.TAP_B)
# sleep(3)
# epson.executeTask(EpsonController.Action.TAP_G)
# sleep(3)
# epson.executeTask(EpsonController.Action.DTAP_A)
# sleep(3)
# epson.executeTask(EpsonController.Action.DTAP_B)
# sleep(3)
epson.executeTask(EpsonController.Action.DTAP_G)
sleep(4)
epson.executeTask(EpsonController.Action.SWIPE_AB)
sleep(3)
# epson.executeTask(EpsonController.Action.SWIPE_BA)
# sleep(3)
# epson.executeTask(EpsonController.Action.SWIPE_AG)
# sleep(3)
epson.executeTask(EpsonController.Action.SWIPE_BG)
sleep(3)
#epson.executeTask(EpsonController.Action.SWIPE_GA)
#sleep(3)
epson.executeTask(EpsonController.Action.SWIPE_GB)
sleep(3)
epson.executeTask(EpsonController.Action.BALL_MAZE_1)
sleep(20)
epson.executeTask(EpsonController.Action.BALL_MAZE_2)
sleep(40)
epson.executeTask(EpsonController.Action.PEN_PLACE)

