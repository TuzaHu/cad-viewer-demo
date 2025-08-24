
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

def import_png_as_image_plane(png_path):
    """Import PNG as image plane positioned exactly like the reference plane"""
    
    plane_name = "SVG_Image_Plane"
    
    # Remove existing image plane if it exists
    existing_plane = bpy.data.objects.get(plane_name)
    if existing_plane:
        bpy.data.objects.remove(existing_plane, do_unlink=True)
    
    # Create plane at exact same position as reference plane
    bpy.ops.mesh.primitive_plane_add(
        size=1, 
        enter_editmode=False, 
        align='WORLD', 
        location=(page_width / 2, page_height / 2, 0)  # Same position as reference plane
    )
    
    plane = bpy.context.active_object
    plane.name = plane_name
    
    # Scale plane to match template dimensions (same as reference plane)
    plane.scale.x = page_width
    plane.scale.y = page_height
    
    # Apply scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Ensure plane is facing up (Z+ direction)
    plane.rotation_euler = (0, 0, 0)
    
    # Create material for the image plane
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
    
    # Load image
    tex_image.image = bpy.data.images.load(png_path)
    
    # Connect nodes
    links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to plane
    plane.data.materials.append(mat)
    
    print(f"✅ Imported PNG as image plane '{plane_name}'")
    print(f"✅ Plane location: {plane.location}")
    print(f"✅ Plane dimensions: {page_width}m x {page_height}m")
    print(f"✅ Plane rotation: {plane.rotation_euler}")
    print(f"✅ Positioned exactly like the reference plane")

def setup_camera_for_png():
    """Setup camera with HIGH RESOLUTION for PNG imports"""
    
    # Template dimensions
    width_m = page_width_mm * scale_factor
    height_m = page_height_mm * scale_factor
    
    # Get or create camera
    camera_name = "Camera"
    cam = bpy.data.objects.get(camera_name)
    if cam is None:
        cam_data = bpy.data.cameras.new(name=camera_name)
        cam = bpy.data.objects.new(name=camera_name, object_data=cam_data)
        bpy.context.scene.collection.objects.link(cam)
    
    # Configure camera
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = width_m  # Use template width
    
    # Position camera above center of template
    cam.location = (width_m / 2, height_m / 2, 10)
    cam.rotation_euler = (0, 0, 0)  # Look straight down
    
    bpy.context.scene.camera = cam
    
    # Set render resolution with HIGH RESOLUTION
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
    
    print(f"✅ Camera setup for PNG: {page_width_mm}mm x {page_height_mm}mm")
    print(f"✅ Camera ortho scale: {cam.data.ortho_scale}")
    print(f"✅ Camera location: {cam.location}")
    print(f"✅ High resolution render: {width_pixels} x {height_pixels} pixels")

def complete_svg_to_png_workflow(png_path):
    """Complete workflow: Import PNG and setup camera with HIGH RESOLUTION"""
    
    # Step 1: Import PNG as image plane
    import_png_as_image_plane(png_path)
    
    # Step 2: Setup camera with high resolution
    setup_camera_for_png()
    
    print("\n✅ Complete SVG to PNG workflow finished!")
    print("✅ PNG image plane is positioned exactly like the reference plane")
    print("✅ Both planes have the same dimensions and position")
    print("✅ High resolution render settings applied")

# Usage:
# complete_svg_to_png_workflow("/path/to/exported2.png")
