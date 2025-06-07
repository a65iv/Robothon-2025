from PointClass import Point

class DetectionResult:
    def __init__(self, name: str, midpoint: Point, callback):
        self.name = name
        self.midpoint = midpoint

    def __str__(self):
        if (self.midpoint):
            print(f"{self.name}: No detection")
        else:
            print(f"{self.name}: [{self.midpoint.x}, {self.midpoint.y}]")

        

class Detector:
    def __init__(self, name):
        print(f"Initialized {name} Detector")

    def detect(self, imageBinary, callback) -> DetectionResult:
        pass