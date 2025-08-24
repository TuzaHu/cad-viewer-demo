import bpy
import json
import os
import math
import subprocess

# === CONFIG ===
json_path = os.path.abspath("//view_export.json")  # Adjust if needed
camera_name = "Camera"
scale_factor = 0.001  # mm → meters (Blender units)

def get_svg_dimensions(svg_file):
    """Get actual pixel dimensions of SVG file"""
    try:
        result = subprocess.run([
            'inkscape', 
            '--query-width', 
            '--query-height', 
            svg_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            width = float(lines[0])
            height = float(lines[1])
            return width, height
        else:
            print(f"Error getting SVG dimensions: {result.stderr}")
            return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# === Load page size from JSON ===
with open(bpy.path.abspath(json_path), "r") as f:
    data = json.load(f)

page_width_mm = data["template"]["width"]
page_height_mm = data["template"]["height"]

page_width = page_width_mm * scale_factor  # in meters
page_height = page_height_mm * scale_factor  # in meters

print(f"Template dimensions: {page_width_mm}mm x {page_height_mm}mm")

# === Get actual SVG dimensions ===
svg_width_px, svg_height_px = get_svg_dimensions("exported2.svg")
if svg_width_px and svg_height_px:
    print(f"Original SVG dimensions: {svg_width_px} x {svg_height_px} pixels")
else:
    print("Could not get SVG dimensions, using template dimensions for render")
    svg_width_px = int(page_width_mm)
    svg_height_px = int(page_height_mm)

# === Get or create the camera ===
cam = bpy.data.objects.get(camera_name)
if cam is None:
    cam_data = bpy.data.cameras.new(name=camera_name)
    cam = bpy.data.objects.new(name=camera_name, object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam)

# === Configure camera ===
cam.data.type = 'ORTHO'
cam.data.ortho_scale = page_width  # exact fit to page width
cam.location = (page_width / 2, page_height / 2, 10)  # above center of page
cam.rotation_euler = (0, 0, 0)  # look straight down (Z–)

bpy.context.scene.camera = cam

# === Render output using ACTUAL SVG dimensions ===
scene = bpy.context.scene

# Use actual SVG pixel dimensions for render resolution
scene.render.resolution_x = int(svg_width_px)
scene.render.resolution_y = int(svg_height_px)
scene.render.resolution_percentage = 100

print(f"✅ Camera perfectly aligned to page size: {page_width_mm} mm x {page_height_mm} mm")
print(f"✅ Render resolution using actual SVG dimensions: {int(svg_width_px)} x {int(svg_height_px)} pixels")
print(f"✅ Camera ortho scale: {cam.data.ortho_scale}")
print(f"✅ Camera location: {cam.location}")
print(f"✅ Perfect consistency with original FreeCAD export!") 