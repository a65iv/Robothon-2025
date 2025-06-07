from PointClass import Point

class DetectionResult:
    def __init__(self, name: str, midpoint: Point):
        self.name = name
        self.midpoint = midpoint

    def __str__(self):
        if (self.midpoint is None):
            return f"{self.name}: No detection"
        else:
            return f"{self.name}: [{self.midpoint.x}, {self.midpoint.y}]"

        

class Detector:
    def __init__(self, name, callback: None):
        print(f"Initialized {name} Detector")

    def detect(self, imageBinary) -> DetectionResult:
        pass