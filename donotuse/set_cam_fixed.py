import bpy
import json
import os
import math

# === CONFIG ===
camera_name = "Camera"
scale_factor = 0.001  # mm → meters (Blender units)

# === Try multiple paths for the JSON file ===
possible_paths = [
    os.path.abspath("//view_export.json"),  # Relative to blend file
    "view_export.json",  # Current directory
    os.path.join(os.getcwd(), "view_export.json"),  # Absolute path
    "/home/tuza/Tapp/view_export.json"  # Full path
]

json_path = None
for path in possible_paths:
    if os.path.exists(path):
        json_path = path
        break

if json_path is None:
    print("❌ Could not find view_export.json")
    print("Available paths tried:")
    for path in possible_paths:
        print(f"  - {path}")
    print("\\nUsing default template dimensions...")
    
    # Use default dimensions (A4 Landscape)
    page_width_mm = 297.0
    page_height_mm = 210.0
else:
    print(f"✅ Found view_export.json at: {json_path}")
    
    # === Load page size from JSON ===
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
        
        page_width_mm = data["template"]["width"]
        page_height_mm = data["template"]["height"]
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        print("Using default template dimensions...")
        page_width_mm = 297.0
        page_height_mm = 210.0

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

# === Render output should match page aspect ratio ===
scene = bpy.context.scene
scene.render.resolution_x = int(page_width_mm)
scene.render.resolution_y = int(page_height_mm)
scene.render.resolution_percentage = 100

print(f"✅ Camera perfectly aligned to page size: {page_width_mm} mm x {page_height_mm} mm")
print(f"✅ Camera ortho scale: {cam.data.ortho_scale}")
print(f"✅ Camera location: {cam.location}")
print(f"✅ Render resolution: {scene.render.resolution_x} x {scene.render.resolution_y}") 