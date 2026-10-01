import os
import csv
import shutil
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import config
from src.module_geo_calc import calculate_affine, generate_pgw, copy_image_to_output
from src.module_geo_calc import generate_aux_xml

INPUT_DIR   = config.INPUT_DIR
OUTPUT_DIR  = config.OUTPUT_DIR
LOG_DIR     = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE    = os.path.join(LOG_DIR, "processing_report.csv")
MANUAL_CSV  = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "manual_coords.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def log_result(filename, status, message=""):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([filename, status, message])

def run():
    # Write CSV header (overwrite each run)
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "status", "message"])

    # Load manual coordinates
    if not os.path.exists(MANUAL_CSV):
        print(f"ERROR: File koordinat manual tidak ditemukan: {MANUAL_CSV}")
        return

    with open(MANUAL_CSV, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    print(f"Memproses {total} file dari koordinat manual...\n")

    for i, row in enumerate(rows, 1):
        filename = row["filename"].strip()
        print(f"Processing {i}/{total}: {filename}")

        try:
            X_min = row.get("X_min", "").strip()
            X_max = row.get("X_max", "").strip()
            Y_min = row.get("Y_min", "").strip()
            Y_max = row.get("Y_max", "").strip()

            if not all([X_min, X_max, Y_min, Y_max]):
                log_result(filename, "SKIP", "Koordinat belum diisi")
                print(f"  -> SKIP: Koordinat belum diisi\n")
                continue

            X_min = float(X_min)
            X_max = float(X_max)
            Y_min = float(Y_min)
            Y_max = float(Y_max)

            # Read image for dimensions
            import cv2
            image_path = os.path.join(INPUT_DIR, filename)
            img = cv2.imread(image_path)
            if img is None:
                log_result(filename, "ERROR", f"Tidak bisa membaca gambar: {filename}")
                print(f"  -> ERROR: Tidak bisa membaca gambar\n")
                continue

            img_height, img_width = img.shape[:2]

            # Generate georef outputs
            affine = calculate_affine(X_min, X_max, Y_min, Y_max, img_width, img_height)
            generate_pgw(filename, affine, OUTPUT_DIR)
            generate_aux_xml(filename, X_min, X_max, Y_min, Y_max, OUTPUT_DIR)
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
