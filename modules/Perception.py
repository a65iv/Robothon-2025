import os
import numpy as np
import tensorflow as tf
import cv2

# --- Load the TFLite model ---
interpreter = tf.lite.Interpreter(model_path="../models/tflite/model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_shape = input_details[0]['shape']
input_dtype = input_details[0]['dtype']
img_size = (input_shape[2], input_shape[1])  # (width, height)

# --- Load and preprocess image ---
image = cv2.imread("your_image.jpg")
image_resized = cv2.resize(image, img_size)
input_tensor = np.expand_dims(image_resized, axis=0).astype(input_dtype)

# --- Inference ---
interpreter.set_tensor(input_details[0]['index'], input_tensor)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])  # shape: (1, 40, 4)

# --- Post-processing ---
boxes = output_data[0]  # shape: (40, 4)

# Draw top N boxes (e.g., first 5 for now)
for i in range(5):
    x1, y1, x2, y2 = boxes[i]
    
    # If normalized coordinates (likely), scale back to original image size
    x1 = int(x1 * image.shape[1])
    y1 = int(y1 * image.shape[0])
    x2 = int(x2 * image.shape[1])
    y2 = int(y2 * image.shape[0])

    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, f"Box {i}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

# --- Show result ---
cv2.imshow("Detections", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
