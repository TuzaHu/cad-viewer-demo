import bpy
import json
import os

# === CONFIG ===
scale_factor = 0.001  # mm → meters (Blender units)

# === Read dimensions from dimensions.txt ===
def read_dimensions_from_file():
    """Read dimensions from dimensions.txt file"""
    dimensions_file = "dimensions.txt"
    
    if not os.path.exists(dimensions_file):
        print(f"❌ {dimensions_file} not found!")
        return None, None, None, None
    
    png_width = None
    png_height = None
    svg_width = None
    svg_height = None
    
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
                        svg_width = float(value)
                    elif key == 'TEMPLATE_HEIGHT':
                        svg_height = float(value)
        
        if png_width and png_height and svg_width and svg_height:
            print(f"✅ Read dimensions from {dimensions_file}:")
            print(f"   PNG: {png_width} x {png_height} pixels")
            print(f"   SVG: {svg_width} x {svg_height} mm")
            return png_width, png_height, svg_width, svg_height
        else:
            print(f"❌ Missing dimensions in {dimensions_file}")
            return None, None, None, None
            
    except Exception as e:
        print(f"❌ Error reading {dimensions_file}: {e}")
        return None, None, None, None

# === Read dimensions from dimensions.txt ===
png_width_px, png_height_px, svg_width_mm, svg_height_mm = read_dimensions_from_file()

if png_width_px is None:
    print("❌ Could not read dimensions from dimensions.txt")
    print("Using default dimensions as fallback...")
    # Fallback to default dimensions
    png_width_px = 1488
    png_height_px = 1052
    svg_width_mm = 420.0
    svg_height_mm = 297.0

print(f"Using dimensions:")
print(f"  PNG: {png_width_px} x {png_height_px} pixels")
print(f"  SVG: {svg_width_mm} x {svg_height_mm} mm")

# Convert SVG dimensions to Blender units (using actual SVG dimensions)
page_width = svg_width_mm * scale_factor  # in meters
page_height = svg_height_mm * scale_factor  # in meters

print(f"SVG dimensions in Blender: {page_width}m x {page_height}m")

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

# Scale plane to match actual SVG dimensions
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

# === Setup camera using manual PNG dimensions ===
camera_name = "Camera"

# Get or create camera
cam = bpy.data.objects.get(camera_name)
if cam is None:
    cam_data = bpy.data.cameras.new(name=camera_name)
    cam = bpy.data.objects.new(name=camera_name, object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam)

# Configure camera
cam.data.type = 'ORTHO'
cam.data.ortho_scale = page_width  # Use actual SVG width
cam.location = (page_width / 2, page_height / 2, 10)
cam.rotation_euler = (0, 0, 0)

bpy.context.scene.camera = cam

# Set render resolution using manual PNG dimensions
scene = bpy.context.scene
scene.render.resolution_x = png_width_px
scene.render.resolution_y = png_height_px
scene.render.resolution_percentage = 100

print(f"✅ Camera setup complete")
print(f"✅ Camera ortho scale: {cam.data.ortho_scale}")
print(f"✅ Camera location: {cam.location}")
print(f"✅ Render resolution: {png_width_px} x {png_height_px} pixels")

print("\n✅ PNG import complete!")
print("📋 You should now see your technical drawing as an image plane")
print("📋 The plane is positioned exactly where your SVG content was")
print(f"📋 SVG dimensions: {svg_width_mm}mm x {svg_height_mm}mm")
print(f"📋 PNG dimensions: {png_width_px} x {png_height_px} pixels")
print("📋 Perfect consistency with dimensions.txt!") 