import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_DIR = os.path.join(PROJECT_ROOT, "data", "1_input_raw")
TEMP_DIR = os.path.join(PROJECT_ROOT, "data", "2_temp_crop_debug")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "3_output_ready")
TEMPLATE_XML = os.path.join(PROJECT_ROOT, "templates", "base_aux.xml")
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "processing_report.csv")

# Map corners dimensions to crop (adjust as necessary)
CROP_WIDTH = 400
CROP_HEIGHT = 150

# Valid coordinates bounds for Bangka Belitung
VALID_X_MIN = 105.0
VALID_X_MAX = 108.0
VALID_Y_MIN = -3.5
VALID_Y_MAX = -1.5
