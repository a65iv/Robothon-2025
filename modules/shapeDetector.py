import os
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps 
from modules.Detector import Detector, DetectionResult

class ShapeDetector(Detector):
    def __init__(self, name):
        model_path = "./KerasModel/keras_model.h5"
        labels_path = "./KerasModel/labels.txt"

        self.name = name
        self.model = None
        self.class_names = None

        if not os.path.exists(model_path):
            print(f"Error: Model file not found at {model_path}")
        if not os.path.exists(labels_path):
            print(f"Error: Labels file not found at {labels_path}")

        try:
            self.model = tf.keras.models.load_model(model_path, compile=False)
            with open(labels_path, "r") as f:
                self.class_names = [line.strip() for line in f.readlines()]

        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    def _detect_shape(self, image_buffer):
        np.set_printoptions(suppress=True)
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        try:
            image = Image.fromarray(cv2.cvtColor(image_buffer, cv2.COLOR_BGR2RGB))
        except Exception as e:
            print(f"Error opening image from buffer: {e}")
            return None

        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

        image_array = np.asarray(image)

        # Normalize the image data to the range of -1 to 1.
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

        # Load the processed image data into our batch array.
        data[0] = normalized_image_array

        # --- Prediction ---
        # Run the model's prediction on the image data.
        prediction = self.model.predict(data)
        index = np.argmax(prediction)
        class_name = self.class_names[index]
        confidence_score = prediction[0][index]

        # The class name is sliced [2:] to remove the leading number and space (e.g., "0 circle")
        print(f"Class: {class_name[2:]}")
        print(f"Confidence Score: {confidence_score:.4f}") # Formatted for readability

        return class_name[2:].lower()


    async def detect(self, frame):  
        name = self._detect_shape(frame)
        return DetectionResult(name, midpoint=None)