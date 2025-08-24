import os
import shutil
import re

def rename_png_sequence_safe(folder_path):
    """
    Safely rename PNG files by creating a new directory with renamed copies.
    Original files remain unchanged.
    
    Args:
        folder_path (str): Path to the folder containing PNG files
    """
    
    # Get all PNG files in the folder
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    
    if not png_files:
        print("No PNG files found in the folder.")
        return
    
    # Create new directory for renamed files
    base_dir = os.path.dirname(folder_path)
    folder_name = os.path.basename(folder_path)
    new_folder_name = f"{folder_name}_renamed"
    new_folder_path = os.path.join(base_dir, new_folder_name)
    
    # Remove existing renamed folder if it exists
    if os.path.exists(new_folder_path):
        shutil.rmtree(new_folder_path)
    
    os.makedirs(new_folder_path)
    print(f"Created new directory: {new_folder_path}")
    
    # Extract numbers from filenames using regex
    numbered_files = []
    for filename in png_files:
        # Find numbers in the filename
        numbers = re.findall(r'\d+', filename)
        if numbers:
            number = int(numbers[-1])  # Use the last number found
            numbered_files.append((number, filename))
        else:
            print(f"Skipping {filename} - no numbers found in filename")
    
    if not numbered_files:
        print("No numbered PNG files found.")
        return
    
    # Sort files by their number
    numbered_files.sort(key=lambda x: x[0])
    
    # Get the minimum number to calculate offset
    min_number = numbered_files[0][0]
    offset = min_number - 1
    
    # Copy and rename files to new directory
    copied_count = 0
    for original_number, filename in numbered_files:
        # Calculate new number
        new_number = original_number - offset
        
        # Construct new filename
        # Replace the last occurrence of the number
        new_filename = re.sub(rf'{original_number}(?!.*\d)', str(new_number), filename)
        
        # Handle edge case where replacement didn't work
        if new_filename == filename:
            # If regex substitution failed, try simple replacement
            new_filename = filename.replace(str(original_number), str(new_number))
        
        # Full paths
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(new_folder_path, new_filename)
        
        try:
            # Copy file to new location with new name
            shutil.copy2(old_path, new_path)
            print(f"Copied: {filename} -> {new_filename}")
            copied_count += 1
        except Exception as e:
            print(f"Error copying {filename}: {e}")
    
    print(f"\nProcess complete! {copied_count} files were copied and renamed.")
    print(f"Original files remain in: {folder_path}")
    print(f"Renamed files are in: {new_folder_path}")

def rename_png_sequence_simple_safe(folder_path):
    """
    Simple safe version for files named like '5.png'
    """
    
    # Get all PNG files in the folder
    png_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
    
    if not png_files:
        print("No PNG files found in the folder.")
        return
    
    # Create new directory for renamed files
    base_dir = os.path.dirname(folder_path)
    folder_name = os.path.basename(folder_path)
    new_folder_name = f"{folder_name}_renamed"
    new_folder_path = os.path.join(base_dir, new_folder_name)
    
    # Remove existing renamed folder if it exists
    if os.path.exists(new_folder_path):
        shutil.rmtree(new_folder_path)
    
    os.makedirs(new_folder_path)
    print(f"Created new directory: {new_folder_path}")
    
    # Extract numbers and sort
    numbered_files = []
    for filename in png_files:
        # Try to extract the number (assuming filename is just number.png)
        try:
            number = int(filename.split('.')[0])
            numbered_files.append((number, filename))
        except ValueError:
            print(f"Skipping {filename} - doesn't follow number.png pattern")
            continue
    
    if not numbered_files:
        print("No numbered PNG files found.")
        return
    
    # Sort by number
    numbered_files.sort(key=lambda x: x[0])
    
    # Calculate offset
    min_number = numbered_files[0][0]
    offset = min_number - 1
    
    # Copy and rename files
    copied_count = 0
    for original_number, filename in numbered_files:
        new_number = original_number - offset
        new_filename = f"{new_number}.png"
        
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(new_folder_path, new_filename)
        
        try:
            shutil.copy2(old_path, new_path)
            print(f"Copied: {filename} -> {new_filename}")
            copied_count += 1
        except Exception as e:
            print(f"Error copying {filename}: {e}")
    
    print(f"\nProcess complete! {copied_count} files were copied and renamed.")
    print(f"Original files remain in: {folder_path}")
    print(f"Renamed files are in: {new_folder_path}")

if __name__ == "__main__":
    # Get folder path from user
    folder_path = input("Enter the folder path containing PNG files: ").strip()
    
    # Validate folder exists
    if not os.path.exists(folder_path):
        print("Folder does not exist!")
        exit()
    
    # Ask which version to use
    print("\nChoose renaming method:")
    print("1. Advanced (handles complex filenames like 'image_5.png')")
    print("2. Simple (for files named like '5.png')")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        rename_png_sequence_safe(folder_path)
    elif choice == "2":
        rename_png_sequence_simple_safe(folder_path)
    else:
        print("Invalid choice. Using advanced method.")
        rename_png_sequence_safe(folder_path)