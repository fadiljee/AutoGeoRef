import os
import csv
import shutil
import sys

# Ensure src is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import config
from src.module_ocr import crop_corners, extract_coordinates, validate_and_consolidate
from src.module_geo_calc import calculate_affine, generate_pgw, generate_aux_xml

def log_result(filename, status, reason=""):
    file_exists = os.path.isfile(config.LOG_FILE)
    with open(config.LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Filename', 'Status', 'Reason'])
        writer.writerow([filename, status, reason])

def process_image(image_path, filename):
    try:
        # 2. Pre-processing
        corners, (img_width, img_height) = crop_corners(image_path, filename)
        
        # 3. OCR Extraction
        extracted_text = extract_coordinates(corners)
        
        # 4. Validation
        coords = validate_and_consolidate(extracted_text)
        if not coords:
            log_result(filename, "FAILED", "Invalid or unreasonable coordinates from OCR")
            return
            
        # 5. Calculation
        affine = calculate_affine(
            coords['X_min'], coords['X_max'], 
            coords['Y_min'], coords['Y_max'], 
            img_width, img_height
        )
        
        # 6. Output Generation
        base_name = os.path.splitext(filename)[0]
        pgw_path = os.path.join(config.OUTPUT_DIR, f"{base_name}.pgw")
        xml_path = os.path.join(config.OUTPUT_DIR, f"{base_name}.jpg.aux.xml")
        out_img_path = os.path.join(config.OUTPUT_DIR, filename)
        
        generate_pgw(affine, pgw_path)
        generate_aux_xml(xml_path)
        shutil.copy(image_path, out_img_path)
        
        log_result(filename, "SUCCESS")
        
    except Exception as e:
        log_result(filename, "ERROR", str(e))

def run():
    print("Starting AutoGeoRef Pipeline...")
    files = [f for f in os.listdir(config.INPUT_DIR) if f.lower().endswith('.jpg')]
    
    if not files:
        print("No JPG files found in input directory.")
        return
        
    for idx, filename in enumerate(files, 1):
        print(f"Processing {idx}/{len(files)}: {filename}")
        image_path = os.path.join(config.INPUT_DIR, filename)
        process_image(image_path, filename)
        
    print("Pipeline finished. Check logs for details.")

if __name__ == "__main__":
    run()
