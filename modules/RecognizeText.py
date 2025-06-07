import cv2
import easyocr
import time
import re
from paddleocr import PaddleOCR

class RecognizeText:
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
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
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
        shape = self.detect_shape(image_path)
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
            if "Time" in text_str:
                start_append = True
        text = led_instruction.strip().lower()
        print(text, shape)
        if text == "" and shape != "Other":
            print(f"Detected shape: {shape}")
            return shape
        print(f"Recognized text: {text}")
        return text
    
img_path = './resources/messages/WIN_20250522_21_17_28_Pro.jpg'
if __name__ == "__main__":
    start = time.time()
    recognizer = RecognizeText(lang='en')
    recognizer.get_readable_text(img_path)
    end = time.time()
    print(f"Text recognition completed in {end - start:.2f} seconds")


class PaddleRecognizeText():
    def __init__(self): 
        self.ocr = PaddleOCR(use_angle_cls=True, use_gpu=True)
    def recognize_text(self, image_path):
        """
        Recognizes text in the given image using PaddleOCR.
        :param image_path: Path to the image file.
        :return: List of detected text strings.
        """
        results = self.ocr.ocr(image_path, cls=True)
        text_results = []
        for result in results:
            for line in result:
                text = line[1][0]
                text_results.append(text)
        return text_results
