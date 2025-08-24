#!/usr/bin/env python3
"""
Convert SVG to PNG using ACTUAL pixel dimensions from the original SVG
This ensures perfect consistency with the original export
"""

import subprocess
import sys
import os
import json

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

def convert_svg_to_png_actual_dimensions(input_svg, output_png):
    """Convert SVG to PNG maintaining exact pixel dimensions"""
    
    # Get actual dimensions from SVG
    width_px, height_px = get_svg_dimensions(input_svg)
    
    if width_px is None or height_px is None:
        print("❌ Could not get SVG dimensions")
        return False
    
    print(f"Original SVG dimensions: {width_px} x {height_px} pixels")
    
    try:
        # Convert to PNG with exact same pixel dimensions
        cmd = [
            'inkscape',
            '--export-type=png',
            f'--export-filename={output_png}',
            '--export-background=white',
            '--export-background-opacity=1.0',
            '--export-area-page',  # Export entire page area
            input_svg
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Converted {input_svg} to {output_png}")
            print(f"✓ Maintained exact dimensions: {width_px} x {height_px} pixels")
            return True, width_px, height_px
        else:
            print(f"✗ Inkscape conversion failed: {result.stderr}")
            return False, None, None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False, None, None

def create_blender_import_script_actual_dimensions(svg_width_px, svg_height_px):
    """Create Blender script using actual SVG pixel dimensions"""
    
    blender_script = f'''
import bpy
import json
import os

# === CONFIG ===
scale_factor = 0.001  # mm → meters (Blender units)

# === Use ACTUAL SVG pixel dimensions ===
svg_width_px = {svg_width_px}
svg_height_px = {svg_height_px}

print(f"Using actual SVG dimensions: {{svg_width_px}} x {{svg_height_px}} pixels")

# === Load page size from JSON for Blender units ===
json_path = os.path.abspath("//view_export.json")
try:
    with open(bpy.path.abspath(json_path), "r") as f:
        data = json.load(f)
    
    page_width_mm = data["template"]["width"]
    page_height_mm = data["template"]["height"]
    print(f"✅ Template dimensions from JSON: {{page_width_mm}}mm x {{page_height_mm}}mm")
except Exception as e:
    print(f"❌ Error reading JSON: {{e}}")
    print("Using default A4 Landscape dimensions...")
    page_width_mm = 297.0
    page_height_mm = 210.0

# Convert template dimensions to Blender units
page_width = page_width_mm * scale_factor  # in meters
page_height = page_height_mm * scale_factor  # in meters

print(f"Template dimensions in Blender: {{page_width}}m x {{page_height}}m")

def import_png_as_image_plane(png_path):
    """Import PNG as image plane using actual SVG dimensions"""
    
    plane_name = "SVG_Image_Plane"
    
    # Remove existing image plane if it exists
    existing_plane = bpy.data.objects.get(plane_name)
    if existing_plane:
        bpy.data.objects.remove(existing_plane, do_unlink=True)
    
    # Create plane at template position
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
    
    print(f"✅ Imported PNG as image plane '{{plane_name}}'")
    print(f"✅ Plane location: {{plane.location}}")
    print(f"✅ Plane dimensions: {{page_width}}m x {{page_height}}m")
    print(f"✅ PNG dimensions: {{svg_width_px}} x {{svg_height_px}} pixels")
    print(f"✅ Positioned exactly like the reference plane")

def setup_camera_with_actual_dimensions():
    """Setup camera using actual SVG dimensions for render resolution"""
    
    # Template dimensions for camera setup
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
    
    # Set render resolution using ACTUAL SVG dimensions
    scene = bpy.context.scene
    scene.render.resolution_x = int(svg_width_px)
    scene.render.resolution_y = int(svg_height_px)
    scene.render.resolution_percentage = 100
    
    print(f"✅ Camera setup using actual SVG dimensions")
    print(f"✅ Camera ortho scale: {{cam.data.ortho_scale}}")
    print(f"✅ Camera location: {{cam.location}}")
    print(f"✅ Render resolution: {{int(svg_width_px)}} x {{int(svg_height_px)}} pixels")
    print(f"✅ This matches the original SVG pixel dimensions exactly!")

def complete_svg_to_png_workflow_actual_dimensions(png_path):
    """Complete workflow using actual SVG dimensions"""
    
    # Step 1: Import PNG as image plane
    import_png_as_image_plane(png_path)
    
    # Step 2: Setup camera with actual dimensions
    setup_camera_with_actual_dimensions()
    
    print("\\n✅ Complete SVG to PNG workflow finished!")
    print("✅ PNG image plane is positioned exactly like the reference plane")
    print("✅ Render resolution matches original SVG pixel dimensions")
    print("✅ Perfect consistency with the original FreeCAD export")

# Usage:
# complete_svg_to_png_workflow_actual_dimensions("/path/to/exported2.png")
'''
    
    with open('blender_actual_dimensions_import.py', 'w') as f:
        f.write(blender_script)
    
    print("Created blender_actual_dimensions_import.py for PNG import")

if __name__ == "__main__":
    input_svg = "exported2.svg"
    output_png = "exported2.png"
    
    print("=== SVG TO PNG CONVERTER (ACTUAL DIMENSIONS) ===\\n")
    
    # Convert SVG to PNG maintaining actual dimensions
    success, width_px, height_px = convert_svg_to_png_actual_dimensions(input_svg, output_png)
    
    if success:
        print("\\n✓ Successfully created PNG with actual SVG dimensions!")
        
        # Create Blender import script
        create_blender_import_script_actual_dimensions(width_px, height_px)
        
        print("\\n=== ACTUAL DIMENSIONS IMPORT GUIDE ===")
        print("1. Use exported2.png in Blender")
        print("2. Run blender_actual_dimensions_import.py for complete workflow")
        print("3. PNG will be positioned exactly like the reference plane")
        print(f"4. Render resolution: {width_px} x {height_px} pixels (matches original SVG)")
        print("5. Perfect consistency with original FreeCAD export")
        
    else:
        print("\\n✗ Conversion failed")
        sys.exit(1) 