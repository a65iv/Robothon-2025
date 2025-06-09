import asyncio
from modules.Camera import Cam
from modules.ShapeTextDetector import ShapeTextDetector


async def main():
    async def detectionCallback(text):
        print(text)
        return
        
        
    lcd_cam = Cam(2)
    shapetextdetector = ShapeTextDetector(callback=detectionCallback)
    await lcd_cam.live_feed(detectors=[shapetextdetector])
    

asyncio.run(main())