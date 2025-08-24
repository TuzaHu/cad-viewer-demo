#!/usr/bin/env python3
"""
Create reverse sequences from PNG animation directories
Usage: python3 create_reverse_sequences.py <source_directory>
"""

import os
import sys
import shutil
from pathlib import Path

def create_reverse_sequence(source_dir):
    """Create a reversed sequence from the source directory"""
    
    # Convert to Path object
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"Error: Directory '{source_dir}' does not exist")
        return
    
    if not source_path.is_dir():
        print(f"Error: '{source_dir}' is not a directory")
        return
    
    # Create reverse directory name
    reverse_dir = source_path.parent / f"{source_path.name}_reverse"
    
    # Get all PNG files and sort them
    png_files = sorted([f for f in source_path.glob("*.png")])
    
    if not png_files:
        print(f"No PNG files found in '{source_dir}'")
        return
    
    print(f"Found {len(png_files)} PNG files in '{source_dir}'")
    
    # Create reverse directory
    reverse_dir.mkdir(exist_ok=True)
    print(f"Created reverse directory: '{reverse_dir}'")
    
    # Get the frame number format (e.g., 4 digits like 0001, 0002)
    first_file = png_files[0].stem  # Get filename without extension
    frame_format = len(first_file)  # Length of frame number
    
    # Create reverse mapping
    total_frames = len(png_files)
    reverse_mapping = {}
    
    for i, png_file in enumerate(png_files):
        # Get current frame number (1-based)
        current_frame = i + 1
        
        # Calculate reverse frame number
        reverse_frame = total_frames - i
        
        # Format frame numbers with leading zeros
        current_str = str(current_frame).zfill(frame_format)
        reverse_str = str(reverse_frame).zfill(frame_format)
        
        reverse_mapping[current_str] = reverse_str
    
    # Copy and rename files
    print("Creating reverse sequence...")
    for i, png_file in enumerate(png_files):
        current_frame = str(i + 1).zfill(frame_format)
        reverse_frame = reverse_mapping[current_frame]
        
        # Create new filename
        new_filename = f"{reverse_frame}.png"
        new_path = reverse_dir / new_filename
        
        # Copy file with new name
        shutil.copy2(png_file, new_path)
        
        print(f"  {png_file.name} → {new_filename}")
    
    print(f"\n✅ Reverse sequence created successfully!")
    print(f"📁 Source: {source_dir}")
    print(f"📁 Reverse: {reverse_dir}")
    print(f"🔄 {total_frames} frames reversed")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 create_reverse_sequences.py <source_directory>")
        print("\nExample:")
        print("  python3 create_reverse_sequences.py Renders/front_top")
        print("  python3 create_reverse_sequences.py Renders/Rest_Top")
        sys.exit(1)
    
    source_directory = sys.argv[1]
    create_reverse_sequence(source_directory)

if __name__ == "__main__":
    main() 