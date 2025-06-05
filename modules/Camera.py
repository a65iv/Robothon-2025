import cv2
import csv
import math
import platform


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

    def live_feed(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Unable to read from the camera.")
                break

            cv2.imshow("Live Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.release()

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
