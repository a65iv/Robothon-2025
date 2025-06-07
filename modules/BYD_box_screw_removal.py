import cv2
import numpy as np

def pick(x, y):
    """
    Function to be called for each screw hole coordinate.
    Replace this with your actual screw picking/processing logic.
    """
    print(f"Processing screw hole at coordinates: ({x}, {y})")
    # Add your screw hole processing logic here
    # For example: move robot to position (x, y) and insert screw
    # time.sleep(1)  # Simulate time taken to process screw hole

def detect_screw_holes(image):
    """
    Detect exactly 4 screw holes in an electronic box image
    Returns list of (x, y) coordinates of hole centers
    """
    # Create a copy for drawing
    result = image.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    # Use HoughCircles to detect circular holes
    # Optimized parameters for screw holes
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,              # Inverse ratio of accumulator resolution
        minDist=50,        # Minimum distance between circle centers
        param1=50,         # Upper threshold for edge detection
        param2=20,         # Accumulator threshold for center detection
        minRadius=10,       # Minimum circle radius
        maxRadius=20       # Maximum circle radius
    )
    
    hole_centers = []
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        
        # Sort circles by area (larger circles first) and take top 4
        circle_data = []
        for (x, y, r) in circles:
            # Calculate confidence based on circularity in the region
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.circle(mask, (x, y), r, 255, -1)
            
            # Check if this looks like a screw hole (darker center)
            roi = cv2.bitwise_and(gray, mask)
            mean_intensity = cv2.mean(roi, mask)[0]
            
            circle_data.append((x, y, r, mean_intensity))
        
        # Sort by darkness (lower intensity = darker = more likely to be a hole)
        circle_data.sort(key=lambda x: x[3])
        
        # Take the 4 darkest circles as screw holes
        for i, (x, y, r, intensity) in enumerate(circle_data[:4]):
            hole_centers.append((x, y))
            
            # Draw the circle and center
            cv2.circle(result, (x, y), r, (0, 255, 0), 2)
            cv2.circle(result, (x, y), 2, (0, 0, 255), -1)
            cv2.putText(result, f'Hole {i+1}', (x - 25, y - r - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            print(f"Screw hole {i+1}: Center at ({x}, {y}), Radius: {r}, Intensity: {intensity:.1f}")
    
    # Alternative method using contour detection if HoughCircles doesn't work well
    if len(hole_centers) < 4:
        print("HoughCircles found less than 4 holes, trying contour method...")
        hole_centers = detect_holes_by_contours(image, result)
    
    return hole_centers, result

def detect_holes_by_contours(image, result):
    """
    Alternative method using contour detection for screw holes
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive threshold to handle varying lighting
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Apply morphological operations to clean up
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours for circular holes
    hole_candidates = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by area (screw holes should be medium-sized)
        if area < 50 or area > 1000:
            continue
        
        # Check circularity
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            continue
        
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Filter by circularity (should be fairly circular)
        if circularity < 0.6:
            continue
        
        # Get centroid
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # Check if it's in a reasonable position (not too close to edges)
            h, w = image.shape[:2]
            if cx > 20 and cx < w-20 and cy > 20 and cy < h-20:
                hole_candidates.append((cx, cy, area, circularity))
    
    # Sort by area and circularity, take top 4
    hole_candidates.sort(key=lambda x: x[2] * x[3], reverse=True)
    
    hole_centers = []
    for i, (x, y, area, circularity) in enumerate(hole_candidates[:4]):
        hole_centers.append((x, y))
        
        # Draw the detection
        cv2.circle(result, (x, y), 8, (0, 255, 0), 2)
        cv2.circle(result, (x, y), 2, (0, 0, 255), -1)
        cv2.putText(result, f'Hole {i+1}', (x - 25, y - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        print(f"Screw hole {i+1}: Center at ({x}, {y}), Area: {area:.0f}, Circularity: {circularity:.2f}")
    
    return hole_centers

def capture_and_process_holes():
    """
    Capture image from webcam and process screw holes
    """
    cap = cv2.VideoCapture(1)
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Electronic Box Screw Hole Detection")
    print("==================================")
    print("Position the electronic box in view...")
    
    # Preview mode
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from webcam")
            cap.release()
            return
        
        # Display preview with instructions
        preview = frame.copy()
        cv2.putText(preview, 'Position electronic box with 4 screw holes visible', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(preview, 'Press SPACE to capture and detect holes', (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(preview, 'Press Q to quit', (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow('Electronic Box - Position for Capture', preview)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Space bar to capture
            captured_frame = frame.copy()
            print("Image captured! Detecting screw holes...")
            break
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return
    
    cap.release()
    
    # Process the captured image
    hole_centers, result_image = detect_screw_holes(captured_frame)
    
    if len(hole_centers) == 0:
        print("No screw holes detected in the captured image.")
        cv2.destroyAllWindows()
        return
    elif len(hole_centers) < 4:
        print(f"Warning: Only {len(hole_centers)} screw holes detected (expected 4)")
    
    # Display results
    cv2.putText(result_image, f'Screw holes found: {len(hole_centers)}', (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    cv2.imshow('Detected Screw Holes', result_image)
    
    # Save the result
    cv2.imwrite('screw_holes_detection_result.jpg', result_image)
    print(f"\nResult image saved as 'screw_holes_detection_result.jpg'")
    
    print(f"\nFound {len(hole_centers)} screw holes. Starting processing sequence...")
    
    # Sort holes by position (top-left, top-right, bottom-left, bottom-right)
    if len(hole_centers) >= 4:
        hole_centers = sort_holes_by_position(hole_centers)
    
    # Cycle through all hole coordinates and call pick function
    for i, (x, y) in enumerate(hole_centers, 1):
        print(f"\nProcessing screw hole {i}/{len(hole_centers)}")
        pick(x, y)
        
        # Optional: Add delay between processing
        # time.sleep(2)  # Uncomment if you want delay between picks
    
    print(f"\nCompleted processing all {len(hole_centers)} screw holes!")
    
    # Keep the result window open
    print("Press any key to close the result window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def sort_holes_by_position(holes):
    """
    Sort holes by position: top-left, top-right, bottom-left, bottom-right
    """
    if len(holes) < 4:
        return holes
    
    # Sort by y-coordinate first (top to bottom)
    holes_sorted = sorted(holes, key=lambda p: p[1])
    
    # Split into top and bottom pairs
    top_holes = sorted(holes_sorted[:2], key=lambda p: p[0])  # Sort by x (left to right)
    bottom_holes = sorted(holes_sorted[2:], key=lambda p: p[0])  # Sort by x (left to right)
    
    # Return in order: top-left, top-right, bottom-left, bottom-right
    ordered_holes = top_holes + bottom_holes
    
    print("Holes ordered by position:")
    positions = ["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"]
    for i, (x, y) in enumerate(ordered_holes):
        print(f"  {positions[i]}: ({x}, {y})")
    
    return ordered_holes

def process_static_image(image_path):
    """
    Process a static image file for screw hole detection
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        return
    
    print(f"Processing static image: {image_path}")
    hole_centers, result_image = detect_screw_holes(image)
    
    if len(hole_centers) == 0:
        print("No screw holes detected in the image.")
        return
    
    # Display and save results
    cv2.imshow('Detected Screw Holes', result_image)
    cv2.imwrite('screw_holes_result.jpg', result_image)
    
    # Process holes
    if len(hole_centers) >= 4:
        hole_centers = sort_holes_by_position(hole_centers)
    
    for i, (x, y) in enumerate(hole_centers, 1):
        print(f"\nProcessing screw hole {i}/{len(hole_centers)}")
        pick(x, y)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Webcam capture mode with camera index 1
    print("Screw Hole Detection System")
    print("===========================")
    print("Using webcam index 1...")
    capture_and_process_holes()

