import cv2
import numpy as np
import asyncio
from modules.Camera import Cam
from modules.EpsonController import EpsonController
from modules.ColorDetectorClass import ColorDetector, ColorFilter

import tracemalloc
tracemalloc.start()

# ─────────────────────────────────────────────
# Initialization
# ─────────────────────────────────────────────
cam = Cam(0)
epson = EpsonController()
detector = ColorDetector("ColorPerception")

# ─────────────────────────────────────────────
# Color filters
# ─────────────────────────────────────────────
BLUE_FILTER_ON = ColorFilter(
    "blue",
    [(np.array([100, 150, 0]), np.array([140, 255, 255]))],
    brightness_threshold=120
)

RED_FILTER_ON = ColorFilter(
    "red",
    [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([160, 100, 100]), np.array([180, 255, 255]))
    ],
    brightness_threshold=80
)

# ─────────────────────────────────────────────
# State tracking
# ─────────────────────────────────────────────
blue_on = False
red_on = False

async def set_blue_on(midpoint):
    global blue_on
    if not blue_on and midpoint is not None:
        blue_on = True
        print("Blue On", midpoint)
        await epson.executeTask(EpsonController.Action.PRESS_BLUE)
        cam.stop_feed()

async def set_red_on(midpoint):
    global red_on
    if not red_on and midpoint is not None:
        red_on = True
        print("Red On", midpoint)
        await epson.executeTask(EpsonController.Action.PRESS_RED)
        cam.stop_feed()

BlueOnDetector = ColorDetector("BlueOnDetector", filters=[BLUE_FILTER_ON], callback=set_blue_on)
RedOnDetector = ColorDetector("RedOnDetector", filters=[RED_FILTER_ON], callback=set_red_on)

# ─────────────────────────────────────────────
# Async Main Logic
# ─────────────────────────────────────────────
async def main():
    cam.take_picture(filename="./local-frame.png")

    print("Detecting red and blue buttons...")
    detector.set_filters([ColorDetector.RED_FILTER, ColorDetector.BLUE_FILTER])
    image = cv2.imread("./local-frame.png")
    _, points = detector.detect_main_color_midpoints(image)

    print(points)
    cam_point_blue = points.get("blue")
    cam_point_red = points.get("red")

    print(f"Found buttons: blue={cam_point_blue}, red={cam_point_red}")

    blue_point = epson.getWorldCoordinates(cam_point_blue)
    red_point = epson.getWorldCoordinates(cam_point_red)

    epson.setLocalFrame(blue_point, red_point)

    success = await epson.executeTask(EpsonController.Action.PRESS_RED_BLUE_RED)
    await asyncio.sleep(3)

    if not success:
        print("Failed to execute action.")
        return

    await cam.live_feed(detectors=[BlueOnDetector, RedOnDetector])

    print("Continue")

    # Additional Epson async task sequence
    await epson.executeTask(EpsonController.Action.PEN_PICK)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.SCREEN_CAMERA)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.DRAW_SQUARE)
    await asyncio.sleep(1)
    
    await epson.executeTask(EpsonController.Action.DRAW_CIRCLE)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.DRAW_TRIANGLE)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.SWIPE_BA)
    await asyncio.sleep(1)
    
    await epson.executeTask(EpsonController.Action.TAP_B)
    await asyncio.sleep(1)

    
    await epson.executeTask(EpsonController.Action.SWIPE_BG)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.BALL_MAZE_1)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.BALL_MAZE_2)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.PEN_PLACE)

# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
