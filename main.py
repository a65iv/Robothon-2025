import cv2
import numpy as np
import asyncio
from modules.Camera import Cam
from modules.EpsonController import EpsonController
from modules.ColorDetectorClass import ColorDetector, ColorFilter

# ─────────────────────────────────────────────
# Initialization
# ─────────────────────────────────────────────
cam = Cam(0)
epson = EpsonController()
detector = ColorDetector("ColorPerception")

# ─────────────────────────────────────────────
# Color filters for detecting "ON" state
# ─────────────────────────────────────────────
BLUE_FILTER_ON = ColorFilter(
    "blue",
    [(np.array([100, 150, 0]), np.array([140, 255, 255]))],
    brightness_threshold=150
)

RED_FILTER_ON = ColorFilter(
    "red",
    [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([160, 100, 100]), np.array([180, 255, 255]))
    ],
    brightness_threshold=100
)

# ─────────────────────────────────────────────
# State tracking for button ON detection
# ─────────────────────────────────────────────
blue_on = False
red_on = False

def set_blue_on(midpoint):
    global blue_on
    global red_on

    if not blue_on:
        blue_on = midpoint is not None
        if blue_on:
            epson.executeTask(EpsonController.Action.PRESS_BLUE)
    
    if blue_on and red_on: 
        cam.stop_feed()

def set_red_on(midpoint):
    global red_on
    if not red_on:
        red_on = midpoint is not None
        if red_on:
            epson.executeTask(EpsonController.Action.PRESS_RED)

    if blue_on and red_on: 
        cam.stop_feed()

BlueOnDetector = ColorDetector("BlueOnDetector", filters=[BLUE_FILTER_ON], callback=set_blue_on)
RedOnDetector = ColorDetector("RedOnDetector", filters=[RED_FILTER_ON], callback=set_red_on)

# ─────────────────────────────────────────────
# Async Main Logic
# ─────────────────────────────────────────────
async def main():
    cam.take_picture(filename="./local-frame.png")

    print("Detecting red and blue buttons...")
    detector.set_filters([ColorDetector.RED_FILTER_OFF, ColorDetector.BLUE_FILTER_OFF])
    image = cv2.imread("./local-frame.png")
    _, points = detector.detect_main_color_midpoints(image)

    cam_point_blue = points.get("blue")
    cam_point_red = points.get("red")

    print(f"Found buttons: blue={cam_point_blue}, red={cam_point_red}")

    blue_point = epson.getWorldCoordinates(cam_point_blue)
    red_point = epson.getWorldCoordinates(cam_point_red)


    epson.setLocalFrame(blue_point, red_point)

    success = await epson.executeTask(EpsonController.Action.PRESS_RED_BLUE_RED)
    
    if not success:
        print("Failed to execute action.")
        return 
    
    cam.live_feed(detectors=[BlueOnDetector, RedOnDetector])

    print("Continue")

    

    
    



# ─────────────────────────────────────────────
# Run it
# ─────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
