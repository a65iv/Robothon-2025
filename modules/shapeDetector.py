import cv2
import numpy as np

def detect_shape(image_path):
    image = cv2.imread(image_path)

    # Crop display area
    h, w = image.shape[:2]
    cropped = image[int(h * 0.2):int(h * 0.85), int(w * 0.15):int(w * 0.85)]

    # Convert to HSV
    hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

    # Red mask
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    # Morphological filtering and blur
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    # Contour detection
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_cnt = max(contours, key=cv2.contourArea, default=None)

    if best_cnt is not None:
        area = cv2.contourArea(best_cnt)
        peri = cv2.arcLength(best_cnt, True)
        circularity = 4 * np.pi * area / (peri * peri) if peri > 0 else 0
        approx = cv2.approxPolyDP(best_cnt, 0.015 * peri, True)
        vertices = len(approx)

        # Shape logic
        if circularity > 0.85 and vertices >= 6:
            shape_name = "circle"
        elif vertices == 3:
            shape_name = "triangle"
        elif vertices == 4:
            x, y, w, h = cv2.boundingRect(approx)
            ar = w / float(h)
            shape_name = "square"
        else:
            shape_name = "circle" 

    return shape_name.lower()