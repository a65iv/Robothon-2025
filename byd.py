import asyncio
from modules.Camera import Cam
from modules.EpsonController import EpsonController
from modules.ScrewDetectorClass import ScrewHoleDetector


import tracemalloc
tracemalloc.start()


cam = Cam(0)
epson = EpsonController()



picked_screws = []

async def pick_screw(midpoint):
    global picked_screws
    if isinstance(midpoint, list) and len(midpoint) > len(picked_screws):
        target = midpoint[len(picked_screws)]
        if (target not in picked_screws):
            world_point = epson.getWorldCoordinates(target)
            await epson.goto(world_point.x, world_point.y, 500)
            await epson.goto(world_point.x, world_point.y, 800)
            await asyncio.sleep(5) 
            picked_screws.append(target)


screwHoleDetector = ScrewHoleDetector("ScrewHoleDetector", callback=pick_screw)

async def main():
    cam.take_picture(filename="./local-frame.png")
    
    await epson.goto(0, 750, 500)
    await cam.live_feed(detectors=[screwHoleDetector])

if __name__ == "__main__":
    asyncio.run(main())
