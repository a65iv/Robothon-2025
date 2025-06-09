import cv2, numpy as np, math

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
            shape = 'Square' if 0.85 <= ar <= 1.15 else 'Rectangle'

        else:
            # ── fit ellipse for anything “roundish”
            (cx,cy), (MA,ma), angle = cv2.fitEllipse(c)
            axis_ratio = max(MA,ma) / min(MA,ma)
            circ       = circularity(c)

            if axis_ratio <= ELLIPSE_AR_THR and circ >= CIRCULARITY_THR:
                shape = 'Circle'
            else:
                shape = 'Circle'

        # simple confidence: bigger blob ⇒ higher confidence
        conf_pct = round(min(1.0, area / (0.4* H * W )) * 100, 1)
        print(conf_pct)

        return shape
    
    
    

print(detect_shape("./resources/messages/_square1.png"))