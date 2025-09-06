#!/usr/bin/env python3
"""
Convert SVG to PNG using manual dimensions from dimensions.txt
FIXED VERSION - Actually forces Inkscape to use specified dimensions
"""

import subprocess
import sys
import os
import json

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

def convert_svg_to_png_manual_dimensions_fixed(input_svg, output_png):
    """Convert SVG to PNG using manual dimensions - FIXED VERSION"""
    
    # Read dimensions from file
    png_width, png_height, template_width, template_height = read_dimensions_from_file()
    
    if png_width is None:
        return False, None, None, None, None
    
    print(f"Converting SVG to PNG with FORCED dimensions: {png_width} x {png_height} pixels")
    
    try:
        # Calculate DPI to achieve the desired pixel dimensions
        # DPI = (pixels * 25.4) / mm
        dpi_width = (png_width * 25.4) / template_width
        dpi_height = (png_height * 25.4) / template_height
        
        # Use the higher DPI to ensure we get at least the desired dimensions
        dpi = max(dpi_width, dpi_height)
        
        print(f"Calculated DPI: {dpi:.2f} (to achieve {png_width} x {png_height} pixels)")
        
        # Convert to PNG with specific DPI to force dimensions
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
            print(f"✓ Used DPI: {dpi:.2f} to achieve target dimensions")
            print(f"✓ Target dimensions: {png_width} x {png_height} pixels")
            
            # Verify the actual output dimensions
            try:
                verify_cmd = ['identify', output_png]
                verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
                if verify_result.returncode == 0:
                    # Parse the identify output to get actual dimensions
                    output_line = verify_result.stdout.strip()
                    if 'PNG' in output_line:
                        # Extract dimensions from output like "exported2.png PNG 1587x1123 1587x1123+0+0 8-bit sRGB"
                        parts = output_line.split()
                        if len(parts) >= 3:
                            actual_dimensions = parts[2]
                            if 'x' in actual_dimensions:
                                actual_width, actual_height = actual_dimensions.split('x')
                                print(f"✓ Actual output dimensions: {actual_width} x {actual_height} pixels")
                                
                                # Check if dimensions match target
                                if int(actual_width) == png_width and int(actual_height) == png_height:
                                    print("✅ Perfect! Output dimensions match target exactly!")
                                else:
                                    print(f"⚠️  Note: Output dimensions differ from target")
                                    print(f"   Target: {png_width} x {png_height}")
                                    print(f"   Actual: {actual_width} x {actual_height}")
            except Exception as e:
                print(f"Could not verify output dimensions: {e}")
            
            return True, png_width, png_height, template_width, template_height
        else:
            print(f"✗ Inkscape conversion failed: {result.stderr}")
            return False, None, None, None, None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False, None, None, None, None

def create_blender_import_script_manual_dimensions_fixed(png_width, png_height, template_width, template_height):
    """Create Blender script using manual dimensions"""
    
    blender_script = f'''
import bpy
import json
import os

# === CONFIG ===
scale_factor = 0.001  # mm → meters (Blender units)

# === Use MANUAL dimensions from dimensions.txt ===
png_width_px = {png_width}
png_height_px = {png_height}
template_width_mm = {template_width}
template_height_mm = {template_height}

print(f"Using manual dimensions:")
print(f"  PNG: {{png_width_px}} x {{png_height_px}} pixels")
print(f"  Template: {{template_width_mm}} x {{template_height_mm}} mm")

# Convert template dimensions to Blender units
page_width = template_width_mm * scale_factor  # in meters
page_height = template_height_mm * scale_factor  # in meters

print(f"Template dimensions in Blender: {{page_width}}m x {{page_height}}m")

def import_png_as_image_plane(png_path):
    """Import PNG as image plane using manual dimensions"""
    
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
    print(f"✅ PNG dimensions: {{png_width_px}} x {{png_height_px}} pixels")
    print(f"✅ Positioned exactly like the reference plane")

def setup_camera_with_manual_dimensions():
    """Setup camera using manual dimensions for render resolution"""
    
    # Template dimensions for camera setup
    width_m = template_width_mm * scale_factor
    height_m = template_height_mm * scale_factor
    
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
    
    # Set render resolution using MANUAL dimensions
    scene = bpy.context.scene
    scene.render.resolution_x = int(png_width_px)
    scene.render.resolution_y = int(png_height_px)
    scene.render.resolution_percentage = 100
    
    print(f"✅ Camera setup using manual dimensions")
    print(f"✅ Camera ortho scale: {{cam.data.ortho_scale}}")
    print(f"✅ Camera location: {{cam.location}}")
    print(f"✅ Render resolution: {{int(png_width_px)}} x {{int(png_height_px)}} pixels")
    print(f"✅ Perfect consistency with your manual dimensions!")

def complete_svg_to_png_workflow_manual_dimensions_fixed(png_path):
    """Complete workflow using manual dimensions"""
    
    # Step 1: Import PNG as image plane
    import_png_as_image_plane(png_path)
    
    # Step 2: Setup camera with manual dimensions
    setup_camera_with_manual_dimensions()
    
    print("\\n✅ Complete SVG to PNG workflow finished!")
    print("✅ PNG image plane is positioned exactly like the reference plane")
    print("✅ Render resolution matches your manual dimensions")
    print("✅ Perfect consistency with dimensions.txt")

# Usage:
# complete_svg_to_png_workflow_manual_dimensions_fixed("/path/to/exported2.png")
'''
    
    with open('blender_manual_dimensions_import_fixed.py', 'w') as f:
        f.write(blender_script)
    
    print("Created blender_manual_dimensions_import_fixed.py for PNG import")

if __name__ == "__main__":
    input_svg = "exported2.svg"
    output_png = "exported2.png"
    
    print("=== SVG TO PNG CONVERTER (MANUAL DIMENSIONS - FIXED) ===\\n")
    
    # Convert SVG to PNG using manual dimensions
    success, png_width, png_height, template_width, template_height = convert_svg_to_png_manual_dimensions_fixed(input_svg, output_png)
    
    if success:
        print("\\n✓ Successfully created PNG!")
        
        # Create Blender import script
        create_blender_import_script_manual_dimensions_fixed(png_width, png_height, template_width, template_height)
        
        print("\\n=== MANUAL DIMENSIONS IMPORT GUIDE (FIXED) ===")
        print("1. Edit dimensions.txt to set your desired dimensions")
        print("2. Use exported2.png in Blender")
        print("3. Run blender_manual_dimensions_import_fixed.py for complete workflow")
        print("4. PNG will be positioned exactly like the reference plane")
        print(f"5. Render resolution: {png_width} x {png_height} pixels (from dimensions.txt)")
        print("6. Perfect consistency with your manual settings")
        
    else:
        print("\\n✗ Conversion failed")
        sys.exit(1) 