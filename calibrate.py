from modules.Calibrator import Calibrator

import pathlib
# calibrator = Calibrator(calibrate=False)
calibrator = Calibrator()


print(calibrator.predict({'x':150, 'y': 88}))
# path = pathlib.Path("./modules/calibration/calibration.png")



# camera_csv_file = pathlib.Path("./modules/calibration/camera_points.csv")
# robot_csv_file = pathlib.Path("./modules/calibration/robot_points.csv")


# calibrator.detect_circles(path)
# calibrator.generate_robot_points(x=-100, y=550, spacing=50)





