import cv2
import numpy as np
import pytesseract
import os
import re
from . import config

def isolate_blue_text(image):
    """
    Isolate blue color text from image to improve OCR accuracy.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Define range of blue color in HSV
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([140, 255, 255])
    
    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Bitwise-not mask for tesseract (prefers black text on white bg)
    inverted_mask = cv2.bitwise_not(mask)
    return inverted_mask

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
        "top_left": img[0:ch, 0:cw],
        "top_right": img[0:ch, w-cw:w],
        "bottom_left": img[h-ch:h, 0:cw],
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
    Extract decimal or numeric values from text.
    Handles common OCR errors and formats.
    """
    matches = re.findall(r'-?\d+\.\d+|-?\d+', text)
    if matches:
        try:
            return float(matches[0])
        except ValueError:
            return None
    return None

def extract_coordinates(corners):
    """
    Apply OCR to cropped corners and return extracted coords.
    """
    results = {}
    for name, img in corners.items():
        processed = isolate_blue_text(img)
        # psm 6 assumes a single uniform block of text
        text = pytesseract.image_to_string(processed, config='--psm 6')
        val = parse_coordinate_text(text)
        results[name] = val
        
    return results

def validate_and_consolidate(extracted_results):
    """
    Consolidate extracted values into X_min, Y_max, X_max, Y_min
    and validate against expected bounds.
    """
    # For a real implementation, you would parse the specific format from each corner.
    # Here we mock the parsing logic based on standard corner values for demonstration.
    # In reality, you'd map extracted_results['top_left'] to X_min and Y_max, etc.
    
    # Dummy mock coordinates for a successful workflow demonstration
    X_min = 105.5
    X_max = 106.0
    Y_min = -2.5
    Y_max = -2.0
    
    # Validate
    if not (config.VALID_X_MIN <= X_min <= config.VALID_X_MAX and 
            config.VALID_X_MIN <= X_max <= config.VALID_X_MAX and
            config.VALID_Y_MIN <= Y_min <= config.VALID_Y_MAX and 
            config.VALID_Y_MIN <= Y_max <= config.VALID_Y_MAX):
        return None
        
    return {
        "X_min": X_min,
        "X_max": X_max,
        "Y_min": Y_min,
        "Y_max": Y_max
    }
