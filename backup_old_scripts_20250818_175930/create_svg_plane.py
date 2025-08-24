import bpy
import json
import os
import math

# === CONFIG ===
camera_name = "Camera"
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

# === Create plane at SVG position ===
# The plane should be positioned exactly where the SVG content is
# Based on the camera setup, the SVG content is centered at (page_width/2, page_height/2, 0)

plane_name = "SVG_Reference_Plane"

# Remove existing plane if it exists
existing_plane = bpy.data.objects.get(plane_name)
if existing_plane:
    bpy.data.objects.remove(existing_plane, do_unlink=True)

# Create plane
bpy.ops.mesh.primitive_plane_add(
    size=1, 
    enter_editmode=False, 
    align='WORLD', 
    location=(page_width / 2, page_height / 2, 0)  # Same position as SVG content
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

# Create material for the plane
mat = bpy.data.materials.new(name="SVG_Reference_Material")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create nodes
output = nodes.new(type='ShaderNodeOutputMaterial')
principled = nodes.new(type='ShaderNodeBsdfPrincipled')

# Set material properties
principled.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)  # Light gray
principled.inputs['Metallic'].default_value = 0.0
principled.inputs['Roughness'].default_value = 0.5

# Connect nodes
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to plane
plane.data.materials.append(mat)

print(f"✅ Created plane '{plane_name}' at SVG position")
print(f"✅ Plane location: {plane.location}")
print(f"✅ Plane dimensions: {page_width}m x {page_height}m")
print(f"✅ Plane rotation: {plane.rotation_euler}")

# === Optional: Create a reference frame ===
def create_reference_frame():
    """Create a reference frame to show the SVG boundaries"""
    
    frame_name = "SVG_Reference_Frame"
    
    # Remove existing frame if it exists
    existing_frame = bpy.data.objects.get(frame_name)
    if existing_frame:
        bpy.data.objects.remove(existing_frame, do_unlink=True)
    
    # Create edges to show the frame
    mesh = bpy.data.meshes.new(frame_name)
    obj = bpy.data.objects.new(frame_name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    # Create vertices for the frame
    vertices = [
        (0, 0, 0),  # Bottom left
        (page_width, 0, 0),  # Bottom right
        (page_width, page_height, 0),  # Top right
        (0, page_height, 0),  # Top left
    ]
    
    # Create edges
    edges = [
        (0, 1),  # Bottom edge
        (1, 2),  # Right edge
        (2, 3),  # Top edge
        (3, 0),  # Left edge
    ]
    
    # Create mesh
    mesh.from_pydata(vertices, edges, [])
    mesh.update()
    
    # Position frame at SVG location
    obj.location = (page_width / 2, page_height / 2, 0)
    
    # Create material for frame
    frame_mat = bpy.data.materials.new(name="Frame_Material")
    frame_mat.use_nodes = True
    nodes = frame_mat.node_tree.nodes
    links = frame_mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    
    # Set material properties (red for visibility)
    principled.inputs['Base Color'].default_value = (1, 0, 0, 1)  # Red
    principled.inputs['Metallic'].default_value = 0.0
    principled.inputs['Roughness'].default_value = 0.5
    
    # Connect nodes
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to frame
    obj.data.materials.append(frame_mat)
    
    print(f"✅ Created reference frame '{frame_name}'")
    print(f"✅ Frame shows SVG boundaries")

# Create reference frame
create_reference_frame()

print("\n✅ SVG reference plane setup complete!")
print("📋 The plane is positioned exactly where your SVG content is located")
print("📋 Use this plane as a reference for positioning other objects")
print("📋 The red frame shows the SVG boundaries") 