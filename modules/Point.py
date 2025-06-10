class Point():
    def __init__(self, x: float, y: float ):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Point: ({self.x}, {self.y})"
