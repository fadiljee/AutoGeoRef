import os
import shutil
from . import config

def calculate_affine(X_min, X_max, Y_min, Y_max, img_width, img_height):
    """
    Calculate 6 affine parameters for .pgw file.
    """
    # Calculate pixel size (resolution)
    pixel_x_size = (X_max - X_min) / img_width
    pixel_y_size = (Y_min - Y_max) / img_height  # Will be negative because Y decreases downwards in map projection
    
    return [
        pixel_x_size,
        0.0,
        0.0,
        pixel_y_size,
        X_min,
        Y_max
    ]

def generate_pgw(affine_params, output_path):
    """
    Write affine parameters to a .pgw file.
    """
    with open(output_path, 'w') as f:
        for param in affine_params:
            f.write(f"{param}\n")
            
def generate_aux_xml(output_path):
    """
    Copy the base XML template to the output path.
    """
    shutil.copy(config.TEMPLATE_XML, output_path)
