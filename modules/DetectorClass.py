from modules.PointClass import Point
from typing import Optional

class DetectionResult:
    def __init__(self, name: str, midpoint: Optional[Point]):
        self.name = name
        self.midpoint = midpoint

    def __str__(self):
        if (self.midpoint is None):
            return f"{self.name}: No detection"
        else:
            return f"{self.name}: [{self.midpoint.x}, {self.midpoint.y}]"

        

class Detector:
    def __init__(self, name, **kwargs):
        print(f"Initialized {name} Detector")

    def detect(self, imageBinary) -> DetectionResult:
        pass