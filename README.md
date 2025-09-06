# CAD Viewer Demo

A sophisticated 3D CAD viewer with smooth animation transitions built with Three.js.

## 🚀 Quick Start

1. **Run the development server:**
   ```bash
   python3 scripts/server.py
   ```

2. **Open in browser:**
   ```
   http://localhost:8001
   ```

3. **Mobile access:**
   Scan the QR code in `assets/` folder

## 📁 Project Structure

```
├── app.js                 # Main application (Three.js animation player)
├── index.html            # Main web interface
├── cad-viewer.html       # Alternative CAD viewer interface
├── cadViewerScene.js     # CAD viewer scene management
├── sceneManager.js       # Scene management utilities
├── re.js                 # Additional app functionality
├── tu.css                # App styling
├── scripts/              # Development tools
│   ├── server.py         # Local development server
│   └── generate_qr.py    # QR code generator
├── blender/              # Blender workflow scripts
│   ├── set_cam_manual_dimensions_fixed.py    # Camera setup
│   ├── simple_png_import_fixed.py            # PNG import
│   ├── svg_to_png_manual_dimensions_fixed.py # SVG conversion
│   └── make_emission_material.py             # Material setup
├── docs/                 # Documentation
├── assets/               # Static assets (QR codes, etc.)
├── Renders/              # Animation sequences
├── images/               # Image assets
└── models/               # 3D models
```

## 🎮 Controls

- **Top/Front/Right/Reset buttons:** Navigate between different views
- **Play Sequence:** Play the complete animation sequence
- **Progress bar:** Shows animation progress

## 🔧 Development

### Web App
- **Local server:** `python3 scripts/server.py`
- **Generate QR:** `python3 scripts/generate_qr.py`
- **Cleanup:** `python3 cleanup_app.py`

### Blender Workflow
1. **Convert SVG to PNG:** `python3 blender/svg_to_png_manual_dimensions_fixed.py`
2. **Import PNG to Blender:** `python3 blender/simple_png_import_fixed.py`
3. **Set up camera:** `python3 blender/set_cam_manual_dimensions_fixed.py`
4. **Create emission material:** `python3 blender/make_emission_material.py`

## 📱 Mobile Access

QR codes are available in the `assets/` folder for easy mobile access.

## 🎨 Animation Sequences

The app includes multiple animation sequences:
- Rest positions (Top, Front, Right)
- Transition animations
- Play sequence
- Reverse sequences for smooth transitions

## 📄 Configuration Files

- `dimensions.txt` - Project dimensions
- `combination.txt` - Animation transition paths
- `positioning.txt` - Camera positioning data
- `view_export.json` - Export configuration
