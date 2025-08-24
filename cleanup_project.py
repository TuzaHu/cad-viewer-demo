#!/usr/bin/env python3
"""
Project Cleanup Script
Moves old/experimental scripts to a backup directory and keeps only essential files.
"""

import os
import shutil
from datetime import datetime

def create_backup_directory():
    """Create a backup directory with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_old_scripts_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def move_file_to_backup(file_path, backup_dir):
    """Move a file to backup directory"""
    if os.path.exists(file_path):
        shutil.move(file_path, os.path.join(backup_dir, os.path.basename(file_path)))
        print(f"✅ Moved {file_path} to backup")

def cleanup_project():
    """Main cleanup function"""
    print("🧹 Starting project cleanup...")
    
    # Create backup directory
    backup_dir = create_backup_directory()
    print(f"📁 Created backup directory: {backup_dir}")
    
    # Files to keep (essential working files)
    essential_files = [
        'exported2.svg',
        'dimensions.txt',
        'view_export.json',
        'svg_to_png_manual_dimensions_fixed.py',
        'set_cam_manual_dimensions_fixed.py',
        'simple_png_import_fixed.py',
        'make_emission_material.py',
        'exported2.png',
        'README.txt',
        'cleanup_project.py'
    ]
    
    # Directories to keep
    essential_dirs = [
        'Renders',
        'donotuse'
    ]
    
    # Files to move to backup (old/experimental scripts)
    files_to_backup = [
        'simple_png_import.py',
        'set_cam.py',
        'set_cam_simple.py',
        'set_cam_fixed.py',
        'set_cam_actual_dimensions.py',
        'set_cam_actual_result.py',
        'set_cam_manual_dimensions.py',
        'set_cam_png_fixed.py',
        'svg_to_png_actual_dimensions.py',
        'svg_to_png_actual_result.py',
        'svg_to_png_manual_dimensions.py',
        'svg_to_png_plane.py',
        'svg_to_png_plane_fixed.py',
        'blender_manual_dimensions_import.py',
        'blender_manual_dimensions_import_fixed.py',
        'blender_svg_to_png_plane.py',
        'blender_svg_to_png_plane_fixed.py',
        'create_svg_plane.py',
        'render_technical_drawing.py',
        'simple_import_test.py',
        'debug_import.py',
        'Result.png',
        'export2a.svg'
    ]
    
    # Move files to backup
    print("\n📦 Moving old/experimental files to backup...")
    for file_path in files_to_backup:
        move_file_to_backup(file_path, backup_dir)
    
    # List remaining files
    print("\n📋 Essential files remaining:")
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
    
    print("\n📁 Essential directories:")
    for dir_path in essential_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ (missing)")
    
    print(f"\n🎉 Cleanup complete!")
    print(f"📁 Old files backed up to: {backup_dir}")
    print(f"📋 Essential files ready for use")
    print(f"📖 Read README.txt for complete workflow instructions")

if __name__ == "__main__":
    cleanup_project() 