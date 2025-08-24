import bpy
import math

# === CONFIG ===
camera_name = "Camera"
scale_factor = 0.001  # mm → meters (Blender units)

# Default template dimensions (A4 Landscape)
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

print("\\n✅ Camera setup complete!")
print("📋 This script works with both SVG and PNG imports") 