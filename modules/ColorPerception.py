import cv2
from Point import Point
import numpy as np
from typing import List, Tuple, Dict, Optional


class ColorFilter:
    def __init__(
        self,
        name: str,
        hsv_ranges: List[Tuple[np.ndarray, np.ndarray]],
        brightness_threshold: Optional[int] = None
    ):
        """
        Args:
            name: Label of the color (e.g., "red").
            hsv_ranges: List of HSV (lower, upper) ranges for masking.
            brightness_threshold: Optional brightness cutoff to detect only bright regions.
        """
        self.name = name
        self.hsv_ranges = hsv_ranges
        self.brightness_threshold = brightness_threshold


class ColorPerception:
    # Public, built-in filters
    RED_FILTER = ColorFilter(
        "red",
        [
            (np.array([0, 100, 100]), np.array([10, 255, 255])),
            (np.array([160, 100, 100]), np.array([180, 255, 255]))
        ],
        brightness_threshold=10  # Only detect bright red (50 is the max)
    )

    BLUE_FILTER = ColorFilter(
        "blue",
        [
            (np.array([100, 150, 0]), np.array([140, 255, 255]))
        ],
        brightness_threshold=10  # Only detect bright blue (50 is the max)
    )

    def __init__(self, filters: Optional[List[ColorFilter]] = None):
        """
        Args:
            filters: Optional list of custom ColorFilter instances.
        """
        self.filters = filters if filters is not None else [self.RED_FILTER, self.BLUE_FILTER]
    
    def set_filters(self, filters: Optional[List[ColorFilter]] = None):
        self.filters = filters if filters is not None else [self.RED_FILTER, self.BLUE_FILTER]

    def detect_main_color_midpoints(self, image_bgr: np.ndarray) -> Tuple[np.ndarray, Dict[str, Optional[Point]]]:
        """
        Detects midpoints of the largest contour for each color in the filter list,
        optionally applying brightness filtering.

        Returns:
            (annotated image, dictionary of color → midpoint or None)
        """
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        annotated = image_bgr.copy()
        results = {}

        for f in self.filters:
            # Create combined mask from HSV ranges
            mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
            for lower, upper in f.hsv_ranges:
                mask |= cv2.inRange(hsv, lower, upper)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            midpoint = self._get_largest_midpoint(contours)

            # Apply brightness threshold at midpoint (if any)
            if midpoint and f.brightness_threshold is not None:
                brightness = gray[midpoint[1], midpoint[0]]
                if brightness < f.brightness_threshold:
                    midpoint = None  # Detected region too dark

            midpoint = Point(midpoint[0], midpoint[1])
            results[f.name] = midpoint 

            # Draw on annotated image
            if midpoint:
                color_bgr = self._label_color(f.name)
                cv2.circle(annotated, (midpoint.x, midpoint.y), 6, color_bgr, -1)
                cv2.putText(annotated, f.name.upper(), (midpoint.x + 5, midpoint.y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_bgr, 2)

        return annotated, results

    def _get_largest_midpoint(self, contours: List[np.ndarray]) -> Optional[Tuple[int, int]]:
        if not contours:
            return None
        largest = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest)
        if M["m00"] == 0:
            return None
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return (cx, cy)

    def _label_color(self, name: str) -> Tuple[int, int, int]:
        return {
            "red": (0, 0, 255),
            "blue": (255, 0, 0)
        }.get(name.lower(), (255, 255, 255))  # default: white

if __name__ == "__main__":
    image = cv2.imread("./output/red_on.png")  # Replace with your actual image
    perception = ColorPerception(filters=[ColorPerception.BLUE_FILTER, ColorPerception.RED_FILTER])

    annotated_image, points = perception.detect_main_color_midpoints(image)

    print("Red midpoint:", points.get("red"))
    print("Blue midpoint:", points.get("blue"))

    cv2.imshow("Detected Points", annotated_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
