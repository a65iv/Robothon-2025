import cv2
import numpy as np

# This class is resposinble for providing all data needed from the detected objects


class DetectedObjects():
    areaThresh = 1600

    distanceThresh = 500

    orientation = 0

    def __init__(self, img) -> None:
        self.img = img
        self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_norm = cv2.normalize(
            self.gray, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        gray_norm2 = cv2.normalize(
            gray_norm, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        self.blur = cv2.GaussianBlur(gray_norm2, (1, 1), cv2.BORDER_DEFAULT)
        self.filter = cv2.bilateralFilter(self.blur, 10, 55, 55)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        erosion = cv2.erode(self.filter, kernel, iterations=7)
        dilation = cv2.dilate(erosion, kernel, iterations=7)
        self.edges = cv2.Canny(dilation, 50, 150)
        # Create a Mask with adaptive threshold
        mask = cv2.adaptiveThreshold(
            dilation, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)
        self.contours = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.centers = []
        self.objects = self.getPickableObjects()
        
        

    def getPickableObjects(self):
        contours, _= self.contours
        objects = []
        index = 0
        px_cm = 1
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > self.areaThresh:
                index += 1
                M = cv2.moments(cnt)
                # Check if the zeroth moment is not zero to prevent division be zero rule
                if M["m00"] != 0:
                    # Get the center x and center y of the objects in the contours
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                x, y, w, h = cv2.boundingRect(cnt)
                _, _, angle = cv2.minAreaRect(cnt)
                cv2.putText(self.img, str(int(w / px_cm)), (cx, cy),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 175, 255), 2)
                cv2.putText(self.img, str(int(h / px_cm)), (cx, cy + 20),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 175, 255), 2)
                if angle < 0:
                    angle = 90 + angle
                objects.append(PickableObjects(
                    (cx, cy), (int(w / px_cm), int(h / px_cm)), angle, (x, y)))
        return objects

    def getCenterPoints(self):
        contours, _ = self.contours
        # Draw the contours on the image
        cv2.drawContours(self.img, contours, -1, (0, 255, 0), 2)
        for cnt in contours:
            # epsilon = 0.05 * cv2.arcLength(cnt, True)
            # approx = cv2.approxPolyDP(cnt, epsilon, True)
            # Draw the contours on the image
            area = cv2.contourArea(cnt)
            if area > self.areaThresh:
                cv2.drawContours(self.img, cnt, -1, (0, 255, 0), 2)
                # calculate moment in contours
                M = cv2.moments(cnt)
                # Check if the zeroth moment is not zero to prevent division be zero rule
                if M["m00"] != 0:
                    # Get the center x and center y of the objects in the contours
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    self.centers.append([cx, cy])
                    cv2.putText(self.img, "0", (cx, cy),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                print("Centers: ", [cx, cy])
        self.centers = np.array(self.centers)
        cv2.imshow("Grey", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return self.centers

    def getBoundingBox(self):
        contours, _ = self.contours  # Access the contours from the state

        for cnt in contours:
            area = cv2.contourArea(cnt)  # calculate the contour areas
            if area > self.areaThresh:  # check if the contour area exceeds the required threshold
                # get the bounding box coordinates for the contours
                x, y, w, h = cv2.boundingRect(cnt)
                _, _, angle = cv2.minAreaRect(cnt)
                self.orientation = area
                # Draw the bounding box for each contour
                cv2.rectangle(self.img, (x, y), (x+w, y+h), (0, 255, 0), 4)
                cv2.putText(self.img, str((x, y)), (x, y),
                            cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 255), 2)
                cv2.putText(self.img, str((x+w, y+h)), (x+w, y+h), cv2.FONT_HERSHEY_COMPLEX,
                            0.8, (0, 0, 255), 2)
        cv2.imshow("Grey", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return [x, y, w, h]


    def sortByCameraProximity(self, pickable_objects, camera_point):
        # this function takes in a list of pickable_objects and sorts them based on the distance of the center of the object from the camera
        # the camera point is the home position of the camera in pixel coordinates i.e epson home position

        # GET PIXEL COORDINATE OF THE CAMERA POINT
        x, y = camera_point

        # SORT THE LIST BASED ON THE DISTANCE FROM THE CAMERA POINT
        for _object in pickable_objects:
            x1, y1 = _object.center_point
            distance = np.sqrt((x1 - x)**2 + (y1 - y)**2)
            _object.distance = distance

        # SORT THE LIST BASED ON THE DISTANCE
        pickable_objects.sort(key=lambda x: x.distance)
        return pickable_objects


    # SHOULD BE RENAMED TO getObjectsInFrame
    def sortDetectedObjects(self, list_to_sort, camera_point):
        # sorted(list_to_sort, key=lambda x: x.getPickScore((0, 450)))
        sorted_list = list_to_sort
        accepted_list = []
        print(len(sorted_list))
        for item in sorted_list:
             if (item.center_point[0] > 60 and item.center_point[0] < 1483) and (item.center_point[1] > 59 and item.center_point[1] < 989):
                 accepted_list.append(item)
        print(f"items detected: {len(accepted_list)}")


        return accepted_list
        # return  self.sortByCameraProximity(accepted_list, camera_point)
        # return sorted_list


class PickableObjects():
    def __init__(self, center_point, dimensions, orientation, boundaries) -> None:
        self.center_point = center_point
        self.dimensions = dimensions
        self.orientation = orientation
        self.boundaries = boundaries
        self.distance = 200

        self.x = boundaries[0]
        self.y = boundaries[1]
        self.w = dimensions[0]
        self.h = dimensions[1]

    def __str__(self) -> str:
        return f"Center: {self.center_point}, Dimensions: {self.dimensions}, Orientation: {self.orientation}, Boundaries: {self.boundaries}"






if __name__ == "__main__":
    img_detect = cv2.imread("pic.png")

    detector = DetectedObjects(img_detect)


    detector.getPickableObjects()
    detector.getBoundingBox()