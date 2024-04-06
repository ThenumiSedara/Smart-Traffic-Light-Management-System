import os
import shutil

def swap_files(folder_A, folder_B):
    # Step 1: Create a temporary directory
    temp_folder = os.path.join(os.path.dirname(folder_A), 'temp_swap_folder')
    os.makedirs(temp_folder, exist_ok=True)

    # Step 2: Move files from folder_A to temp_folder
    for filename in os.listdir(folder_A):
        shutil.move(os.path.join(folder_A, filename), os.path.join(temp_folder, filename))

    # Step 3: Move files from folder_B to folder_A
    for filename in os.listdir(folder_B):
        shutil.move(os.path.join(folder_B, filename), os.path.join(folder_A, filename))

    # Step 4: Move files from temp_folder to folder_B
    for filename in os.listdir(temp_folder):
        shutil.move(os.path.join(temp_folder, filename), os.path.join(folder_B, filename))

    # Clean up by removing the temporary folder
    os.rmdir(temp_folder)

# Example usage
folder_A = 'Object-Detection/input_images'
folder_B = 'Object-Detection/input_images_temp'
swap_files(folder_A, folder_B)
