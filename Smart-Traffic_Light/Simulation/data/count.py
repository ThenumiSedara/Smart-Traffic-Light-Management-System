import json
import os
import traci
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from traci.exceptions import FatalTraCIError

def read_vehicle_counts(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return None

def generate_vehicles(counts):
    for image_file, count in counts.items():
        video_id = extract_img_frame_info(image_file)
        route_id = map_img_id_to_route_id(video_id)
        if route_id:
            for _ in range(count):
                # This is a simplified example. Customize your vehicle generation as needed.
                traci.vehicle.add(vehID=f"vehicle_{video_id}_{_}", routeID=route_id, depart=traci.simulation.getTime())
        else:
            print(f"Error: No route ID found for video ID '{video_id}'")

def map_img_id_to_route_id(video_id):
    # Example mapping, adjust according to your needs
    return {
        "NorthBound": "NorthBound",
        "EastBound": "EastBound",
        "SouthBound": "SouthBound",
        "WestBound": "WestBound",
    }.get(video_id, None)

def extract_img_frame_info(image_file):
    # Directly use the file name as the video ID, remove the file extension
    video_id = os.path.splitext(image_file)[0]
    return video_id


def display_html_ui(counts):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vehicle Counts at Junction</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"> <!-- Include Font Awesome for icons -->
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 60px;
            background-color: #000;
            background-size: 100% auto; 
            background-position: center center;
            background-repeat: no-repeat;
            height: 100vh; 
            color: #fff;
        }}
        h1 {{
            color: #fff;
            margin-bottom: 30px;
        }}
        .lane-counts {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 20px;
        }}
        .lane-group {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .lane {{
            background-color: rgba(255, 255, 255, 0.8);
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            width: 200px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        .lane:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .lane span {{
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
            display: block;
            margin-top: 10px;
        }}
        .lane h2 {{
            font-size: 18px; /* Reduced font size */
            margin-bottom: 10px;
            color: #555;
        }}
    </style>
</head>
<body>
    <h1>Vehicle Counts at Junction</h1>
    <div class="lane-counts">
        {"".join(f'<div class="lane"><h2>{lane}</h2><span>{count}</span></div>' for lane, count in counts.items())}
    </div>
</body>
</html>"""

    # Save to a temporary HTML file
    html_file_path = 'Simulation3/index.html'
    with open(html_file_path, 'w') as file:
        file.write(html_content)

    # Display in browser using Selenium
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    # Set the desired window size
    driver.set_window_size(800, 650) 
    
    driver.get(f'file:///{os.path.abspath(html_file_path)}')
    return driver


if __name__ == "__main__":
    json_file = 'Object-Detection/object_counts.json'
    counts = read_vehicle_counts(json_file)
    
    # First, display the HTML UI with vehicle counts
    browser_driver = display_html_ui(counts)

    # Initialize SUMO and TraCI
    sumo_binary = "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe"  # Adjust the path to your SUMO GUI binary
    sumo_config_file = "Simulation3/data/road.sumocfg"  # Adjust the path to your configuration file
    
    if not os.path.exists(sumo_binary) or not os.path.exists(sumo_config_file):
        print("Error: SUMO binary or configuration file not found.")
        browser_driver.quit()
        exit()
        
    try:
        traci.start([sumo_binary, "-c", sumo_config_file])
        generate_vehicles(counts)

        while traci.simulation.getMinExpectedNumber() > 0:
            try:
                traci.simulationStep()
            except FatalTraCIError as e:
                print("\nSUMO GUI has been closed unexpectedly:", e)
                break
        traci.close()
    except FatalTraCIError as e:
        print("\nFailed to start SUMO GUI:", e)

    input("\nPress Enter to close the browser and exit...\n")
    if 'driver' in locals():
        browser_driver.quit()
