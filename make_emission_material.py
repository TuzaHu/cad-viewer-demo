import bpy

print("=== CONVERTING TO EMISSION MATERIAL ===")

# Find the SVG image plane
plane_name = "SVG_Image_Plane"
plane = bpy.data.objects.get(plane_name)

if plane is None:
    print(f"❌ Could not find plane: {plane_name}")
    print("Please run the import script first")
else:
    print(f"✅ Found plane: {plane.name}")
    
    # Get the material
    if plane.data.materials:
        mat = plane.data.materials[0]
        print(f"✅ Found material: {mat.name}")
        
        # Enable nodes if not already enabled
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear existing nodes
        nodes.clear()
        
        # Create emission material nodes
        output = nodes.new(type='ShaderNodeOutputMaterial')
        emission = nodes.new(type='ShaderNodeEmission')
        tex_image = nodes.new(type='ShaderNodeTexImage')
        
        # Load the PNG image
        png_path = "/home/tuza/Tapp/exported2.png"
        if tex_image.image is None:
            tex_image.image = bpy.data.images.load(png_path)
            print(f"✅ Loaded image: {png_path}")
        
        # Connect nodes for emission material
        links.new(tex_image.outputs['Color'], emission.inputs['Color'])
        links.new(emission.outputs['Emission'], output.inputs['Surface'])
        
        # Set emission strength (adjust this value as needed)
        emission.inputs['Strength'].default_value = 1.0
        
        print("✅ Converted to emission material!")
        print("✅ The plane will now emit light based on the image")
        print("✅ Adjust emission strength in the material nodes if needed")
        
    else:
        print("❌ No material found on the plane")
        print("Please run the import script first")

print("\n=== EMISSION MATERIAL TIPS ===")
print("1. The plane will now emit light")
print("2. Adjust emission strength in the material nodes")
print("3. You may need to enable 'Emission' in render settings")
print("4. For better results, use Cycles render engine") 