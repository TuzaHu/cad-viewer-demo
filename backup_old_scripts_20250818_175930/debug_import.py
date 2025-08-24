import bpy
import os

print("=== DEBUG: PNG Import Test ===")

# Check if PNG exists
png_path = "/home/tuza/Tapp/exported2.png"
print(f"Checking PNG file: {png_path}")
print(f"File exists: {os.path.exists(png_path)}")

# Check dimensions.txt
dimensions_file = "dimensions.txt"
print(f"Checking dimensions file: {dimensions_file}")
print(f"File exists: {os.path.exists(dimensions_file)}")

if os.path.exists(dimensions_file):
    with open(dimensions_file, 'r') as f:
        print("Dimensions file contents:")
        print(f.read())

# Test basic plane creation
print("\n=== Testing plane creation ===")
try:
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    plane = bpy.context.active_object
    print(f"✅ Created test plane: {plane.name}")
    print(f"   Location: {plane.location}")
    print(f"   Scale: {plane.scale}")
except Exception as e:
    print(f"❌ Error creating plane: {e}")

# Test image loading
print("\n=== Testing image loading ===")
try:
    if os.path.exists(png_path):
        image = bpy.data.images.load(png_path)
        print(f"✅ Loaded image: {image.name}")
        print(f"   Size: {image.size[0]} x {image.size[1]}")
    else:
        print(f"❌ PNG file not found: {png_path}")
except Exception as e:
    print(f"❌ Error loading image: {e}")

print("\n=== Debug complete ===") 