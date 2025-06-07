import math
import re
import time

import cv2
import easyocr
import numpy as np
import pytesseract
import requests
import Levenshtein
from PIL import Image
from enum import Enum
from modules.RecognizeText import detect_shape

from modules.DetectorClass import Detector, DetectionResult

class OCRDetector(Enum):
    TESERACT = "teseract"
    EASYOCR = "easyocr"

instructions = [
    "drag from b to background",
    "drag from b to back",
    "swipe up",
    "drag from background to a",
    "tap b",
    "long press b",
    "drag from a to background",
    "drag from b to a",
    "long press background",
    "double tap a",
    "circle",
    "rectangle",
    "triangle"
]

# ─── Constants ────────────────────────────────────────────────────────────────
CROP_REGION = (1200, 550, 2000, 1500)
GAUSSIAN_BLUR = (7, 7)
ORANGE_LOWER = np.array([10, 100, 100], dtype=np.uint8)
ORANGE_UPPER = np.array([25, 255, 255], dtype=np.uint8)
THRESH_BINARY = (100, 255)


# ─── Utility Functions ───────────────────────────────────────────────────────
def reduce_image_size(in_path: str, out_path: str, quality: int = 85) -> None:
    """Compress image using Pillow."""
    try:
        img = Image.open(in_path)
        img.save(out_path, optimize=True, quality=quality)
    except FileNotFoundError:
        print(f"[!] File not found: {in_path}")


def resize_image(in_path: str, out_path: str, width: int, height: int) -> None:
    """Resize image to specific dimensions."""
    try:
        img = Image.open(in_path)
        img.resize((width, height), Image.Resampling.LANCZOS).save(out_path)
    except FileNotFoundError:
        print(f"[!] File not found: {in_path}")


def circularity(contour: np.ndarray) -> float:
    """Return circularity metric for a contour."""
    area = cv2.contourArea(contour)
    perim = cv2.arcLength(contour, True)
    return 4 * math.pi * area / (perim**2) if perim else 0.0


def approximate_polygon(contour: np.ndarray, eps_ratio: float = 0.02) -> np.ndarray:
    perim = cv2.arcLength(contour, True)
    return cv2.approxPolyDP(contour, eps_ratio * perim, True)


def detect_orange_shape(img_path: str) -> str:
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Unable to load image: {img_path}")

    h, w = img.shape[:2]
    blur = cv2.GaussianBlur(img, GAUSSIAN_BLUR, 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, ORANGE_LOWER, ORANGE_UPPER)

    kern_big = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    kern_med = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kern_big)
    mask = cv2.dilate(mask, kern_med, iterations=1)
    mask = cv2.erode(mask, kern_med, iterations=1)

    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = 0.02 * h * w

    for cnt in sorted(cnts, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue

        poly = approximate_polygon(cnt)
        vtx = len(poly)

        if vtx == 3:
            return 'Triangle'
        elif vtx == 4:
            x, y, w, h = cv2.boundingRect(poly)
            return 'Rectangle'
        else:
            return 'Circle'

    return 'None'


def crop_region(img: np.ndarray, region: tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = region
    return img


def preprocess_for_tesseract(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, *THRESH_BINARY, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary

def load_and_validate(path: str) -> np.ndarray:
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Failed to load image from: {path}")
    return img

def handle_levenshtein_distance(instructions, detected_intstruction):
    decided_instruction = ""
    MIN_DISTANCE = float('inf')
    for instruction in instructions:
        distance = Levenshtein.distance(detected_intstruction, instruction)
        # print(instruction, distance)
        if distance <= MIN_DISTANCE:
            MIN_DISTANCE = distance
            decided_instruction = instruction

    # print(decided_instruction)
    if decided_instruction == "drag from b to back":
        decided_instruction = "drag from b to background"
    return decided_instruction

# ─── OCR Classes ─────────────────────────────────────────────────────────────
class EasyOCRRecognizer:
    def __init__(self, lang: str = 'en'):
        self.reader = easyocr.Reader([lang], gpu=True)
        self.original_img_path = ""


    @staticmethod
    def is_number(s: str) -> bool:
        return bool(re.fullmatch(r'-?\d+(\.\d+)?', s))

    def get_readable_text(self, img_path: str, originial_img_path: str) -> str:
        self.original_img_path = originial_img_path
        results = self.reader.readtext(img_path)
        text_seq, start = [], False

        for _, text, _ in results:
            if start:
                if not self.is_number(text):
                    text_seq.append(text)
            elif 'touch' in text.lower():
                start = True

        print(text_seq)

        text = ' '.join(text_seq).strip().lower()
        print(text)
        if text is None or text == " " or len(text_seq) == 0:
            return detect_orange_shape(originial_img_path)
        return text


class TesseractRecognizer:
    def __init__(self, lang: str = 'eng'):
        self.lang = lang
        self.original_img_path = ""

    def get_readable_text(self, img_path: str, original_img_path: str) -> str:
        self.original_img_path = original_img_path
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Unable to load image: {img_path}")

        roi = crop_region(img, CROP_REGION)
        if roi.size == 0:
            raise ValueError(f"ROI crop is empty:")
        proc = preprocess_for_tesseract(roi)
        data = pytesseract.image_to_data(proc, lang=self.lang, output_type=pytesseract.Output.DICT)

        texts = data['text']
        print(texts)
        start_idx = next((i for i, t in enumerate(texts) if 'touch' in t.lower() or 'screen' in t.lower()), None)


        if start_idx is not None and len(texts[start_idx + 1:]) > 0:
            interested_texts = texts[start_idx + 1:]
            print(interested_texts)
            result = [t.strip() for t in texts[start_idx + 1:] if t.strip() not in ('|', '_', '')]
            # print("detected string", result)
            if len(result) > 0:
                return ' '.join(result).lower()

        return detect_orange_shape(original_img_path)


# ─── Detector Implementation ────────────────────────────────────────────────
class ShapeTextDetector(Detector):
    def __init__(self, model = OCRDetector.TESERACT, use_api: bool = True, callback = None):
        self.use_api = use_api
        self.model: OCRDetector = model
        self.callback = callback

    def detect(self, img_path: str, originial_img_path: str) -> DetectionResult:
        if self.use_api:
            return self._detect_via_api(img_path)
        
        if self.model == OCRDetector.TESERACT:
            text = handle_levenshtein_distance(instructions, TesseractRecognizer().get_readable_text(img_path, originial_img_path))
            return DetectionResult(text, None)
        else:
            text = handle_levenshtein_distance(instructions, EasyOCRRecognizer().get_readable_text(img_path, originial_img_path))
            return DetectionResult(text, None)

    @staticmethod
    def _detect_via_api(img_path: str) -> DetectionResult:
        url = "http://127.0.0.1:8000/detect-led-instruction"
        with open(img_path, 'rb') as f:
            resp = requests.post(url, files={'file': (img_path, f, 'image/jpeg')})

        if not resp.ok:
            resp.raise_for_status()
        instr = resp.json().get('instruction', '')
        instr = handle_levenshtein_distance(instructions, instr)
        return DetectionResult(instr, None)


# ─── Main Execution ─────────────────────────────────────────────────────────
def main():
    img_src = './resources/messages/WIN_20250522_21_16_42_Pro.jpg'
    out = './cropped.jpg'
    resize_image(img_src, out, width=600, height=400)

    detector = ShapeTextDetector(model=OCRDetector.TESERACT, use_api=False)
    start_time = time.time()
    result = detector.detect(out, img_src)
    print(result)
    print(f"Elapsed: {time.time() - start_time:.2f}s")


if __name__ == '__main__':
    main()

