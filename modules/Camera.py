import cv2
import csv
import math
import argparse
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

class Cam:

    def __init__(self, index = None):
        self.count = 0
        self.points = []
        # Initialize the camera (you may need to adjust the camera index)
        if index != None:
            print(type(index))
            self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            if not self.cap.isOpened():
                raise Exception("Error: Unable to open the camera.")

            # Initialize variables to store selected point
            self.selected_point = None

    def take_picture(self, duration = 10, filename = "pic.png"):
        image = None
        count_duration = 0
        self.cap.open(0)

        while(count_duration < duration and image == None):
            open, frame = self.cap.read()
            if open: 
                count_duration+=1
                if count_duration > duration / 2:
                    print("TAKING PICTURE")
                    image = cv2.imwrite(filename, frame)
                    print("PICTURE TAKEN")
                    return filename
            else: 
                # self.release()
                return False

    def live_feed(self):
        # Show a live feed from the camera
        while True:
            open, frame = self.cap.read()
            if not open:
                print("Error: Unable to open the camera.")
                break

            cv2.imshow("Live Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the camera when done
        self.cap.release()
        cv2.destroyAllWindows()
    
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def point(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.count += 1
            font = cv2.FONT_HERSHEY_SIMPLEX
            color = (255, 0, 0)  # white color in BGR format

            # Get the size of the text
            text_size, _ = cv2.getTextSize(f"{x}{y}", font, 1, 2)
            copy = param["image"]

            # Draw a circle around the point on the image copy
            cv2.circle(copy, (x, y), 10, (255, 0, 0), 2)
            # Put the text on the image
            cv2.putText(
                copy, f"{math.ceil(x)}, {math.ceil(y)}", (x, y - 10), font, 0.5, color, 2)

            # Save the point
            if param["train"]:
                point_name = input("Enter the name of the point: ")
                self.points.append([point_name, x, y])
            self.points.append(["", x, y])
            print("save point")

            # Display the image with circles
            cv2.imshow('point', copy)


    
    def get_count(self):
        return self.count
    
    def get_points(self):
        return self.points
    
    def dump_points(self, filename = "output/saved_camera_points.csv"):
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['name', 'x', 'y'])
            csv_writer.writerows(self.points)
            print("Coordinates saved to camera_points.csv")
        return filename, self.points
       



def main():
    parser = argparse.ArgumentParser(description="Perform Camera Operations like picture taking or live feed")
    parser.add_argument("--take_picture", action="store_true", help="Take a picture from the camera")
    parser.add_argument("--live_feed", action="store_true", help="Show a live feed from the camera")
    parser.add_argument("--point", type=str, help="Index of the camera to use")


    args = parser.parse_args()

    if args.take_picture:
        cam = Cam(0)
        cam.take_picture()
    elif args.live_feed:
        cam = Cam(0)
        cam.live_feed()
    elif args.point:
        cam = Cam()
        img = cv2.imread(args.point)
        cv2.imshow("point", img)
        cv2.setMouseCallback('point', cam.point, {"image": img, "train": False})
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cam.dump_points()


if __name__ == "__main__":
    main()


# Path: Modules/Calibrator.py
# Example usage:
# python ./modules/Camera.py --take_picture
# python ./modules/Camera.py --live_feed