import os
import shutil
from . import config

def calculate_affine(X_min, X_max, Y_min, Y_max, img_width, img_height):
    """
    Calculate 6 affine parameters for .pgw world file.
    Returns: [pixel_x_size, rotation_x, rotation_y, pixel_y_size, X_upper_left, Y_upper_left]
    """
    pixel_x_size =  (X_max - X_min) / img_width
    pixel_y_size = -(Y_max - Y_min) / img_height  # negative: Y decreases downward

    return [
        pixel_x_size,   # A: pixel size X
        0.0,            # B: rotation (always 0 for north-up maps)
        0.0,            # C: rotation (always 0)
        pixel_y_size,   # D: pixel size Y (negative)
        X_min,          # E: X coordinate of upper-left pixel center
        Y_max           # F: Y coordinate of upper-left pixel center
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

def generate_aux_xml(filename, X_min, X_max, Y_min, Y_max, output_dir):
    """
    Generate a .aux.xml georeferencing metadata file alongside the image.
    """
    base = os.path.splitext(filename)[0]
    xml_path = os.path.join(output_dir, filename + ".aux.xml")

    xml_content = f"""<PAMDataset>
  <SRS dataAxisToSRSAxisMapping="2,1">GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]</SRS>
  <GeoTransform> {X_min:.10f},  {(X_max-X_min)/1:.10f},  0,  {Y_max:.10f},  0, -{(Y_max-Y_min)/1:.10f}</GeoTransform>
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
