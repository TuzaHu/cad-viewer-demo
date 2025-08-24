#!/usr/bin/env python3
"""
Convert SVG to PNG while preserving exact size and appearance
"""

import subprocess
import sys
import os

def check_inkscape():
    """Check if Inkscape is installed"""
    try:
        result = subprocess.run(['inkscape', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_rsvg_convert():
    """Check if rsvg-convert is installed"""
    try:
        result = subprocess.run(['rsvg-convert', '--version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def convert_svg_to_png_inkscape(input_svg, output_png, dpi=300):
    """Convert SVG to PNG using Inkscape"""
    try:
        # Get SVG dimensions
        cmd = [
            'inkscape', 
            '--export-type=png',
            f'--export-dpi={dpi}',
            f'--export-filename={output_png}',
            input_svg
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Converted {input_svg} to {output_png} using Inkscape")
            return True
        else:
            print(f"✗ Inkscape conversion failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error with Inkscape: {e}")
        return False

def convert_svg_to_png_rsvg(input_svg, output_png, dpi=300):
    """Convert SVG to PNG using rsvg-convert"""
    try:
        cmd = [
            'rsvg-convert',
            '-d', str(dpi),
            '-o', output_png,
            input_svg
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Converted {input_svg} to {output_png} using rsvg-convert")
            return True
        else:
            print(f"✗ rsvg-convert conversion failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Error with rsvg-convert: {e}")
        return False

def convert_svg_to_png_cairosvg(input_svg, output_png, dpi=300):
    """Convert SVG to PNG using cairosvg (Python library)"""
    try:
        import cairosvg
        
        # Convert SVG to PNG
        cairosvg.svg2png(url=input_svg, write_to=output_png, dpi=dpi)
        print(f"✓ Converted {input_svg} to {output_png} using cairosvg")
        return True
        
    except ImportError:
        print("✗ cairosvg not installed. Install with: pip install cairosvg")
        return False
    except Exception as e:
        print(f"✗ Error with cairosvg: {e}")
        return False

def install_cairosvg():
    """Install cairosvg if not available"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'cairosvg'], 
                      check=True, capture_output=True)
        print("✓ cairosvg installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install cairosvg: {e}")
        return False

def convert_svg_to_png(input_svg, output_png, dpi=300):
    """Convert SVG to PNG using available tools"""
    
    print(f"Converting {input_svg} to {output_png}...")
    print(f"DPI: {dpi}")
    
    # Try different conversion methods
    methods = [
        ("Inkscape", convert_svg_to_png_inkscape),
        ("rsvg-convert", convert_svg_to_png_rsvg),
        ("cairosvg", convert_svg_to_png_cairosvg)
    ]
    
    for method_name, method_func in methods:
        print(f"\nTrying {method_name}...")
        
        if method_name == "Inkscape" and not check_inkscape():
            print(f"✗ {method_name} not available")
            continue
            
        if method_name == "rsvg-convert" and not check_rsvg_convert():
            print(f"✗ {method_name} not available")
            continue
            
        if method_name == "cairosvg":
            try:
                import cairosvg
            except ImportError:
                print("Installing cairosvg...")
                if install_cairosvg():
                    try:
                        import cairosvg
                    except ImportError:
                        print(f"✗ {method_name} not available")
                        continue
                else:
                    print(f"✗ {method_name} not available")
                    continue
        
        if method_func(input_svg, output_png, dpi):
            return True
    
    print("\n✗ All conversion methods failed")
    return False

def create_blender_import_script():
    """Create a Blender script for importing PNG as image plane"""
    
    blender_script = '''
import bpy
import bmesh
from mathutils import Vector

def import_png_as_image_plane(png_path, scale_factor=0.001):
    """Import PNG as image plane in Blender"""
    
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Add a plane
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    plane = bpy.context.active_object
    
    # Create material
    mat = bpy.data.materials.new(name="ImageMaterial")
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
    
    # Scale the plane to match image aspect ratio
    if tex_image.image:
        width, height = tex_image.image.size
        aspect_ratio = width / height
        plane.scale.x = aspect_ratio
        plane.scale.y = 1
    
    # Apply scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Scale to desired size
    plane.scale = (scale_factor, scale_factor, scale_factor)
    
    print(f"Imported {png_path} as image plane")

# Usage:
# import_png_as_image_plane("/path/to/your/exported2.png", 0.001)
'''
    
    with open('blender_png_import.py', 'w') as f:
        f.write(blender_script)
    
    print("Created blender_png_import.py for PNG import")

if __name__ == "__main__":
    input_svg = "exported2.svg"
    output_png = "exported2.png"
    
    # Try different DPI settings for better quality
    dpi_options = [300, 600, 900]
    
    print("=== SVG TO PNG CONVERTER ===\n")
    
    for dpi in dpi_options:
        output_file = f"exported2_{dpi}dpi.png"
        print(f"\nConverting with {dpi} DPI...")
        
        if convert_svg_to_png(input_svg, output_file, dpi):
            print(f"\n✓ Successfully created {output_file}")
            break
    else:
        print("\n✗ All conversion attempts failed")
        sys.exit(1)
    
    # Create Blender import script
    create_blender_import_script()
    
    print("\n=== PNG IMPORT GUIDE ===")
    print("1. Use the created PNG file in Blender")
    print("2. Import as image plane using blender_png_import.py")
    print("3. Or manually add image texture to a plane")
    print("4. Scale as needed for your project")
    print("\nThe PNG will preserve all dashed lines and styling!") 