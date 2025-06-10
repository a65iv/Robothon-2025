import cv2
import numpy as np
import asyncio
from modules.Camera import Cam
from modules.EpsonController import EpsonController
from modules.ColorDetectorClass import ColorDetector, ColorFilter
from modules.ShapeTextDetector import ShapeTextDetector

import tracemalloc
tracemalloc.start()

# ─────────────────────────────────────────────
# Initialization
# ─────────────────────────────────────────────
cam = Cam(0)
lcd_cam = Cam(2)
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
count = 0

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

async def read_instruction(led_instruction): 
    if epson.isPerformingAction:
        return
    
    global count
    if count >= 6:
        lcd_cam.stop_feed()
        return
    
    
    print(led_instruction)
    match led_instruction:
        case "circle":
            print("Detected shape: Circle")
            await epson.executeTask(EpsonController.Action.DRAW_CIRCLE)
        case "triangle":
            print("Detected shape: Triangle")
            await epson.executeTask(EpsonController.Action.DRAW_TRIANGLE)
        case "square":
            print("Detected shape: Square")
            await epson.executeTask(EpsonController.Action.DRAW_SQUARE)
        case "drag from b to background":
            await epson.executeTask(EpsonController.Action.SWIPE_BG)
        case "drag from a to background":
            await epson.executeTask(EpsonController.Action.SWIPE_AG)
        case "drag from brackground to a":
            await epson.executeTask(EpsonController.Action.SWIPE_GA)
        case "tap b":
            await epson.executeTask(EpsonController.Action.TAP_B)
        case "drag from b to a":
            await epson.executeTask(EpsonController.Action.SWIPE_BA)
        case "double tap a":
            await epson.executeTask(EpsonController.Action.DTAP_A)
        case _:
            print("Unknown shape detected")
            await epson.executeTask(EpsonController.Action.TAP_G)
    
    asyncio.sleep(1)
    count += 1

async def setLocal():
    cam.take_picture(filename="./local-frame.png")
    print("Detecting red and blue buttons...")
    detector.set_filters([ColorDetector.RED_FILTER, ColorDetector.BLUE_FILTER])
    image = cv2.imread("./local-frame.png")
    *, points = detector.detect_main_color_midpoints(image)
    print(points)
    cam_point_blue = points.get("blue")
    cam_point_red = points.get("red")
    print(f"Found buttons: blue={cam_point_blue}, red={cam_point_red}")
    if cam_point_blue:
        blue_point = epson.getWorldCoordinates(cam_point_blue)
    if cam_point_red: 
        red_point = epson.getWorldCoordinates(cam_point_red)
    epson.setLocalFrame(blue_point, red_point)
    
BlueOnDetector = ColorDetector("BlueOnDetector", filters=[BLUE_FILTER_ON], callback=set_blue_on)
RedOnDetector = ColorDetector("RedOnDetector", filters=[RED_FILTER_ON], callback=set_red_on)


async def doRBR():
    success = await epson.executeTask(EpsonController.Action.DO_PRESSRBR)
    await asyncio.sleep(3)
    if not success:
        print("Failed to execute action.")
        return
    await cam.live_feed(detectors=[BlueOnDetector, RedOnDetector])
    print("Continue")


# ─────────────────────────────────────────────
# Async Main Logic
# ─────────────────────────────────────────────
async def main():
    success = await setLocal()
    await asyncio.sleep(3)

    #--- we should remove below lines after implementing the Task Sequence Manager GUI ---
    await doRBR()
    await asyncio.sleep(3)

    await do_drawScreen()  # this is the screen recognition / drawing /tapping routine
    await asyncio.sleep(3)

    await epson.executeTask(EpsonController.Action.PEN_PICK)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.BALL_MAZE_1)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.BALL_MAZE_2)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.PEN_PLACE)
    #--- end of lines to be replaced by the Task Sequence Manager GUI ---

# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
