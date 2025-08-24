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

# === Setup Camera for Rendering ===
camera_name = "Camera"

# Get or create camera
cam = bpy.data.objects.get(camera_name)
if cam is None:
    cam_data = bpy.data.cameras.new(name=camera_name)
    cam = bpy.data.objects.new(name=camera_name, object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam)

# Configure camera for technical drawing
cam.data.type = 'ORTHO'
cam.data.ortho_scale = page_width  # Use template width for ortho scale
cam.location = (page_width / 2, page_height / 2, 10)
cam.rotation_euler = (0, 0, 0)  # Look straight down

bpy.context.scene.camera = cam

# === Setup Render Settings with High Resolution ===
scene = bpy.context.scene

# Set render engine to Cycles for best quality
scene.render.engine = 'CYCLES'

# Calculate high resolution while maintaining aspect ratio
# Use 300 DPI equivalent for print quality
dpi = 300
width_pixels = int((page_width_mm * dpi) / 25.4)  # Convert mm to pixels at 300 DPI
height_pixels = int((page_height_mm * dpi) / 25.4)

# Alternative: Use fixed high resolution
# width_pixels = 3508  # A4 landscape at 300 DPI
# height_pixels = 2480  # A4 landscape at 300 DPI

# Ensure minimum resolution
width_pixels = max(width_pixels, 2000)
height_pixels = max(height_pixels, 1400)

scene.render.resolution_x = width_pixels
scene.render.resolution_y = height_pixels
scene.render.resolution_percentage = 100

# Set aspect ratio to match template
scene.render.pixel_aspect_x = 1.0
scene.render.pixel_aspect_y = 1.0

# Set render format and quality
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.compression = 15  # Good quality, reasonable file size

# Set output path
scene.render.filepath = "//technical_drawing_render.png"

# === Setup Lighting for Technical Drawing ===
# Remove existing lights
for obj in bpy.data.objects:
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

# Add area light for even illumination
bpy.ops.object.light_add(type='AREA', location=(page_width / 2, page_height / 2, 20))
light = bpy.context.active_object
light.data.energy = 1000  # Bright light
light.data.size = max(page_width, page_height) * 2  # Large area light
light.data.color = (1, 1, 1)  # White light

# Add second light for better illumination
bpy.ops.object.light_add(type='AREA', location=(page_width / 2, page_height / 2, 15))
light2 = bpy.context.active_object
light2.data.energy = 500  # Secondary light
light2.data.size = max(page_width, page_height) * 1.5
light2.data.color = (1, 1, 1)

# === Setup World Settings ===
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

# Set world background to white
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links

# Clear existing nodes
nodes.clear()

# Create background node
background = nodes.new(type='ShaderNodeBackground')
background.inputs['Color'].default_value = (1, 1, 1, 1)  # White background
background.inputs['Strength'].default_value = 0.5  # Subtle background

# Create output node
output = nodes.new(type='ShaderNodeOutputWorld')

# Connect nodes
links.new(background.outputs['Background'], output.inputs['Surface'])

# === Setup Material for Better Rendering ===
# Find the image plane
image_plane = bpy.data.objects.get("SVG_Image_Plane")
if image_plane and image_plane.data.materials:
    mat = image_plane.data.materials[0]
    if mat.use_nodes:
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Find the image texture node
        tex_image = None
        for node in nodes:
            if node.type == 'TEX_IMAGE':
                tex_image = node
                break
        
        if tex_image and tex_image.image:
            # Set image interpolation to Linear for crisp lines
            tex_image.image.interpolation = 'Linear'
            print(f"✅ Set image interpolation to Linear for crisp lines")

# === Setup Viewport Settings ===
# Set viewport to look through camera
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'CAMERA'
                break

print(f"✅ Camera setup complete")
print(f"✅ Camera ortho scale: {cam.data.ortho_scale}")
print(f"✅ Camera location: {cam.location}")
print(f"✅ Render resolution: {scene.render.resolution_x} x {scene.render.resolution_y}")
print(f"✅ Render format: {scene.render.image_settings.file_format}")
print(f"✅ Output path: {scene.render.filepath}")

# === Render Settings Summary ===
print("\n📋 Render Settings Summary:")
print(f"  - Template dimensions: {page_width_mm}mm x {page_height_mm}mm")
print(f"  - Render resolution: {width_pixels} x {height_pixels} pixels")
print(f"  - DPI equivalent: {dpi}")
print(f"  - Format: PNG with RGBA")
print(f"  - Engine: Cycles")
print(f"  - Camera: Orthographic")
print(f"  - Lighting: Two area lights for even illumination")
print(f"  - Background: White")
print(f"  - Output: technical_drawing_render.png")

print("\n🎯 To render:")
print("  1. Press F12 or go to Render → Render Image")
print("  2. Or use: bpy.ops.render.render(write_still=True)")
print("  3. The render will be saved as 'technical_drawing_render.png'")

# === Optional: Auto-render function ===
def render_technical_drawing():
    """Render the technical drawing with current settings"""
    print("\n🎨 Rendering technical drawing...")
    bpy.ops.render.render(write_still=True)
    print("✅ Render complete! Check 'technical_drawing_render.png'")

# Uncomment the line below to auto-render when script runs
# render_technical_drawing() 