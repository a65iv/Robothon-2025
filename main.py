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
<<<<<<< Updated upstream
    # if epson.isPerformingAction:
    #     return
    
    # global count
    # if count >= 6:
    #     lcd_cam.stop_feed()
    #     return
    
    
    print("From read instruction: ", led_instruction)
=======
    global count
    if count > 6:
        lcd_cam.stop_feed()
        return
    print(led_instruction) 
>>>>>>> Stashed changes
    match led_instruction:
        case "circle":
            print("Detected shape: Circle")
            await epson.executeTask(EpsonController.Action.DRAW_TRIANGLE)
            return 
        case "triangle":
            print("Detected shape: Triangle")
            await epson.executeTask(EpsonController.Action.DRAW_TRIANGLE)
            return 
        case "square":
            print("Detected shape: Square")
            await epson.executeTask(EpsonController.Action.DRAW_SQUARE)
            return 
        case "drag from a to background":
            await epson.executeTask(EpsonController.Action.SWIPE_AG)
            return 
        case "drag from b to background":
            await epson.executeTask(EpsonController.Action.SWIPE_BG)
            return 
        case "drag from brackground to a":
            await epson.executeTask(EpsonController.Action.SWIPE_GA)
            return 
        case "drag from brackground to b":
            await epson.executeTask(EpsonController.Action.SWIPE_GB)
            return 
        case "drag from a to b":
            await epson.executeTask(EpsonController.Action.SWIPE_AB)
            return 
        case "drag from b to a":
            await epson.executeTask(EpsonController.Action.SWIPE_BA)
            return 
        case "tap a":
            await epson.executeTask(EpsonController.Action.TAP_A)
            return 
        case "tap b":
            await epson.executeTask(EpsonController.Action.TAP_B)
            return 
        case "double tap a":
            await epson.executeTask(EpsonController.Action.DTAP_A)
            return 
        case "double tap b":
            await epson.executeTask(EpsonController.Action.DTAP_B)
            return 
        case "double tap background":
            await epson.executeTask(EpsonController.Action.DTAP_G)
            return 
        case "swipe right":
            await epson.executeTask(EpsonController.Action.SWIPE_AB)
            return 
        case _:
            print("Unknown shape detected")
            await epson.executeTask(EpsonController.Action.TAP_G)
            return 

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

    if cam_point_blue:
        blue_point = epson.getWorldCoordinates(cam_point_blue)
    if cam_point_red: 
        red_point = epson.getWorldCoordinates(cam_point_red)

    epson.setLocalFrame(blue_point, red_point)

    success = await epson.executeTask(EpsonController.Action.ARMREADY) # testing new action by Judhi 10-06-25 18:00 
    await asyncio.sleep(1)
    
    success = await epson.executeTask(EpsonController.Action.PRESS_RED_BLUE_RED)
    await asyncio.sleep(1)

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

    shapetextdetector = ShapeTextDetector()
    
    detections = []
    for i in range(6):
        print("Epson Action: ", epson.isPerformingAction)
        print(f"TAKE PICTURE {i}: ShapeTextDetection")
        filename = f"./shape{i}.png"
        lcd_cam.take_picture(filename=filename)
        
        detection = await shapetextdetector.detect(cv2.imread(filename))
        detections.append(detection.name)
        await read_instruction(detection.name)
        
    # await lcd_cam.live_feed(detectors=[shapetextdetector])


    print("Detections:\n", detections)
# instructions = [
#     # "drag from b to background",
#     # "drag from b to back",
#     "swipe up",
#     # "drag from background to a",
#     # "tap b",
#     "long press b",
#     # "drag from a to background",
#     # "drag from b to a",
#     "long press background",
#     # "double tap a",
#     # "circle",
#     # "rectangle",
#     # "triangle"
# ]


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
