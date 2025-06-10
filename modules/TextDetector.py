import cv2
import numpy as np
import pytesseract
import Levenshtein
from modules.Detector import Detector, DetectionResult

class TextDetector(Detector):
    def __init__(self, name):
        self.name = name
        self.lang = "eng"
        self.instructions = [
            "drag from b to background",
            "drag from b to back",
            "swipe up",
            "swipe left",
            "swipe right",
            "swipe down",
            "drag from background to a",
            "drag from background to b",
            "tap a",
            "tap b",
            "long press b",
            "long press a",
            "drag from a to background",
            "drag from b to background",
            "drag from b to a",
            "drag from a to b",
            "long press background",
            "double tap a",
            "double tap b",
        ]

    async def detect(self, image_binary):
        value = self.get_readable_text(image_binary)
        return DetectionResult(value, midpoint=None)
    
    def preprocess_for_tesseract(self, img: np.ndarray) -> np.ndarray:
        THRESH_BINARY = (100, 255)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, *THRESH_BINARY, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    
    def lvs_distance(self, detected):
        decided_instruction = ""
        MIN_DISTANCE = float('inf')
        for instruction in self.instructions:
            distance = Levenshtein.distance(detected, instruction)
            # print(instruction, distance)
            if distance <= MIN_DISTANCE:
                MIN_DISTANCE = distance
                decided_instruction = instruction

        if decided_instruction == "drag from b to back":
            decided_instruction = "drag from b to background"

        return decided_instruction

    def get_readable_text(self, img) -> str:
        if img is None:
            raise ValueError(f"Unable to load image")

        proc = self.preprocess_for_tesseract(img)
        data = pytesseract.image_to_data(proc, lang=self.lang, output_type=pytesseract.Output.DICT)

        texts = data['text']
        start_idx = next((i for i, t in enumerate(texts) if 'touch' in t.lower() or 'screen' in t.lower()), None)


        if start_idx is not None and len(texts[start_idx + 1:]) > 0:
            # interested_texts = texts[start_idx + 1:]
            result = [t.strip() for t in texts[start_idx + 1:] if t.strip() not in ('|', '_', '')]
            detected = ' '.join(result).lower() 
            return self.lvs_distance(detected)


