import os
from PIL import Image
import subprocess

def convert_to_svg(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for fname in os.listdir(input_dir):
        if not fname.lower().endswith(".png"):
            continue

        input_path = os.path.join(input_dir, fname)
        bmp_path   = input_path.replace(".png", ".bmp")
        svg_path   = os.path.join(output_dir, fname.replace(".png", ".svg"))

        # המרה ל־BMP לצורך potrace
        img = Image.open(input_path).convert("1")
        img.save(bmp_path)

        subprocess.run(["potrace", bmp_path, "-s", "-o", svg_path])
        print(f"✅ SVG: {fname} → {svg_path}")

        os.remove(bmp_path)
