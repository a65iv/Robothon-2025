import os
import csv
import cv2
import argparse
import numpy as np  
from sklearn.linear_model import LinearRegression
CAMERA_DATA_PATH = './modules/calibration/fixed_camera_points.csv'
ROBOT_DATA_PATH = './modules/calibration/fixed_robot_points.csv'
class Calibrator(): 
    """
    The Calibrator class is responsible for calibrating the camera mounted to the EPSON Robot.
    """ 

    def __init__(self, camera_data_path = CAMERA_DATA_PATH, robot_data_path = ROBOT_DATA_PATH, calibrate = True) -> None:
        # Load the camera calibration data and the robot's calibration data, if available
        # If not available, the class will use the data in the cache or prompt the user to calibrate the camera and the robot
        print("path exists:", os.path.exists(camera_data_path))
        print(os.listdir("modules"))
        self.camera_points = self.read_csv(camera_data_path)
        self.robot_points = self.read_csv(robot_data_path)

        self.calibration_path = "./modules/calibration"

        self.x_model = LinearRegression()
        self.y_model = LinearRegression()

        self.x_camera_model = LinearRegression()
        self.y_camera_model = LinearRegression()

        if calibrate:
            self.calibrate()
        pass

    def sort_points(self, target, output_file:str, sort_order = None, flip=True):
        if sort_order == None:
            sort_order= (target[:, 1], -target[:, 0]); 

        # sorts the csv based on the highest x and the highest y
        sorted_indices = np.lexsort(sort_order)
        sorted_data = target[sorted_indices]
        if flip:
            sorted_data = sorted_data[::-1]
        np.savetxt(output_file, sorted_data, delimiter=',', header='x,y', fmt='%d', comments='')

    def calibrate(self) -> None:
        """
        Calibrate the camera and the robot and return the prediction models for both axes.
        """
        # calculate the time it takes to calibrate the camera and the robot
        # start_time = time.time()
        # instantiate the linear regression model

        # camera x and robot x calibration 
        camera_x = self.camera_points[:, 0]
        robot_x = self.robot_points[:, 0]

        # camera y and robot y calibration
        camera_y = self.camera_points[:, 1]
        robot_y = self.robot_points[:, 1]

        # reshape the data
        _camera_x = camera_x.reshape(-1, 1)
        _robot_x = robot_x.reshape(-1, 1)
        _camera_y = camera_y.reshape(-1, 1)
        _robot_y = robot_y.reshape(-1, 1)

        # fit the model
        self.x_model.fit(_camera_x, _robot_x)
        self.y_model.fit(_camera_y, _robot_y)

        self.x_camera_model.fit(_robot_x, _camera_x)
        self.y_camera_model.fit(_robot_y, _camera_y)

        # endtime = time.time()
        # print(f"Calibration took {endtime - start_time} seconds")

    def rotate(self, angle: float) -> None:
        """
        Rotate the robot by a given angle.
        """
        radians = np.deg2rad(angle)

        rotation_matrix = np.array([[np.cos(radians), -np.sin(radians)], [np.sin(radians), np.cos(radians)]])
        self.robot_points = np.dot(self.robot_points, rotation_matrix)
        self.calibrate()
        pass


    def translate(self, x: float, y: float) -> None:
        """
        Translate the robot by a given x and y.
        """
        translation_matrix = np.array([[x, y]])
        self.robot_points = self.robot_points + translation_matrix
        self.calibrate()
        pass


        # Generate and save world coordinate points in one go
    def generate_robot_points(self, x: float, y: float, spacing: float) -> None:
        with open( f"{self.calibration_path}/robot_points.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["x", "y"])
            writer.writerows(
                [(x + i * spacing, y + j * spacing) for i in range(5) for j in range(5)]
            )

        target = self.read_csv(f"{self.calibration_path}/robot_points.csv")
        sort_order = (-target[:, 1], target[:, 0]) 
        self.sort_points(target, f"{self.calibration_path}/fixed_robot_points.csv", sort_order, False)


    def predict(self, coordinate, world = True) -> tuple:
        print("printing coordinates", coordinate)
        """
        Predict the robot's coordinates based on the camera's coordinates.
        """
        if world:
            world_x = self.x_model.predict([[coordinate['x']]])[0][0]
            world_y = self.y_model.predict([[coordinate['y']]])[0][0]
            return (world_x, world_y)
        else:
            pixel_x = self.x_camera_model.predict([[coordinate['x']]])[0][0]
            pixel_y = self.y_camera_model.predict([[coordinate['y']]])[0][0]
            return (pixel_x, pixel_y)
    
    def detect_circles(self, image):
        targetImage = cv2.imread(image)
        gray = cv2.cvtColor(targetImage, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Use HoughCircles to detect circles
        circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, 5, param1=100, param2=10, minRadius=0, maxRadius=10)

        # check if circles were found
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            circle_coordinates = []

            for (x, y, r) in circles:
                # draw the circle in the output image
                cv2.circle(targetImage, (x, y), r, (0, 255, 0), 4)

                circle_coordinates.append((x, y))

                cv2.putText(targetImage, f"({x}, {y})", (x-5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

            # write coordinates to CSV file
            with open(f'{self.calibration_path}/camera_points.csv', 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['x', 'y'])

                
                csv_writer.writerows(circle_coordinates)
                print("Coordinates saved to camera_points.csv")
            
            target = self.read_csv(f"{self.calibration_path}/camera_points.csv")
            self.sort_points(target, f"{self.calibration_path}/fixed_camera_points.csv")

            # show the output image
            outputImage = np.hstack([targetImage])
            cv2.imshow("Detected Circles", outputImage)

            key = cv2.waitKey(0)
            if key:
                cv2.imwrite('output/contours.png', outputImage)
                print("Image saved successfully!")
            cv2.destroyAllWindows()
        else:
            print("No circles were found.")
    

    def read_csv(self, path: str):
        """
        Read the camera calibration data from a CSV file.
        """
        try: 
            result = []
            with open(path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    result.append([row["x"], row["y"]])
                    pass
            result = np.array(result)
            return result.astype(np.float32)
        except Exception as e:
            print("Failed to read csv file at:", path, e) 
            return None



def main():
    parser = argparse.ArgumentParser(description="This is the calibrator class it is responsible for every aspect of calibration")
    parser.add_argument("--circles", type=str, help="Uses opencv to draw circles on the image and save the coordinates to a csv file, you need to specify the path to the image")
    # parser.add_argument("--fix_camera", type=str, help="Fixes the camera points by sorting the y values in descending order")
    parser.add_argument("--predict", metavar=("x", "y"), type=float, nargs=2, help="Predict the robot's coordinates based on the camera's coordinates")


    args = parser.parse_args()

    

    # if args.fix_camera:
    #     calibrator = Calibrator(camera_data_path=args.fix_camera, calibrate=False)
    #     calibrator.fix_camera_points()
    if args.circles: 
        calibrator = Calibrator(calibrate=False)
        calibrator.detect_circles(args.circles)
    elif args.predict:
        calibrator = Calibrator()
        print(calibrator.predict({"x": args.predict[0], "y": args.predict[1]}))


if __name__ == "__main__":
    main()


# Path: Modules/Calibrator.py
# Example usage:
# python ./modules/Calibrator.py --circles ./calibration/calibration.png
# python ./modules/Calibrator.py --circles ./calibration/calibration.png --camera_points ./calibration/camera_points.csv