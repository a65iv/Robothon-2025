import cv2
import easyocr
import re
import time
import pytesseract
import numpy as np
import requests
from PIL import Image
from modules.DetectorClass import Detector, DetectionResult
import math
# from mask import detect_shape



def reduce_image_size(image_path, output_path, quality=85):
    """
    Reduces the file size of an image using Pillow.

    Args:
        image_path (str): The path to the input image file.
        output_path (str): The path to save the compressed image.
        quality (int): The quality of the compressed image (0-100, lower is smaller).
    """
    try:
        image = Image.open(image_path)
        image.save(output_path, optimize=True, quality=quality)
        print(f"Image compressed and saved to: {output_path}")
    except FileNotFoundError:
        print(f"Error: Image not found at path: {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def reduce_resolution(image_path, output_path, new_width, new_height):
       try:
           img = Image.open(image_path)
           img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS) # Use Image.Resampling.LANCZOS for higher quality
           img_resized.save(output_path)
           print(f"Image resized and saved to {output_path}")
       except FileNotFoundError:
           print(f"Error: Image not found at {image_path}")
       except Exception as e:
           print(f"An error occurred: {e}")

   # Example usage:
#    reduce_resolution("input_image.jpg", "output_image.jpg", 600, 400)


def circularity(cnt) -> float:
    a = cv2.contourArea(cnt)
    p = cv2.arcLength(cnt, True)
    return 0 if p == 0 else 4 * math.pi * a / (p * p)

def polygonize(cnt, eps_ratio=0.02):
    peri = cv2.arcLength(cnt, True)
    return cv2.approxPolyDP(cnt, eps_ratio * peri, True)

def detect_shape(img_path):
    CROP_BOTTOM_RIGHT = True          # False = analyse entire image
    MIN_AREA_FRAC     = 0.02          # ignore blobs <2 % of frame
    BLUR_KSIZE        = (7, 7)
    CIRCULARITY_THR   = 0.60          # ≥0.60 → “round enough”
    ELLIPSE_AR_THR    = 1.25          # >1.25 axis-ratio ⇒ ellipse
    img = cv2.imread(img_path)

    H, W = img.shape[:2]

    # 1) orange mask with heavy “glue”
    blur = cv2.GaussianBlur(img, BLUR_KSIZE, 0)
    hsv  = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    lowerb = np.array([10, 100, 100], dtype=np.uint8)
    upperb = np.array([25, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lowerb, upperb)

    kernel_big = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15,15))
    kernel_med = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9,9))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_big)
    mask = cv2.dilate(mask, kernel_med, iterations=1)
    mask = cv2.erode (mask, kernel_med, iterations=1)
    # 2) contours
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = MIN_AREA_FRAC * H * W
    out = img.copy()
    shape = "Circle"

    for c in sorted(cnts, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(c)
        if area < min_area:
            continue

        approx = polygonize(c)
        vtx    = len(approx)
        x,y,w,h = cv2.boundingRect(approx)

        # ── polygons first
        if vtx == 3:
            shape = 'Triangle'

        elif vtx == 4:
            ar = w/float(h)
            # shape = 'Square' if 0.85 <= ar <= 1.15 else 'Rectangle'
            shape = 'Square' if 0.85 <= ar <= 1.15 else 'Rectangle'

        else:
            # ── fit ellipse for anything “roundish”
            (cx,cy), (MA,ma), angle = cv2.fitEllipse(c)
            axis_ratio = max(MA,ma) / min(MA,ma)
            circ       = circularity(c)

            shape = "Circle"

            if axis_ratio <= ELLIPSE_AR_THR and circ >= CIRCULARITY_THR:
                shape = 'Circle'
            else:
                shape = 'Circle'

        # simple confidence: bigger blob ⇒ higher confidence
        conf_pct = round(min(1.0, area / (0.4* H * W )) * 100, 1)
        print(conf_pct)

    return shape


class EasyOCRTextRecognizer:
    def __init__(self, lang='en'):
        self.reader = easyocr.Reader([lang], gpu=True)

    def recognize_text(self, image_path):
        """
        Recognizes text in the given image using EasyOCR.

        :param image_path: Path to the image file.
        :return: List of detected text strings.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found or unable to read: {image_path}")
        results = self.reader.readtext(image_path)
        return [result for result in results]

    def is_number(self, s):
        return bool(re.fullmatch(r'-?\d+(\.\d+)?', s))
    
    def detect_shape(self, image_path):
        """
        Detects the shape of the object in the image.

        :param image_path: Path to the image file.
        :return: Detected shape as a string.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found or unable to read: {image_path}")
        x, y, w, h = 1200, 550, 2000, 1500 
        img = img[y:y+h, x:x+w]  # Crop the image to the region of interest
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 100, 200, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # cv2.imshow("Threshold Image", thresh)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.175 * cv2.arcLength(cnt, True), True)
            # print(f"Detected contour with {len(approx)} vertices")
            if len(approx) == 3:
                shape = "Triangle"
            elif len(approx) == 4:
                shape = "Rectangle"
            elif len(approx) > 10:
                shape = "Circle"
            else:
                shape = "Other"

        return shape
    
    def get_readable_text(self, image_path):
        """
        Returns a readable string from the recognized text in the image.

        :param image_path: Path to the image file.
        :return: Readable string of recognized text.
        """
        results = self.recognize_text(image_path)
        shape = detect_shape(image_path)
        start_append = False
        led_instruction = ""
        sec_count = 0
        for text in results:
            _, text_str, _ = text
            # print(f"Detected text: {text_str} with confidence: {confidence:.2f}")
            if start_append:
                sec_count += 1
                if self.is_number(text_str) == False:
                    led_instruction += text_str + " "
            if "touch" in text_str.lower():
                start_append = True
        text = led_instruction.strip().lower()
        print(text, shape)
        if text == "" and shape != "Other":
            print(f"Detected shape: {shape}")
            return shape
        print(f"Recognized text: {text}")
        return text
    
class TesseractTextRecognizer:
    def __init__(self, lang='eng'):
        self.lang = lang

    #opening - erosion followed by dilation
    def opening(self, image):
        kernel = np.ones((5,5),np.uint8)
        return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    #thresholding
    def thresholding(self, image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    #canny edge detection
    def canny(self, image):
        return cv2.Canny(image, 100, 200)

    def recognize_text(self, image_path):
        """
        Recognizes text in the given image using Tesseract OCR.

        :param image_path: Path to the image file.
        :return: List of detected text strings.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Image not found or unable to read: {image_path}")
        # img = self.thresholding(img)
        # img = self.canny(img)
        # img = self.opening(img)

        # text = pytesseract.image_to_string(img, lang=self.lang)
        # Adding custom options
        custom_config = r'--oem 3 --psm 6'
        data = pytesseract.image_to_data(img, lang=self.lang, output_type=pytesseract.Output.DICT)
        print(data)
        return data['text']
    
    def get_readable_text(self, image_path):
        """
        Returns a readable string from the recognized text in the image.

        :param image_path: Path to the image file.
        :return: Readable string of recognized text.
        """
        data = self.recognize_text(image_path)
        number_predicate = lambda s: re.fullmatch(r'-?\d+(\.\d+)?', s)
        index = next((i for i, text in enumerate(data) if "touch" in text.lower() or "screen" in text.lower()), None)
        if index is not None:
            # slice the list to get the text from the first number to the end
            index += 1  # Skip the "TOUCH_SCREEN" text
            interested_text = data[index:]
            text_result = []
            for text in interested_text:
                if text.strip() not in ["|", "_", ""]:
                    text_result.append(text.strip())
            

            text = ' '.join(text_result).lower()
        if not text:
            shape = detect_shape(img_path=image_path)
            return shape
        return text
    
img_path = './resources/messages/square1.jpg'

class ShapeAndTextDetector(Detector):
    def __init__(self):
        self.output_path = "./cropped.jpg"

    def detect(self, image_path = None, use_api = True) -> DetectionResult:
        """
        Recognizes text in the given image using an external API.

        :param image_path: Path to the image file.
        :return: Readable string of recognized text.
        """
        if use_api: 
            return self.recognise_text_api(image_path)
        else :
            return self.recognize_text_local(image_path)
        
        
    def recognise_text_api(self, image_path = None) -> DetectionResult:
        """
        Recognizes text in the given image using an external API.

        :param image_path: Path to the image file.
        :return: Readable string of recognized text.
        """
        
        output_path = "./cropped.jpg" if image_path is None else image_path
        url = "http://127.0.0.1:8000/detect-led-instruction"
        # read the image and convert to base 64
        with open(output_path, 'rb') as img_file:
            files = {"file": (output_path, img_file, "image/jpeg")}
            response = requests.post(url, files=files)

        
        if response.status_code == 200:
            result = response.json()
            print(f"API response: {result}")
            instruction = result.get('instruction', [])
            return DetectionResult(instruction, None)
        else:
            raise Exception(f"API request failed with status code {response.status_code}")
        
    def recognize_text_local(self, image_path = None) -> DetectionResult:
        recognizer = EasyOCRTextRecognizer(lang='en')
        recognizedValue = recognizer.get_readable_text(img_path)

        return DetectionResult(recognizedValue, None)

if __name__ == "__main__":
    output_path = "./cropped.jpg" 
    # reduce_image_size(img_path, output_path, 20)
    reduce_resolution(img_path, output_path, 600, 400)
    start = time.time()
    # print(recognise_text_api(img_path))
    shape_text_detector = ShapeAndTextDetector()
    print(shape_text_detector.detect())
    end = time.time()
    print(f"Text recognition completed in {end - start:.2f} seconds")

