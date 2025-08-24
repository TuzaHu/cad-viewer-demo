import bpy
import json
import os
import math

def read_dimensions_from_file():
    """Read dimensions from dimensions.txt file"""
    dimensions_file = "dimensions.txt"
    
    if not os.path.exists(dimensions_file):
        print(f"❌ {dimensions_file} not found!")
        print("Please create dimensions.txt with your desired dimensions")
        return None, None, None, None
    
    png_width = None
    png_height = None
    template_width = None
    template_height = None
    
    try:
        with open(dimensions_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'PNG_WIDTH':
                        png_width = int(value)
                    elif key == 'PNG_HEIGHT':
                        png_height = int(value)
                    elif key == 'TEMPLATE_WIDTH':
                        template_width = float(value)
                    elif key == 'TEMPLATE_HEIGHT':
                        template_height = float(value)
        
        if png_width and png_height and template_width and template_height:
            print(f"✅ Read dimensions from {dimensions_file}:")
            print(f"   PNG: {png_width} x {png_height} pixels")
            print(f"   Template: {template_width} x {template_height} mm")
            return png_width, png_height, template_width, template_height
        else:
            print(f"❌ Missing dimensions in {dimensions_file}")
            return None, None, None, None
            
    except Exception as e:
        print(f"❌ Error reading {dimensions_file}: {e}")
        return None, None, None, None

# === CONFIG ===
camera_name = "Camera"
scale_factor = 0.001  # mm → meters (Blender units)

# === Read manual dimensions ===
png_width, png_height, template_width, template_height = read_dimensions_from_file()

if png_width is None:
    print("❌ Could not read dimensions, exiting...")
    exit()

# Convert template dimensions to Blender units
page_width = template_width * scale_factor  # in meters
page_height = template_height * scale_factor  # in meters

print(f"Template dimensions: {template_width}mm x {template_height}mm")

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

# === Render output using MANUAL dimensions ===
scene = bpy.context.scene

# Use manual dimensions for render resolution
scene.render.resolution_x = png_width
scene.render.resolution_y = png_height
scene.render.resolution_percentage = 100

print(f"✅ Camera perfectly aligned to page size: {template_width} mm x {template_height} mm")
print(f"✅ Render resolution using manual dimensions: {png_width} x {png_height} pixels")
print(f"✅ Camera ortho scale: {cam.data.ortho_scale}")
print(f"✅ Camera location: {cam.location}")
print(f"✅ Perfect consistency with dimensions.txt!") 