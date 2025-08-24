# 🎯 SVG to Blender Technical Drawing Pipeline
## Complete Workflow Documentation

### 📋 Overview
This project converts FreeCAD technical drawings (SVG) into high-quality Blender renders by converting SVG to PNG first, then importing the PNG into Blender as an image plane with emission materials.

---

## 🛠️ Prerequisites

### Required Software:
1. **Python 3.x** - For running conversion scripts
2. **Inkscape** - For SVG to PNG conversion
   ```bash
   sudo apt install inkscape
   ```
3. **Blender 3.x+** - For 3D rendering
4. **FreeCAD** - For creating source SVG files

### Required Python Packages:
```bash
pip install lxml
```

---

## 📁 Project Structure

```
Tapp/
├── exported2.svg                    # Source FreeCAD technical drawing
├── dimensions.txt                   # Central configuration file
├── view_export.json                # FreeCAD export configuration
├── svg_to_png_manual_dimensions_fixed.py    # SVG to PNG converter
├── set_cam_manual_dimensions_fixed.py       # Camera setup script
├── simple_png_import_fixed.py              # PNG import script
├── make_emission_material.py               # Emission material script
├── exported2.png                   # Generated PNG file
└── Renders/                        # Animation sequences (optional)
    ├── Rest_Sliced_2/             # 144-frame slicing animation
    ├── Rest_sliced/               # 73-frame slicing animation
    ├── Rest_Top/                  # 72-frame top view animation
    └── Resr_Right/                # 72-frame right view animation
```

---

## ⚙️ Configuration

### 1. Edit dimensions.txt
This is the **central configuration file** that all scripts read from:

```bash
# Manual Dimensions Configuration
# Edit these values to match your actual conversion results

# PNG dimensions (pixels) - from your Result.png
PNG_WIDTH=1488
PNG_HEIGHT=1052

# Actual SVG dimensions (mm) - from exported2.svg
TEMPLATE_WIDTH=420
TEMPLATE_HEIGHT=297
```

**Important:** 
- `PNG_WIDTH` and `PNG_HEIGHT` should match your desired render resolution
- `TEMPLATE_WIDTH` and `TEMPLATE_HEIGHT` should match your SVG's actual dimensions in mm

---

## 🚀 Complete Workflow

### Step 1: Prepare Your SVG File
1. Export your technical drawing from FreeCAD as SVG
2. Place the SVG file in the project directory (e.g., `exported2.svg`)
3. Note the SVG's actual dimensions (width × height in mm)

### Step 2: Configure Dimensions
1. Open `dimensions.txt`
2. Update `TEMPLATE_WIDTH` and `TEMPLATE_HEIGHT` to match your SVG dimensions
3. Set `PNG_WIDTH` and `PNG_HEIGHT` to your desired render resolution

### Step 3: Convert SVG to PNG
```bash
cd /home/tuza/Tapp
python svg_to_png_manual_dimensions_fixed.py
```

**What this does:**
- Reads dimensions from `dimensions.txt`
- Converts your SVG to PNG using Inkscape
- Forces exact pixel dimensions as specified
- Outputs `exported2.png`

**Expected output:**
```
✅ Read dimensions from dimensions.txt:
   PNG: 1488 x 1052 pixels
   SVG: 420 x 297 mm
✅ Converting SVG to PNG...
✅ PNG created successfully: exported2.png
✅ PNG dimensions verified: 1488 x 1052 pixels
```

### Step 4: Open Blender and Set Up Camera
1. Open Blender
2. Open the Script Editor (View → Toggle System Console)
3. Run the camera setup script:
   ```python
   exec(open('set_cam_manual_dimensions_fixed.py').read())
   ```

**What this does:**
- Sets up orthographic camera
- Uses SVG dimensions for camera scale
- Uses PNG dimensions for render resolution
- Positions camera correctly

**Expected output:**
```
✅ Camera setup complete
✅ Camera ortho scale: 0.42
✅ Camera location: (0.21, 0.1485, 10)
✅ Render resolution: 1488 x 1052 pixels
```

### Step 5: Import PNG as Image Plane
```python
exec(open('simple_png_import_fixed.py').read())
```

**What this does:**
- Creates a plane in Blender
- Scales it to match SVG dimensions
- Applies the PNG as a texture
- Positions it correctly in 3D space

**Expected output:**
```
✅ Created image plane 'SVG_Image_Plane'
✅ Plane location: (0.21, 0.1485, 0)
✅ Plane dimensions: 0.42m x 0.297m
✅ PNG import complete!
```

### Step 6: Convert to Emission Material
```python
exec(open('make_emission_material.py').read())
```

**What this does:**
- Converts the material to emission (self-illuminating)
- Perfect for technical drawings
- Makes the drawing glow and stand out

**Expected output:**
```
✅ Emission material created successfully!
✅ Material 'SVG_Image_Material' is now self-illuminating
```

### Step 7: Render Your Technical Drawing
1. Switch to **Cycles** render engine (Render → Render Engine → Cycles)
2. Set render settings:
   - **Resolution**: 1488 × 1052 (already set by camera script)
   - **Samples**: 128-256 for good quality
   - **Output**: PNG format
3. Press **F12** or click **Render → Render Image**

---

## 🎬 Creating Animation Sequences (Optional)

If you want to create animation sequences like those in the `Renders/` directory:

### For Slicing Animations:
1. Set up your pipe model in Blender
2. Use the **Boolean modifier** with animated cutting planes
3. Render frames 001-144 (or your desired range)
4. Save to `Renders/Your_Animation_Name/`

### For Rotation Animations:
1. Set up your model
2. Add rotation keyframes
3. Render the sequence
4. Save to appropriate subdirectory

---

## 🔧 Troubleshooting

### Common Issues:

**1. "Inkscape not found"**
```bash
sudo apt install inkscape
```

**2. "dimensions.txt not found"**
- Make sure you're in the correct directory
- Check that `dimensions.txt` exists and has correct format

**3. "PNG dimensions don't match"**
- Verify Inkscape is installed and working
- Check that your SVG file exists and is valid
- Ensure `dimensions.txt` has correct values

**4. "Blender script errors"**
- Make sure all scripts are in the same directory as your `.blend` file
- Check that `exported2.png` exists before running import scripts
- Verify Python syntax in Blender's Script Editor

**5. "Material not working"**
- Ensure you're using Cycles render engine
- Check that the material was applied to the correct object
- Verify the PNG texture is loaded correctly

### Debug Commands:
```bash
# Check if Inkscape is installed
which inkscape

# Verify PNG dimensions
file exported2.png

# Check script syntax
python -m py_compile svg_to_png_manual_dimensions_fixed.py
```

---

## 📊 Performance Tips

### For High-Quality Renders:
- Use **Cycles** render engine
- Set **samples** to 256-512 for final renders
- Enable **Denoising** for cleaner results
- Use **GPU rendering** if available

### For Animation Sequences:
- Use **Eevee** for faster preview renders
- Use **Cycles** for final quality
- Consider **batch rendering** for multiple sequences
- Use **render layers** for complex scenes

---

## 🎯 Expected Results

After following this workflow, you should have:
1. ✅ A high-quality PNG of your technical drawing
2. ✅ A Blender scene with your drawing as an image plane
3. ✅ Correct camera setup with proper dimensions
4. ✅ Self-illuminating material for professional appearance
5. ✅ Ready-to-render technical drawing

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure `dimensions.txt` has correct values
4. Check that all files are in the correct locations

---

## 🔄 Workflow Summary

```bash
# 1. Configure dimensions
nano dimensions.txt

# 2. Convert SVG to PNG
python svg_to_png_manual_dimensions_fixed.py

# 3. In Blender Script Editor, run:
exec(open('set_cam_manual_dimensions_fixed.py').read())
exec(open('simple_png_import_fixed.py').read())
exec(open('make_emission_material.py').read())

# 4. Render (F12)
```

**Total time:** ~5-10 minutes for complete setup
**Output:** Professional technical drawing renders ready for documentation or presentation

---

*Last updated: August 2024*
*Project: SVG to Blender Technical Drawing Pipeline* 