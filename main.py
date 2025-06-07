import cv2
import numpy as np
import threading
from modules.Camera import Cam 
from modules.EpsonController import EpsonController
from modules.ColorDetectorClass import ColorDetector, ColorFilter


# Initializing modules
cam = Cam(0)
epson = EpsonController()

BLUE_FILTER_ON = ColorFilter("blue", [
    (np.array([100, 150, 0]), np.array([140, 255, 255]))
],
    brightness_threshold=150  
)

RED_FILTER_ON = ColorFilter("red",[
    (np.array([0, 100, 100]), np.array([10, 255, 255])),
    (np.array([160, 100, 100]), np.array([180, 255, 255]))
],
    brightness_threshold=100  # Only detect bright red (50 is the max)
)

blue_point = None
red_point= None

blue_on = False
red_on = False

def set_blue_point(midpoint):
    global blue_point 
    blue_point = epson.getWorldCoordinates(midpoint)

def set_red_point(midpoint):
    global red_point 
    red_point = epson.getWorldCoordinates(midpoint)


def set_blue_on(midpoint):
    global blue_on 
    blue_on = True if midpoint is not None else False 

def set_red_on(midpoint):
    global red_on 
    red_on = True if midpoint is not None else False 


BlueDetector = ColorDetector("BlueDetector", filters=[ColorDetector.BLUE_FILTER], callback=set_blue_point) 
RedDetector = ColorDetector("RedDetector", filters=[ColorDetector.RED_FILTER], callback=set_red_point) 
BlueOnDetector = ColorDetector("BlueOnDetector", filters=[BLUE_FILTER_ON], callback=set_blue_on) 
RedOnDetector = ColorDetector("RedOnDetector", filters=[RED_FILTER_ON], callback=set_red_on) 


# Run cameras feed with detectors
# Start the video loop in a new thread
video_thread = threading.Thread(target=cam.live_feed, kwargs={
    'detectors': [RedDetector, BlueDetector, RedOnDetector, BlueOnDetector]
}, daemon=True)
video_thread.start()



print("hello there")
print("what is up")
