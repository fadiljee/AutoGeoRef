import os
import csv
import json

geojson_path = 'data/1_input_raw/051_Parittiga_Final SLS.geojson'
csv_path = 'data/manual_coords.csv'
input_dir = 'data/1_input_raw'

with open(geojson_path, 'r') as f:
    data = json.load(f)

# Build a mapping from the last 6 digits of idsubsls to its bounding box
mapping = {}
for feature in data.get('features', []):
    props = feature.get('properties', {})
    idsubsls = props.get('idsubsls')
    if not idsubsls:
        continue
    
    suffix = str(idsubsls)[-6:]
    
    geom = feature.get('geometry')
    if not geom:
        continue
        
    coords = geom.get('coordinates', [])
    
    # Flatten the coordinates to find min/max
    def flatten(coords_list):
        flat = []
        for item in coords_list:
            if isinstance(item, list) and len(item) == 2 and isinstance(item[0], (int, float)):
                flat.append(item)
            elif isinstance(item, list):
                flat.extend(flatten(item))
        return flat
    
    flat_coords = flatten(coords)
    if not flat_coords:
        continue
        
    x_coords = [c[0] for c in flat_coords]
    y_coords = [c[1] for c in flat_coords]
    
    mapping[suffix] = {
        'X_min': min(x_coords),
        'X_max': max(x_coords),
        'Y_min': min(y_coords),
        'Y_max': max(y_coords)
    }

# Now read all images and write to CSV
images = [f for f in os.listdir(input_dir) if f.endswith('.jpg')]

with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "X_min", "X_max", "Y_min", "Y_max"])
    
    for img in sorted(images):
        # Extract the last 6 digits before _WSS.jpg
        # Format is typically XXXXXXXXXX000400_WSS.jpg
        base = img.replace('_WSS.jpg', '')
        if len(base) >= 6:
            suffix = base[-6:]
            if suffix in mapping:
                b = mapping[suffix]
                writer.writerow([img, b['X_min'], b['X_max'], b['Y_min'], b['Y_max']])
                print(f"Matched {img} to geojson suffix {suffix}")
            else:
                writer.writerow([img, "", "", "", ""])
                print(f"No match for {img} (suffix {suffix})")
        else:
            writer.writerow([img, "", "", "", ""])

print("CSV filled.")
