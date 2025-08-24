import bpy
import json
import os
import math

# === CONFIG ===
json_path = os.path.abspath("//view_export.json")  # Adjust if needed
camera_name = "Camera"
scale_factor = 0.001  # mm → meters (Blender units)

# === Use ACTUAL RESULT dimensions from user's Result.png ===
actual_width_px = 1488
actual_height_px = 1052

print(f"Using actual result dimensions: {actual_width_px} x {actual_height_px} pixels")

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

# === Render output using ACTUAL RESULT dimensions ===
scene = bpy.context.scene

# Use actual result dimensions for render resolution
scene.render.resolution_x = actual_width_px
scene.render.resolution_y = actual_height_px
scene.render.resolution_percentage = 100

print(f"✅ Camera perfectly aligned to page size: {page_width_mm} mm x {page_height_mm} mm")
print(f"✅ Render resolution using actual result dimensions: {actual_width_px} x {actual_height_px} pixels")
print(f"✅ Camera ortho scale: {cam.data.ortho_scale}")
print(f"✅ Camera location: {cam.location}")
print(f"✅ Perfect consistency with your actual Result.png dimensions!") 