import bpy
import json
import os
import math

# === CONFIG ===
json_path = os.path.abspath("//view_export.json")  # Adjust if needed
camera_name = "Camera"
scale_factor = 0.001  # mm → meters (Blender units)

# === Load page size from JSON ===
with open(bpy.path.abspath(json_path), "r") as f:
    data = json.load(f)

page_width_mm = data["template"]["width"]
page_height_mm = data["template"]["height"]

page_width = page_width_mm * scale_factor  # in meters
page_height = page_height_mm * scale_factor  # in meters

print(f"Template dimensions: {page_width_mm}mm x {page_height_mm}mm")

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

# === Render output with HIGH RESOLUTION ===
scene = bpy.context.scene

# Calculate high resolution while maintaining aspect ratio
# Use 300 DPI equivalent for print quality
dpi = 300
width_pixels = int((page_width_mm * dpi) / 25.4)  # Convert mm to pixels at 300 DPI
height_pixels = int((page_height_mm * dpi) / 25.4)

# Ensure minimum resolution
width_pixels = max(width_pixels, 2000)
height_pixels = max(height_pixels, 1400)

scene.render.resolution_x = width_pixels
scene.render.resolution_y = height_pixels
scene.render.resolution_percentage = 100

print(f"✅ Camera perfectly aligned to page size: {page_width_mm} mm x {page_height_mm} mm")
print(f"✅ High resolution render: {width_pixels} x {height_pixels} pixels")
print(f"✅ Camera ortho scale: {cam.data.ortho_scale}")
print(f"✅ Camera location: {cam.location}") 