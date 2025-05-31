from modules.Calibrator import Calibrator

import pathlib
# calibrator = Calibrator(calibrate=False)
calibrator = Calibrator()
# x compensation = 2.47mm
# y compensation = 12.88mm

# x compensation = 2.2mm
# y compensation = 8.65mm

# x compensation = 1.09mm
# y compensation = 5.66mm


# x compensation = 1.92mm
# y componsation = 9.06mm

def get_world_points(camera_points):
    for point in camera_points:
        print(f"camera point:{point}", f"world point {calibrator.predict({'x': point["x"], 'y': point["y"]})}")

        
# {"x": 398, "y": 292},
#                   {"x": 1405, "y": 279},
#                   {"x": 402, "y": 974},
#                   {"x": 1421, "y": 947}

get_world_points([ {"x": 591, "y": 491}, {"x": 629, "y": 810} ])  
# print(f"cam ",  calibrator.predict({'x':402, 'y': 974}))
# path = pathlib.Path("./pic1.png")



# camera_csv_file = "./saved_camera_points.csv"
# # robot_csv_file = pathlib.Path("./modules/calibration/robot_points.csv")


# calibrator.detect_circles(path)
# calibrator.generate_robot_points(x=-150, y=550, spacing=50)
# camera_points = calibrator.read_csv(camera_csv_file)
# calibrator.sort_points(camera_points, "./modules/calibration/1fixed_camera_points.csv")

# from modules.Camera import Cam

# cam = Cam(0)
# cam.point()



