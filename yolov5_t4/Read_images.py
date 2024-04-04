import subprocess
import re
import os
import json

# Script directory
script_directory = "../Smart-Traffic_Light/"

# Base directory where you want to save the output images and results
base_output_directory = "../Smart-Traffic_Light/Object-Detection/yolov5/runs/detect"

# Create the base output directory if it does not exist
os.makedirs(base_output_directory, exist_ok=True)

# Determine the index for the exp directory
exp_index = len(os.listdir(base_output_directory))

# Path to the folder containing images
image_folder = '../Smart-Traffic_Light/Object-Detection/input_images'

# List of image paths
image_paths = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(('.jpg', '.png'))]

# Initialize a list to store total vehicle counts for each image
total_vehicle_counts_list = []

# Iterate over the image paths
for image_path in image_paths:
    # Determine the directory name based on the current exp index
    exp_directory = os.path.join(base_output_directory, f"exp{exp_index}")

    # Create the exp directory if it does not exist
    os.makedirs(exp_directory, exist_ok=True)

    # Extract the image file name
    image_file_name = os.path.basename(image_path)

    # Run the command and capture its output
    command = f'python ../Smart-Traffic_Light/Object-Detection/yolov5/detect.py --source {image_path} --data ../Smart-Traffic_Light/Object-Detection/dataset/dataset.yaml --weights ../Smart-Traffic_Light/Object-Detection/yolov5/runs/train/exp/weights/best.pt --project {exp_directory}'
    process = subprocess.Popen(command, cwd=script_directory, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()

    # Decode the output and error messages
    output_text = error.decode('utf-8')

    # Define a regex pattern to match the vehicle counts
    pattern = r'(\d+) (Cars|Motorcycles|Buses|Trucks|Ambulances)'

    # Use regex to find all matches in the output text
    matches = re.findall(pattern, output_text)

    # Initialize a dictionary to store vehicle counts
    vehicle_counts = {}

    # Extract vehicle counts from the matches
    for count, vehicle_type in matches:
        vehicle_counts[vehicle_type] = int(count)

    # Display vehicle counts for the current image
    print(f"Image: {image_file_name}")
    total_count = 0
    for vehicle_type, count in vehicle_counts.items():
        print(f"{vehicle_type}: {count}")
        total_count += count

    print(f"Total Vehicles: {total_count}\n")

    # Add the total vehicle count to the list
    total_vehicle_counts_list.append({image_file_name: total_count})

# Increment the exp index for the next run
exp_index += 1

# Convert the list of dictionaries to a single dictionary
merged_counts = {}
for item in total_vehicle_counts_list:
    merged_counts.update(item)

# Save total vehicle counts to a file
output_file = ("../Smart-Traffic_Light/Object-Detection/object_counts.json")
with open(output_file, 'w') as f:
    json.dump(merged_counts, f)

print("Total vehicle counts saved to:", output_file)

