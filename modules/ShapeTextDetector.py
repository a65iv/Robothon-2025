import math
import re
import time

import cv2
import easyocr
import numpy as np
import pytesseract
import requests
import Levenshtein
import asyncio
from enum import Enum
# from keras.models import load_model
import tensorflow as tf
from PIL import Image, ImageOps 
import numpy as np
import os
import io

from modules.Detector import Detector, DetectionResult

import tracemalloc
tracemalloc.start()


class OCRDetector(Enum):
    TESERACT = "teseract"
    EASYOCR = "easyocr"

instructions = [
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


def keras_detect_shape(image_buffer):
    """
    Detects a shape in an image using a pre-trained Keras model.

    Args:
        image_buffer (bytes): The image file content as a byte buffer.

    Returns:
        str: The predicted class name for the shape in the image.
             Returns None if model or label files are not found, or if the buffer is invalid.
    """
    # Define paths for the model and labels
    model_path = "./KerasModel/keras_model.h5"
    labels_path = "./KerasModel/labels.txt"

    # --- Pre-computation Checks ---
    # Check if the required model and label files exist before proceeding
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return None
    if not os.path.exists(labels_path):
        print(f"Error: Labels file not found at {labels_path}")
        return None

    # --- Keras/TensorFlow Setup ---
    # Disable scientific notation for clarity in numpy
    np.set_printoptions(suppress=True)

    # Load the model.
    # Using compile=False speeds up loading for inference-only models.
    try:
        model = tf.keras.models.load_model(model_path, compile=False)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

    # Load the labels, stripping out newline characters.
    with open(labels_path, "r") as f:
        class_names = [line.strip() for line in f.readlines()]

    # --- Image Processing ---
    # Create a numpy array with the right shape to feed into the Keras model.
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # UPDATED: Open the image from the in-memory byte buffer instead of a file path.
    try:
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    except Exception as e:
        print(f"Error opening image from buffer: {e}")
        return None


    # Resize the image to 224x224 and crop from the center.
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

    # Convert the image into a numpy array.
    image_array = np.asarray(image)

    # Normalize the image data to the range of -1 to 1.
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Load the processed image data into our batch array.
    data[0] = normalized_image_array

    # --- Prediction ---
    # Run the model's prediction on the image data.
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    # Print prediction and confidence score
    # The class name is sliced [2:] to remove the leading number and space (e.g., "0 circle")
    print(f"Class: {class_name[2:]}")
    print(f"Confidence Score: {confidence_score:.4f}") # Formatted for readability

    return class_name[2:].lower()

def reduce_image_size(in_path: str, out_path: str, quality: int = 85) -> None:
    """Compress image using Pillow."""
    try:
        img = Image.open(in_path)
        img.save(out_path, optimize=True, quality=quality)
    except FileNotFoundError:
        print(f"[!] File not found: {in_path}")


# def resize_image(in_path: str, out_path: str, width: int, height: int) -> None:
#     """Resize image to specific dimensions."""
#     try:
#         img = Image.open(in_path)
#         img.resize((width, height), Image.Resampling.LANCZOS).save(out_path)
#     except FileNotFoundError:
#         print(f"[!] File not found: {in_path}")


def resize_image(image_bgr: np.ndarray, width: int, height: int) -> np.ndarray:
    """
    Resize an OpenCV (BGR) image in memory and return the resized image (still BGR).
    
    Args:
        image_bgr (np.ndarray): The original OpenCV image (BGR format).
        width (int): Target width.
        height (int): Target height.

    Returns:
        np.ndarray: The resized OpenCV image.
    """
    try:
        resized = cv2.resize(image_bgr, (width, height), interpolation=cv2.INTER_LANCZOS4)
        return resized
    except Exception as e:
        print(f"[!] Error resizing image: {e}")
        return image_bgr  # Return original if resizing fails


def detect_shape(image):

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
    shape_name = "Unknown"

    if best_cnt is not None:
        area = cv2.contourArea(best_cnt)
        peri = cv2.arcLength(best_cnt, True)
        circularity = 4 * np.pi * area / (peri * peri) if peri > 0 else 0
        approx = cv2.approxPolyDP(best_cnt, 0.015 * peri, True)
        vertices = len(approx)

        # Shape logic
        if circularity > 0.75 and vertices >= 8:
            shape_name = "Circle"
        elif vertices == 3:
            shape_name = "Triangle"
        elif vertices == 4:
            x, y, w, h = cv2.boundingRect(approx)
            ar = w / float(h)
            shape_name = "Square"
        else:
            shape_name = "Circle" 
            
    print("shape: ", shape_name)
    return shape_name.lower()

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

    print(detected_intstruction, decided_instruction)
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

    def get_readable_text(self, img_path) -> str:
        results = self.reader.readtext(img_path)
        text_seq, start = [], False

        for _, text, _ in results:
            if start:
                if not self.is_number(text):
                    text_seq.append(text)
            elif 'touch' in text.lower():
                start = True

        text = ' '.join(text_seq).strip().lower()
        print("Text detected: ",  text)
        if text is None or text == " " or len(text_seq) == 0:
            return detect_shape(img_path)
        return text


class TesseractRecognizer:
    def __init__(self, lang: str = 'eng'):
        self.lang = lang

    def get_readable_text(self, img) -> str:
        # self.original_img_path = original_img_path
        # img = cv2.imread(img_path)
        if img is None:
            raise ValueError(f"Unable to load image")

        roi = crop_region(img, CROP_REGION)
        if roi.size == 0:
            raise ValueError(f"ROI crop is empty:")
        proc = preprocess_for_tesseract(roi)
        data = pytesseract.image_to_data(proc, lang=self.lang, output_type=pytesseract.Output.DICT)

        texts = data['text']
        start_idx = next((i for i, t in enumerate(texts) if 'touch' in t.lower() or 'screen' in t.lower()), None)


        if start_idx is not None and len(texts[start_idx + 1:]) > 0:
            interested_texts = texts[start_idx + 1:]
            result = [t.strip() for t in texts[start_idx + 1:] if t.strip().lower() not in ('|', '_', 'screen' '')]
            print("detected string ", result)
            if len(result) > 0 :
                return handle_levenshtein_distance(instructions, ' '.join(result).lower())

        return keras_detect_shape(img)


# ─── Detector Implementation ────────────────────────────────────────────────
class ShapeTextDetector(Detector):
    def __init__(self, model = OCRDetector.TESERACT, use_api: bool = False, callback = None):
        self.use_api = use_api
        self.model: OCRDetector = model
        self.callback = callback
        self.img_path = "./cropped.jpg"

    async def detect(self, frame) -> DetectionResult:
        img = resize_image(frame, width=600, height=400)
        if self.use_api:
            return self._detect_via_api(self.img_path)
        
        if self.model == OCRDetector.TESERACT:
            text = TesseractRecognizer().get_readable_text(img)
            if self.callback is not None:
                await self.callback(text)
            return DetectionResult(text, None)
        else:
            text = EasyOCRRecognizer().get_readable_text(img)
            if self.callback is not None:
                await self.callback(text)
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
async def main():
    # img_src = './resources/messages/WIN_20250522_21_16_42_Pro.jpg'
    # out = './cropped.jpg'
    # resize_image(img_src, out, width=600, height=400)
    
    # cam = Cam(2)
    # cam.take_picture(filename="piccc.png")
    # img = cv2.imread("piccc.png")
    
    img = cv2.imread("./resources/messages/_triangle1.png")
    

    detector = ShapeTextDetector(model=OCRDetector.TESERACT, use_api=False)
    start_time = time.time()
    result = await detector.detect(img)
    print(result)
    print(f"Elapsed: {time.time() - start_time:.2f}s")


if __name__ == '__main__':
    asyncio.run(main())

