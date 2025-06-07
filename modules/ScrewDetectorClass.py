import cv2
import numpy as np
from modules.PointClass   import Point
from modules.DetectorClass import Detector, DetectionResult


class ScrewHoleDetector(Detector):
    def __init__(self, name, callback):
        self.name = name
        self.callback = callback

    async def detect(self, frame) -> DetectionResult:
        holes_xy = self._detect_screw_holes(frame)   # list[(x,y)]
        points   = [Point(x, y) for (x, y) in holes_xy]
        if self.callback and points:
            await self.callback(points)
        return DetectionResult(self.name, points if points else None)

    def _detect_screw_holes(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 2)

        circles = cv2.HoughCircles(
            blur, cv2.HOUGH_GRADIENT,
            dp=1, minDist=50, param1=50, param2=20,
            minRadius=10, maxRadius=20
        )

        holes = []

        if circles is not None:
            circles = np.round(circles[0, :]).astype(int)
            scored  = []
            for (x, y, r) in circles:
                mask = np.zeros(gray.shape, np.uint8)
                cv2.circle(mask, (x, y), r, 255, -1)
                darkness = cv2.mean(gray, mask)[0]   # lower = darker
                scored.append((darkness, (x, y)))

            scored.sort(key=lambda t: t[0])          # darkest first
            holes = [pt for _, pt in scored[:4]]

        if len(holes) < 4:                           # fallback
            holes = self._holes_by_contours(image)

        return holes

    def _holes_by_contours(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        at   = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        k     = np.ones((3, 3), np.uint8)
        clean = cv2.morphologyEx(at, cv2.MORPH_CLOSE, k)
        clean = cv2.morphologyEx(clean, cv2.MORPH_OPEN,  k)

        cnts, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

        cand = []
        for c in cnts:
            area = cv2.contourArea(c)
            if not (50 < area < 1000):
                continue
            peri = cv2.arcLength(c, True)
            circ = 4 * np.pi * area / (peri * peri + 1e-5)
            if circ < 0.6:
                continue
            M = cv2.moments(c)
            if M["m00"] == 0:
                continue
            cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
            h, w   = image.shape[:2]
            if 20 < cx < w-20 and 20 < cy < h-20:
                cand.append((area * circ, (cx, cy)))   # rank key

        cand.sort(reverse=True)                       # best first
        return [pt for _, pt in cand[:4]]


if __name__ == "__main__":
    img = cv2.imread("resources/messages/square2.jpg")
    detector = ScrewHoleDetector()
    res = detector.detect(img)
    print(res)
    if res.midpoint:
        for idx, p in enumerate(res.midpoint, 1):
            print(f"Hole {idx}: ({p.x}, {p.y})")
