import os
import csv
import shutil
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import config
from src.module_ocr import crop_corners, extract_coordinates, validate_and_consolidate
from src.module_geo_calc import calculate_affine, generate_pgw, copy_image_to_output, get_neatline_bounds
from src.module_geo_calc import generate_aux_xml

INPUT_DIR   = config.INPUT_DIR
OUTPUT_DIR  = config.OUTPUT_DIR
LOG_DIR     = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE    = os.path.join(LOG_DIR, "processing_report.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(config.TEMP_DIR, exist_ok=True)

def log_result(filename, status, message=""):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([filename, status, message])

def run():
    # Write CSV header (overwrite each run)
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "status", "message"])

    if not os.path.exists(INPUT_DIR):
        print(f"ERROR: Folder {INPUT_DIR} tidak ditemukan")
        return

    # Batch processing from INPUT_DIR
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".jpg")]
    total = len(files)
    
    if total == 0:
        print(f"Tidak ada file JPG di folder {INPUT_DIR}")
        return

    print(f"Memproses {total} file gambar...\n")

    for i, filename in enumerate(files, 1):
        print(f"Processing {i}/{total}: {filename}")
        image_path = os.path.join(INPUT_DIR, filename)

        try:
            # 1. Crop corners
            corners, dim = crop_corners(image_path, filename)
            
            # 2. Extract OCR
            extracted = extract_coordinates(corners)
            
            # 3. Validate & Consolidate
            coords = validate_and_consolidate(extracted)
            
            if not coords:
                log_result(filename, "ERROR", "OCR gagal mengekstrak koordinat valid")
                print(f"  -> ERROR: OCR gagal mengekstrak koordinat valid\n")
                continue
                
            X_min = coords['X_min']
            X_max = coords['X_max']
            Y_min = coords['Y_min']
            Y_max = coords['Y_max']

            # Detect inner map bounds (neatline)
            neatline_bounds = get_neatline_bounds(image_path)
            nx, ny, nw, nh = neatline_bounds
            print(f"  -> Neatline Detected: x={nx}, y={ny}, w={nw}, h={nh}")

            # Generate georef outputs
            affine = calculate_affine(X_min, X_max, Y_min, Y_max, neatline_bounds)
            generate_pgw(filename, affine, OUTPUT_DIR)
            generate_aux_xml(filename, affine, OUTPUT_DIR)
            copy_image_to_output(image_path, filename, OUTPUT_DIR)

            log_result(filename, "SUCCESS", f"X:[{X_min},{X_max}] Y:[{Y_min},{Y_max}]")
            print(f"  -> SUCCESS: X:[{X_min},{X_max}] Y:[{Y_min},{Y_max}]\n")

        except Exception as e:
            import traceback
            log_result(filename, "ERROR", str(e))
            print(f"  -> ERROR: {e}\n")

    print("Selesai! Cek folder data/3_output_ready/ dan logs/processing_report.csv")

if __name__ == "__main__":
    run()
