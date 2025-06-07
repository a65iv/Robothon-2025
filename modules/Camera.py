import cv2
import csv
import math
import platform
import numpy as np
import argparse
from modules.DetectorClass import DetectionResult, Detector
from modules.ColorDetectorClass import ColorDetector, ColorFilter


class Cam:
    def __init__(self, index=0):
        self.count = 0
        self.points = []
        self.selected_point = None

        if index != None:
            print(f"Initialize camera at index {index}")

            os_name = platform.system()
            if os_name == "Windows":
                self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

                self.cap.set(cv2.CAP_PROP_FPS, 30)
                # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
            elif os_name == "Linux":
                self.cap = cv2.VideoCapture(index)  # Default backend is usually fine
            elif os_name == "Darwin":  # macOS
                self.cap = cv2.VideoCapture(index)

        if not self.cap.isOpened():
            raise Exception("Error: Unable to open the camera.")

    def take_picture(self, duration=10, filename="pic1.png"):
        count_duration = 0
        image_captured = False

        while count_duration < duration and not image_captured:
            ret, frame = self.cap.read()
            if ret:
                count_duration += 1
                if count_duration > duration / 2:
                    print("TAKING PICTURE")
                    success = cv2.imwrite(filename, frame)
                    if success:
                        print("PICTURE TAKEN")
                        image_captured = True
                        return filename
                    else:
                        print("Failed to save the picture.")
                        return False
            else:
                print("Failed to read frame from camera.")
                return False
        return False
    
    def put_text(self, frame, text, left = 10, top = 30):
        font_scale = 0.5
        thickness = 1
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Get text size
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)

        # Draw filled rectangle as background
        cv2.rectangle(frame,
                    (left - 5, top - text_height - 5),
                    (left + text_width + 5, top + 5),
                    (0, 0, 0),  # Black background
                    thickness=cv2.FILLED)

        # Draw text on top
        cv2.putText(frame,
                    text,
                    org=(left, top),
                    fontFace=font,
                    fontScale=font_scale,
                    color=(0, 255, 0),  # Green
                    thickness=thickness,
                    lineType=cv2.LINE_AA)


    def live_feed(self, detectors: list[Detector] = []):
        self.running = True
        while True:
            ret, frame = self.cap.read()

            if detectors and len(detectors) != 0:
                # we pass the detectors to detect things on each frame
                for index, detector in enumerate(detectors):
                    # detectors should return an object called a detection value
                    # (true, midpoint, x,y,w,h) detectorName
                    # detectors should as have a string value such that it prints out the output of the detections  
                    detection = detector.detect(frame)
                    
                    
                    self.put_text(frame, str(detection), top= 20 + index * 25)

            if not ret:
                print("Error: Unable to read from the camera.")
                break
            
            
            cv2.imshow("Live Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.release()
    
    def stop_feed(self):
        self.running = False

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()

    def point(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.count += 1
            font = cv2.FONT_HERSHEY_SIMPLEX
            color = (255, 0, 0)  # Blue color in BGR

            copy = param["image"].copy()
            cv2.circle(copy, (x, y), 10, color, 2)
            cv2.putText(copy, f"{math.ceil(x)}, {math.ceil(y)}", (x, y - 10), font, 0.5, color, 2)

            point_name = ""
            if param.get("train", False):
                point_name = input("Enter the name of the point: ")

            self.points.append([point_name, x, y])
            print("Point saved.")

            cv2.imshow('Point Selection', copy)

    def get_count(self):
        return self.count

    def get_points(self):
        return self.points

    def dump_points(self, filename="saved_camera_points.csv"):
        with open(filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Name', 'x', 'y'])
            csv_writer.writerows(self.points)
            print(f"Coordinates saved to {filename}")
        return filename, self.points

def main():
    parser = argparse.ArgumentParser(description="Perform Camera Operations like picture taking or live feed")
    parser.add_argument("--take_picture", type=int, nargs='?', const=0, help="Take a picture from the camera")
    parser.add_argument("--live_feed", action="store_true", help="Show a live feed from the camera")
    parser.add_argument("--live_feed_detect", action="store_true", help="Show a live feed from the camera")
    parser.add_argument("--point", type=str, help="Pick points on an image and get the pixel coordinates")


    args = parser.parse_args()

    if args.take_picture is not None:
        cam = Cam(args.take_picture)
        cam.take_picture()
    elif args.live_feed:
        cam = Cam(0)
        cam.live_feed()
    elif args.live_feed_detect:
        cam = Cam(0)

        
        BLUE_FILTER_ON = ColorFilter("blue", [
            (np.array([100, 150, 0]), np.array([140, 255, 255]))
        ],
            brightness_threshold=150  
        )

        RED_FILTER_ON = ColorFilter("red",[
            (np.array([0, 100, 100]), np.array([10, 255, 255])),
            (np.array([160, 100, 100]), np.array([180, 255, 255]))
        ],
            brightness_threshold=100  # Only detect bright red (50 is the max)
        )

        # detectors 
        RedDetector = ColorDetector("RedDetector", filters=[ColorDetector.RED_FILTER]) 
        BlueDetector = ColorDetector("BlueDetector", filters=[ColorDetector.BLUE_FILTER]) 
        RedOnDetector = ColorDetector("RedOnDetector", filters=[RED_FILTER_ON]) 
        BlueOnDetector = ColorDetector("BlueOnDetector", filters=[BLUE_FILTER_ON]) 
 
        cam.live_feed(detectors=[RedDetector, BlueDetector, RedOnDetector, BlueOnDetector])

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