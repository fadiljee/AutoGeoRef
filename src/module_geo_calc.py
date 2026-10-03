import os
import shutil
import cv2
from . import config

def get_neatline_bounds(image_path):
    """
    Detect the inner map boundary (neatline) which holds the true geographic coordinates.
    Returns (x, y, w, h) of the neatline in pixels.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Cannot read image {image_path}")
    
    # Threshold to find dark lines on white background
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    h, w = img.shape[:2]
    image_area = h * w
    
    best_rect = None
    best_area = 0
    
    # Find the largest contour that covers between 50% and 98% of the image area
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        if 0.5 * image_area < area < 0.98 * image_area:
            if area > best_area:
                best_area = area
                best_rect = (x, y, cw, ch)
                
    if best_rect:
        return best_rect
        
    # Fallback to Canny edge detection if simple threshold fails
    edges = cv2.Canny(img, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        if 0.5 * image_area < area < 0.98 * image_area:
            if area > best_area:
                best_area = area
                best_rect = (x, y, cw, ch)
                
    if best_rect:
        return best_rect
        
    # If no neatline detected, fallback to the entire image bounds
    return (0, 0, w, h)

def calculate_affine(X_min, X_max, Y_min, Y_max, neatline_bounds):
    """
    Calculate 6 affine parameters for .pgw world file.
    Returns: [pixel_x_size, rotation_x, rotation_y, pixel_y_size, X_upper_left, Y_upper_left]
    """
    nx, ny, nw, nh = neatline_bounds
    
    pixel_x_size =  (X_max - X_min) / nw
    pixel_y_size = -(Y_max - Y_min) / nh  # negative: Y decreases downward
    
    # Calculate the coordinates for the absolute top-left pixel (0,0) of the image paper,
    # by offsetting from the neatline's top-left corner.
    X_upper_left = X_min - (nx * pixel_x_size)
    # Since pixel_y_size is negative, subtracting (ny * pixel_y_size) increases the Y value
    # (moving UP towards pixel 0, which corresponds to a higher latitude/Y coordinate).
    Y_upper_left = Y_max - (ny * pixel_y_size)

    return [
        pixel_x_size,   # A: pixel size X
        0.0,            # B: rotation (always 0 for north-up maps)
        0.0,            # C: rotation (always 0)
        pixel_y_size,   # D: pixel size Y (negative)
        X_upper_left,   # E: X coordinate of upper-left pixel center
        Y_upper_left    # F: Y coordinate of upper-left pixel center
    ]

def generate_pgw(filename, affine_params, output_dir):
    """
    Write affine parameters to a .pgw world file.
    """
    base = os.path.splitext(filename)[0]
    pgw_path = os.path.join(output_dir, base + ".pgw")
    with open(pgw_path, 'w') as f:
        for param in affine_params:
            f.write(f"{param:.10f}\n")
    return pgw_path

def generate_aux_xml(filename, affine_params, output_dir):
    """
    Generate a .aux.xml georeferencing metadata file alongside the image.
    Uses affine parameters directly to map correctly across margins.
    """
    pixel_x_size, _, _, pixel_y_size, X_upper_left, Y_upper_left = affine_params
    base = os.path.splitext(filename)[0]
    xml_path = os.path.join(output_dir, filename + ".aux.xml")

    xml_content = f"""<PAMDataset>
  <SRS dataAxisToSRSAxisMapping="2,1">GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]</SRS>
  <GeoTransform> {X_upper_left:.10f},  {pixel_x_size:.10f},  0,  {Y_upper_left:.10f},  0, {pixel_y_size:.10f}</GeoTransform>
</PAMDataset>
"""
    with open(xml_path, 'w') as f:
        f.write(xml_content)
    return xml_path

def copy_image_to_output(src_path, filename, output_dir):
    """
    Copy the source image JPG to the output directory.
    """
    dst_path = os.path.join(output_dir, filename)
    shutil.copy2(src_path, dst_path)
    return dst_path

