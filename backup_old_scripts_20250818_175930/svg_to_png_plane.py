#!/usr/bin/env python3
"""
Convert SVG to PNG and import as image plane positioned exactly like the reference plane
"""

import subprocess
import sys
import os
import json

def convert_svg_to_png(input_svg, output_png, width_mm=297, height_mm=210):
    """Convert SVG to PNG with exact template dimensions"""
    
    try:
        # Calculate DPI for exact template size
        width_pixels = (width_mm * 300) / 25.4
        height_pixels = (height_mm * 300) / 25.4
        dpi = 300
        
        print(f"Template dimensions: {width_mm}mm x {height_mm}mm")
        print(f"Output dimensions: {int(width_pixels)} x {int(height_pixels)} pixels")
        print(f"DPI: {dpi}")
        
        # Use Inkscape with specific settings
        cmd = [
            'inkscape',
            '--export-type=png',
            f'--export-dpi={dpi}',
            f'--export-filename={output_png}',
            '--export-background=white',
            '--export-background-opacity=1.0',
            '--export-area-page',  # Export entire page area
            input_svg
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Converted {input_svg} to {output_png}")
            return True
        else:
            print(f"✗ Inkscape conversion failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def create_blender_import_script():
    """Create Blender script to import PNG as image plane"""
    
    blender_script = '''
import bpy
import json
import os
import math

# === CONFIG ===
scale_factor = 0.001  # mm → meters (Blender units)

# === Load page size from JSON ===
json_path = os.path.abspath("//view_export.json")
with open(bpy.path.abspath(json_path), "r") as f:
    data = json.load(f)

page_width_mm = data["template"]["width"]
page_height_mm = data["template"]["height"]

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

def create_reference_plane():
    """Create reference plane for comparison"""
    
    plane_name = "SVG_Reference_Plane"
    
    # Remove existing reference plane if it exists
    existing_plane = bpy.data.objects.get(plane_name)
    if existing_plane:
        bpy.data.objects.remove(existing_plane, do_unlink=True)
    
    # Create reference plane
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
    
    # Ensure plane is facing up
    plane.rotation_euler = (0, 0, 0)
    
    # Create material for reference plane
    mat = bpy.data.materials.new(name="SVG_Reference_Material")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Set material properties (semi-transparent for reference)
    principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 0.3)  # Semi-transparent gray
    principled.inputs['Metallic'].default_value = 0.0
    principled.inputs['Roughness'].default_value = 0.5
    
    # Connect nodes
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Set blend mode for transparency
    mat.blend_method = 'BLEND'
    
    # Assign material to plane
    plane.data.materials.append(mat)
    
    print(f"✅ Created reference plane '{plane_name}'")
    print(f"✅ Reference plane location: {plane.location}")

def complete_svg_to_png_workflow(png_path):
    """Complete workflow: Create reference plane and import PNG image plane"""
    
    # Step 1: Create reference plane
    create_reference_plane()
    
    # Step 2: Import PNG as image plane
    import_png_as_image_plane(png_path)
    
    print("\\n✅ Complete SVG to PNG workflow finished!")
    print("✅ PNG image plane is positioned exactly like the reference plane")
    print("✅ Both planes will have the same dimensions and position")

# Usage:
# complete_svg_to_png_workflow("/path/to/exported2.png")
'''
    
    with open('blender_svg_to_png_plane.py', 'w') as f:
        f.write(blender_script)
    
    print("Created blender_svg_to_png_plane.py for PNG import")

if __name__ == "__main__":
    input_svg = "exported2.svg"
    output_png = "exported2.png"
    
    print("=== SVG TO PNG PLANE CONVERTER ===\\n")
    
    # Read template dimensions from view_export.json
    try:
        with open('view_export.json', 'r') as f:
            config = json.load(f)
            template_width = config['template']['width']
            template_height = config['template']['height']
            print(f"Template dimensions: {template_width}mm x {template_height}mm")
    except:
        template_width = 297.0
        template_height = 210.0
        print(f"Using default template dimensions: {template_width}mm x {template_height}mm")
    
    # Convert SVG to PNG
    if convert_svg_to_png(input_svg, output_png, template_width, template_height):
        print("\\n✓ Successfully created PNG!")
        
        # Create Blender import script
        create_blender_import_script()
        
        print("\\n=== PNG PLANE IMPORT GUIDE ===")
        print("1. Use exported2.png in Blender")
        print("2. Run blender_svg_to_png_plane.py for complete workflow")
        print("3. PNG will be positioned exactly like the reference plane")
        print("4. Both planes will have the same dimensions and position")
        
    else:
        print("\\n✗ Conversion failed")
        sys.exit(1) 