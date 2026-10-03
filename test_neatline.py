import cv2
import numpy as np
import sys

def find_neatline(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold to find dark lines
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # The neatline is usually a very large rectangle, but not the image edge itself.
    h, w = img.shape[:2]
    image_area = h * w
    
    best_rect = None
    best_area = 0
    
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        # We look for a box that is between 50% and 98% of the image area
        if 0.5 * image_area < area < 0.98 * image_area:
            if area > best_area:
                best_area = area
                best_rect = (x, y, cw, ch)
                
    print(f"Image shape: {w}x{h}")
    if best_rect:
        x, y, cw, ch = best_rect
        print(f"Neatline found: x={x}, y={y}, w={cw}, h={ch}")
        print(f"Margins: Left={x}, Top={y}, Right={w-(x+cw)}, Bottom={h-(y+ch)}")
    else:
        print("Neatline not found with simple threshold. Trying edge detection.")
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            area = cw * ch
            if 0.5 * image_area < area < 0.98 * image_area:
                if area > best_area:
                    best_area = area
                    best_rect = (x, y, cw, ch)
        if best_rect:
            x, y, cw, ch = best_rect
            print(f"Neatline found via Canny: x={x}, y={y}, w={cw}, h={ch}")
        else:
            print("Still no neatline found.")

find_neatline('data/1_input_raw/1903051009000100_WSS.jpg')
