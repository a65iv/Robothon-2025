import cv2
import numpy as np

def detect_bolts(image_path):
    """
    Detect black bolts on white surface and overlay midpoints
    """
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image from {image_path}")
        return None
    
    # Create a copy for drawing
    result = img.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Threshold to create binary image (black bolts on white surface)
    # Using THRESH_BINARY_INV to make bolts white on black background
    _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Apply morphological operations to clean up the image
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours based on area and circularity
    min_area = 20  # Minimum area for a bolt
    max_area = 500  # Maximum area for a bolt
    min_circularity = 0.3  # Minimum circularity (0-1, where 1 is perfect circle)
    
    bolt_count = 0
    
    for contour in contours:
        # Calculate area
        area = cv2.contourArea(contour)
        
        # Filter by area
        if area < min_area or area > max_area:
            continue
        
        # Calculate circularity
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Filter by circularity (bolts are roughly circular)
        if circularity < min_circularity:
            continue
        
        # Calculate moments to find centroid
        M = cv2.moments(contour)
        if M["m00"] != 0:
            # Calculate centroid (midpoint)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # Draw the contour outline
            cv2.drawContours(result, [contour], -1, (0, 255, 0), 2)
            
            # Draw the midpoint
            cv2.circle(result, (cx, cy), 5, (0, 0, 255), -1)  # Red filled circle
            cv2.circle(result, (cx, cy), 8, (255, 0, 0), 2)   # Blue outline
            
            # Add text label
            cv2.putText(result, f'Bolt {bolt_count + 1}', (cx - 30, cy - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            bolt_count += 1
            
            print(f"Bolt {bolt_count}: Center at ({cx}, {cy}), Area: {area:.0f}, Circularity: {circularity:.2f}")
    
    print(f"\nTotal bolts detected: {bolt_count}")
    
    return result, binary

def main():
    # You can change this to your image path
    image_path = "bolts_image.jpg"  # Replace with your image path
    
    # For webcam capture (uncomment the following lines if you want to use webcam)
    # cap = cv2.VideoCapture(0)
    # ret, frame = cap.read()
    # if ret:
    #     cv2.imwrite("captured_frame.jpg", frame)
    #     image_path = "captured_frame.jpg"
    # cap.release()
    
    result, binary = detect_bolts(image_path)
    
    if result is not None:
        # Display results
        cv2.imshow('Original with Detected Bolts', result)
        cv2.imshow('Binary Image', binary)
        
        # Save the result
        cv2.imwrite('detected_bolts_result.jpg', result)
        print("Result saved as 'detected_bolts_result.jpg'")
        
        # Wait for key press and close windows
        print("\nPress any key to close the windows...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# Alternative function for real-time detection from webcam
def pick_bolt(x, y):
    """
    Function to be called for each bolt center point.
    Replace this with your actual bolt picking logic.
    """
    print(f"Picking bolt at coordinates: ({x}, {y})")
    # Add your bolt picking logic here
    # For example: move robot arm to position (x, y) and pick up the bolt
    # time.sleep(1)  # Simulate time taken to pick bolt
    
def capture_and_process_bolts():
    """
    Capture a single image from webcam, detect bolts, and cycle through center points
    """
    cap = cv2.VideoCapture(1)
    
    # Set camera resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Initializing camera...")
    
    # Preview mode - show live feed until user presses SPACE to capture
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from webcam")
            cap.release()
            return
        
        # Display preview with instructions
        preview = frame.copy()
        cv2.putText(preview, 'Press SPACE to capture image', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(preview, 'Press Q to quit', (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow('Camera Preview - Position your bolts', preview)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Space bar to capture
            captured_frame = frame.copy()
            print("Image captured! Processing...")
            break
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return
    
    cap.release()
    
    # Process the captured image
    bolt_centers = process_captured_image(captured_frame)
    
    if not bolt_centers:
        print("No bolts detected in the captured image.")
        cv2.destroyAllWindows()
        return
    
    print(f"\nFound {len(bolt_centers)} bolts. Starting bolt picking sequence...")
    
    # Cycle through all center points and call pick_bolt function
    for i, (x, y) in enumerate(bolt_centers, 1):
        print(f"\nProcessing bolt {i}/{len(bolt_centers)}")
        pick_bolt(x, y)
        
        # Optional: Add delay between picks
        # time.sleep(2)  # Uncomment if you want delay between picks
    
    print(f"\nCompleted processing all {len(bolt_centers)} bolts!")
    
    # Keep the result window open until user presses a key
    print("Press any key to close the result window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def process_captured_image(frame):
    """
    Process a single captured image and return list of bolt center coordinates
    """
    # Create a copy for drawing
    result = frame.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Threshold to create binary image
    _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Apply morphological operations to clean up the image
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours and collect center points
    bolt_centers = []
    min_area = 50
    max_area = 10000
    min_circularity = 0.3
    
    for contour in contours:
        # Calculate area
        area = cv2.contourArea(contour)
        
        # Filter by area
        if area < min_area or area > max_area:
            continue
        
        # Calculate circularity
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Filter by circularity
        if circularity < min_circularity:
            continue
        
        # Calculate centroid
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            bolt_centers.append((cx, cy))
            
            # Draw visualization
            cv2.drawContours(result, [contour], -1, (0, 255, 0), 2)
            cv2.circle(result, (cx, cy), 5, (0, 0, 255), -1)  # Red filled circle
            cv2.circle(result, (cx, cy), 8, (255, 0, 0), 2)   # Blue outline
            cv2.putText(result, f'Bolt {len(bolt_centers)}', (cx - 30, cy - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            print(f"Bolt {len(bolt_centers)}: Center at ({cx}, {cy}), Area: {area:.0f}, Circularity: {circularity:.2f}")
    
    # Display result
    cv2.putText(result, f'Total bolts found: {len(bolt_centers)}', (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    cv2.imshow('Detected Bolts - Processing Complete', result)
    cv2.imshow('Binary Image', binary)
    
    # Save the result
    cv2.imwrite('bolt_detection_result.jpg', result)
    print(f"\nResult image saved as 'bolt_detection_result.jpg'")
    
    return bolt_centers

if __name__ == "__main__":
    # Single capture mode with bolt picking sequence
    print("Bolt Detection and Picking System")
    print("================================")
    capture_and_process_bolts()
    
    # Uncomment the line below for static image detection instead
    # main()
    
    # Uncomment the line below for continuous real-time detection
    # detect_bolts_realtime()
