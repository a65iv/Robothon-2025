import cv2
import asyncio
from config import *
from modules.Camera import Cam
from modules.TextDetector import TextDetector
from modules.ShapeDetector import ShapeDetector
from modules.EpsonController import EpsonController
from modules.ShapeTextDetector import ShapeTextDetector
from modules.ColorDetector import ColorDetector

import tracemalloc
tracemalloc.start()

blue_on = False
red_on = False

cam = Cam(0)
lcd_cam = Cam(2)
epson = EpsonController()

async def set_blue_on(midpoint):
    global blue_on
    if not blue_on and midpoint is not None:
        blue_on = True
        await epson.executeTask(EpsonController.Action.PRESS_BLUE)
        cam.stop_feed()

async def set_red_on(midpoint):
    global red_on
    if not red_on and midpoint is not None:
        red_on = True
        await epson.executeTask(EpsonController.Action.PRESS_RED)
        cam.stop_feed()

textDetector = TextDetector("TextDetector")
colorDetector = ColorDetector("ColorDetector")
shapeDetector = ShapeDetector("ShapeDetector")

BlueOnDetector = ColorDetector("BlueOnDetector", filters=[BLUE_FILTER_ON], callback=set_blue_on)
RedOnDetector = ColorDetector("RedOnDetector", filters=[RED_FILTER_ON], callback=set_red_on)


async def read_instruction(led_instruction):
    if led_instruction == "circle":
        print("Detected shape: Circle")
        await epson.executeTask(EpsonController.Action.DRAW_CIRCLE)

    elif led_instruction == "triangle":
        print("Detected shape: Triangle")
        await epson.executeTask(EpsonController.Action.DRAW_TRIANGLE)

    elif led_instruction == "square":
        print("Detected shape: Square")
        await epson.executeTask(EpsonController.Action.DRAW_SQUARE)

    elif led_instruction == "drag from a to background":
        await epson.executeTask(EpsonController.Action.SWIPE_AG)

    elif led_instruction == "drag from b to background":
        await epson.executeTask(EpsonController.Action.SWIPE_BG)

    elif led_instruction == "drag from brackground to a":
        await epson.executeTask(EpsonController.Action.SWIPE_GA)

    elif led_instruction == "drag from brackground to b":
        await epson.executeTask(EpsonController.Action.SWIPE_GB)

    elif led_instruction == "drag from a to b":
        await epson.executeTask(EpsonController.Action.SWIPE_AB)

    elif led_instruction == "drag from b to a":
        await epson.executeTask(EpsonController.Action.SWIPE_BA)

    elif led_instruction == "tap a":
        await epson.executeTask(EpsonController.Action.TAP_A)

    elif led_instruction == "tap b":
        await epson.executeTask(EpsonController.Action.TAP_B)

    elif led_instruction == "double tap a":
        await epson.executeTask(EpsonController.Action.DTAP_A)

    elif led_instruction == "double tap b":
        await epson.executeTask(EpsonController.Action.DTAP_B)

    elif led_instruction == "double tap background":
        await epson.executeTask(EpsonController.Action.DTAP_G)

    elif led_instruction == "swipe right":
        await epson.executeTask(EpsonController.Action.SWIPE_AB)

    else:
        print("Unknown shape detected")
        await epson.executeTask(EpsonController.Action.TAP_G)


async def main():
    cam.take_picture(filename="./local-frame.png")

    print("Detecting red and blue buttons...")
    colorDetector.set_filters([ColorDetector.RED_FILTER, ColorDetector.BLUE_FILTER])
    image = cv2.imread("./local-frame.png")
    _, points = colorDetector.detect_main_color_midpoints(image)

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


    # Additional Epson async task sequence
    await epson.executeTask(EpsonController.Action.PEN_PICK)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.SCREEN_CAMERA)
    await asyncio.sleep(1)

    detections = []
    for i in range(6):
        print("Epson Action: ", epson.isPerformingAction)
        print(f"TAKE PICTURE {i}: ShapeTextDetection")
        filename = f"./output/shape{i}.png"
        lcd_cam.take_picture(filename=filename)

        image_binary = cv2.imread(filename)

        if i < 3:
            detection = await shapeDetector.detect(image_binary)
        else:
            detection = await textDetector.detect(image_binary)
                
        detections.append(detection.name)
        await read_instruction(detection.name)
        
    print("Detections:\n", detections)

    await epson.executeTask(EpsonController.Action.BALL_MAZE_1)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.BALL_MAZE_2)
    await asyncio.sleep(1)

    await epson.executeTask(EpsonController.Action.PEN_PLACE)


if __name__ == "__main__":
    asyncio.run(main())
