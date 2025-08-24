import bpy
import json
import os

# === CONFIG ===
scale_factor = 0.001  # mm → meters (Blender units)

# === Load page size from JSON ===
json_path = os.path.abspath("//view_export.json")
try:
    with open(bpy.path.abspath(json_path), "r") as f:
        data = json.load(f)
    
    page_width_mm = data["template"]["width"]
    page_height_mm = data["template"]["height"]
    print(f"✅ Loaded dimensions from JSON: {page_width_mm}mm x {page_height_mm}mm")
except Exception as e:
    print(f"❌ Error reading JSON: {e}")
    print("Using default A4 Landscape dimensions...")
    page_width_mm = 297.0
    page_height_mm = 210.0

page_width = page_width_mm * scale_factor  # in meters
page_height = page_height_mm * scale_factor  # in meters

print(f"Template dimensions: {page_width_mm}mm x {page_height_mm}mm")

# === Clear existing objects ===
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# === Create PNG image plane ===
plane_name = "SVG_Image_Plane"

# Create plane
bpy.ops.mesh.primitive_plane_add(
    size=1, 
    enter_editmode=False, 
    align='WORLD', 
    location=(page_width / 2, page_height / 2, 0)
)

plane = bpy.context.active_object
plane.name = plane_name

# Scale plane to match template dimensions
plane.scale.x = page_width
plane.scale.y = page_height

# Apply scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Ensure plane is facing up (Z+ direction)
plane.rotation_euler = (0, 0, 0)

# === Create material with PNG texture ===
mat = bpy.data.materials.new(name="SVG_Image_Material")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create nodes
output = nodes.new(type='ShaderNodeOutputMaterial')
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_image = nodes.new(type='ShaderNodeTexImage')

# Load image - use absolute path
png_path = "/home/tuza/Tapp/exported2.png"
if os.path.exists(png_path):
    tex_image.image = bpy.data.images.load(png_path)
    print(f"✅ Loaded image: {png_path}")
else:
    print(f"❌ Image not found: {png_path}")
    print("Please make sure exported2.png exists in /home/tuza/Tapp/")

# Connect nodes
links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to plane
plane.data.materials.append(mat)

print(f"✅ Created image plane '{plane_name}'")
print(f"✅ Plane location: {plane.location}")
print(f"✅ Plane dimensions: {page_width}m x {page_height}m")
print(f"✅ Plane rotation: {plane.rotation_euler}")

# === Setup camera ===
camera_name = "Camera"

# Get or create camera
cam = bpy.data.objects.get(camera_name)
if cam is None:
    cam_data = bpy.data.cameras.new(name=camera_name)
    cam = bpy.data.objects.new(name=camera_name, object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam)

# Configure camera
cam.data.type = 'ORTHO'
cam.data.ortho_scale = page_width
cam.location = (page_width / 2, page_height / 2, 10)
cam.rotation_euler = (0, 0, 0)

bpy.context.scene.camera = cam

# Set render resolution
scene = bpy.context.scene
scene.render.resolution_x = int(page_width_mm)
scene.render.resolution_y = int(page_height_mm)
scene.render.resolution_percentage = 100

print(f"✅ Camera setup complete")
print(f"✅ Camera ortho scale: {cam.data.ortho_scale}")
print(f"✅ Camera location: {cam.location}")

print("\\n✅ PNG import complete!")
print("📋 You should now see your technical drawing as an image plane")
print("📋 The plane is positioned exactly where your SVG content was")
print(f"📋 Dimensions from JSON: {page_width_mm}mm x {page_height_mm}mm") 