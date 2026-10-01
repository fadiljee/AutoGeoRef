import cv2
import numpy as np
import easyocr
import os
import re
from . import config

# Initialize EasyOCR globally (once at startup to save memory)
ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)

def advanced_preprocessing(image):
    """
    Advanced Image Pre-processing Pipeline for sub-pixel precision.
    """
    # 1. Color Masking (Isolasi Warna Cyan/Blue)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([150, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # 2. Upscaling (Pembesaran Resolusi 300%)
    width = int(mask.shape[1] * 3)
    height = int(mask.shape[0] * 3)
    upscaled_mask = cv2.resize(mask, (width, height), interpolation=cv2.INTER_CUBIC)

    # 3. Binarization - invert so text is black on white bg
    binary_inv = cv2.bitwise_not(upscaled_mask)

    # 4. Morphological Ops - erode to thicken text strokes
    kernel = np.ones((2, 2), np.uint8)
    processed = cv2.erode(binary_inv, kernel, iterations=1)

    return processed

def crop_corners(image_path, filename):
    """
    Crop the 4 corners of the image.
    Returns a dictionary of cropped images and the image dimensions.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image {image_path}")

    h, w = img.shape[:2]
    cw = config.CROP_WIDTH
    ch = config.CROP_HEIGHT

    corners = {
        "top_left":     img[0:ch, 0:cw],
        "top_right":    img[0:ch, w-cw:w],
        "bottom_left":  img[h-ch:h, 0:cw],
        "bottom_right": img[h-ch:h, w-cw:w]
    }

    # Save debug crops
    for name, crop_img in corners.items():
        base = os.path.splitext(filename)[0]
        debug_path = os.path.join(config.TEMP_DIR, f"{base}_{name}.jpg")
        cv2.imwrite(debug_path, crop_img)

    return corners, (w, h)

def parse_coordinate_text(text):
    """
    Strict Regex Validation - extract float with >= 4 decimal places.
    Falls back to accepting >= 2 decimal places so partial reads still work.
    """
    # Try strict: >= 6 decimal places (PRD v2.0 requirement)
    matches = re.findall(r'-?\d+\.\d{6,}', text)
    if matches:
        try:
            return float(matches[0])
        except ValueError:
            pass
    # Fallback: accept >= 2 decimal places 
    matches = re.findall(r'-?\d+\.\d{2,}', text)
    if matches:
        try:
            return float(matches[0])
        except ValueError:
            pass
    return None

def extract_coordinates(corners):
    """
    Apply EasyOCR to cropped corners and return extracted coords.
    """
    results = {}
    for name, img in corners.items():
        processed = advanced_preprocessing(img)

        # EasyOCR returns list of (bbox, text, confidence)
        ocr_results = ocr_reader.readtext(processed, detail=1, paragraph=False,
                                          allowlist='0123456789.-')

        extracted_val = None
        for (_, text, confidence) in ocr_results:
            if confidence < 0.3:
                continue
            val = parse_coordinate_text(text)
            if val is not None:
                extracted_val = val
                break

        results[name] = extracted_val

    return results

def validate_and_consolidate(extracted_results):
    """
    Map corner OCR results to geospatial variables and validate.
    top_left  -> X_min, Y_max
    top_right -> X_max, Y_max
    bottom_left  -> X_min, Y_min
    bottom_right -> X_max, Y_min
    """
    tl = extracted_results.get("top_left")
    tr = extracted_results.get("top_right")
    bl = extracted_results.get("bottom_left")
    br = extracted_results.get("bottom_right")

    # Determine coordinates from available results
    X_min = tl if tl is not None else (bl if bl is not None else None)
    X_max = tr if tr is not None else (br if br is not None else None)
    Y_max_val = tl if tl is not None else (tr if tr is not None else None)
    Y_min_val = bl if bl is not None else (br if br is not None else None)

    # If OCR failed on all corners, return None
    if None in (X_min, X_max, Y_max_val, Y_min_val):
        return None

    # For Bangka area: longitude ~105-108 (X), latitude ~-1.5 to -3.5 (Y)
    # Corner top = Y_max (less negative), corner bottom = Y_min (more negative)
    # Corner left = X_min, corner right = X_max
    # Here we need specific per-corner logic; use a heuristic:
    # If value is in longitude range -> it's an X coord
    # If value is in latitude range  -> it's a Y coord

    def classify(val):
        if val is None:
            return None, None
        if config.VALID_X_MIN <= val <= config.VALID_X_MAX:
            return 'X', val
        if config.VALID_Y_MIN <= val <= config.VALID_Y_MAX:
            return 'Y', val
        return None, None

    # Collect all extracted non-None values and classify
    coords = {'X': [], 'Y': []}
    for corner_name, val in extracted_results.items():
        ctype, cval = classify(val)
        if ctype:
            coords[ctype].append(cval)

    if len(coords['X']) < 1 or len(coords['Y']) < 1:
        return None

    X_min_final = min(coords['X'])
    X_max_final = max(coords['X']) if len(coords['X']) > 1 else X_min_final + 0.5
    Y_min_final = min(coords['Y'])
    Y_max_final = max(coords['Y']) if len(coords['Y']) > 1 else Y_min_final + 0.5

    # Validate all values within Bangka Belitung bounds
    if not (config.VALID_X_MIN <= X_min_final <= config.VALID_X_MAX and
            config.VALID_X_MIN <= X_max_final <= config.VALID_X_MAX and
            config.VALID_Y_MIN <= Y_min_final <= config.VALID_Y_MAX and
            config.VALID_Y_MIN <= Y_max_final <= config.VALID_Y_MAX):
        return None

    return {
        "X_min": X_min_final,
        "X_max": X_max_final,
        "Y_min": Y_min_final,
        "Y_max": Y_max_final
    }
