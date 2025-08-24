import bpy
import os

print("=== SIMPLE IMPORT TEST ===")

# Clear existing objects
print("Clearing existing objects...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
print("✅ Cleared all objects")

# Create a simple plane
print("Creating plane...")
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "Test_Plane"
print(f"✅ Created plane: {plane.name}")

# Scale the plane
plane.scale.x = 0.420  # 420mm in meters
plane.scale.y = 0.297  # 297mm in meters
print(f"✅ Scaled plane to: {plane.scale}")

# Create material
print("Creating material...")
mat = bpy.data.materials.new(name="Test_Material")
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
png_path = "/home/tuza/Tapp/exported2.png"
if os.path.exists(png_path):
    tex_image.image = bpy.data.images.load(png_path)
    print(f"✅ Loaded image: {png_path}")
else:
    print(f"❌ Image not found: {png_path}")

# Connect nodes
links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to plane
plane.data.materials.append(mat)
print("✅ Assigned material to plane")

# Setup camera
print("Setting up camera...")
camera_name = "Camera"
cam = bpy.data.objects.get(camera_name)
if cam is None:
    cam_data = bpy.data.cameras.new(name=camera_name)
    cam = bpy.data.objects.new(name=camera_name, object_data=cam_data)
    bpy.context.scene.collection.objects.link(cam)

cam.data.type = 'ORTHO'
cam.data.ortho_scale = 0.420
cam.location = (0.210, 0.1485, 10)
cam.rotation_euler = (0, 0, 0)
bpy.context.scene.camera = cam
print("✅ Camera setup complete")

print("\n✅ Simple import test complete!")
print("You should see a plane with your PNG texture") 