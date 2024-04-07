import json
import os
import traci
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from traci.exceptions import FatalTraCIError
import traci.exceptions

def read_vehicle_counts(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return None


def map_img_id_to_route_id(img_id):
    return {
        "NorthBound": "NorthBound",
        "EastBound": "EastBound",
        "SouthBound": "SouthBound",
        "WestBound": "WestBound",
    }.get(img_id, None)


def extract_img_frame_info(image_file):
    img_id = os.path.splitext(image_file)[0]
    return img_id


def generate_vehicles(counts):
    for image_file, count in counts.items():
        img_id = extract_img_frame_info(image_file)
        route_id = map_img_id_to_route_id(img_id)
        if route_id:
            for _ in range(count):
                try:
                    depart_speed = 10.0
                    depart_pos = 50
                    traci.vehicle.add(
                        vehID=f"vehicle_{img_id}_{_}",
                        routeID=route_id,
                        departLane="random",
                        departPos=depart_pos,
                        departSpeed=depart_speed)
                except traci.exceptions.FatalTraCIError:
                    pass
                    return
                
            # Generate one emergency vehicle for each direction   
            if img_id in ["NorthBound", "EastBound", "SouthBound", "WestBound"]:
                for _ in range(4):
                    try:
                        emergency_depart_pos = 50
                        emergency_depart_speed = 20.0
                        traci.vehicle.add(
                            vehID=f"emergency_{img_id}_{_}",
                            routeID=route_id,
                            departLane="random",
                            departPos=emergency_depart_pos,
                            departSpeed=emergency_depart_speed,
                            typeID="emergency"
                        )
                    except traci.exceptions.FatalTraCIError:
                        pass
                        return
        else:
            print(f"Error: No route ID found for Image ID '{img_id}'")


# Function to find the lane with the highest vehicle count
def find_lane_with_highest_count(counts):
    max_count = max(counts.values())
    for direction, count in counts.items():
        if count == max_count:
            return direction
    return None


def prioritize_high_count_lane(counts):
    lane_with_highest_count = find_lane_with_highest_count(counts)
    
    # Strip the file extension if present (adjust as necessary based on your filenames)
    lane_with_highest_count = os.path.splitext(lane_with_highest_count)[0]
    
    print("\nLane with highest count:", lane_with_highest_count)

    phase_to_set = None  # Initialize to None to detect unhandled cases

    if lane_with_highest_count in ["NorthBound", "SouthBound"]:
        phase_to_set = 0  # Adjust phase number as needed for vertical traffic
    elif lane_with_highest_count in ["EastBound", "WestBound"]:
        phase_to_set = 2  # Adjust phase number as needed for horizontal traffic

    if phase_to_set is not None:
        traci.trafficlight.setPhase("tl0", phase_to_set)
        print(f"Prioritizing {lane_with_highest_count} by setting traffic light phase to {phase_to_set}.")
    else:
        print(f"Unhandled lane: {lane_with_highest_count}. Cannot set traffic light phase.")


def display_html_ui(counts):
    # Sorting the counts in descending order to easily identify the highest count
    sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Vehicle Counts at Junction</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 60px;
            background-color: #000;
            color: #fff;
        }}
        .lane-counts {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 20px;
        }}
        .lane {{
            background-color: rgba(255, 255, 255, 0.8);
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            width: 200px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            color: #000;
        }}
        .lane:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .lane h2, .lane span {{
            margin: 0;
            padding: 0;
        }}
        .lane h2 {{
            font-size: 18px;
            color: #333;
        }}
        .lane span {{
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .highlight {{
            background-color: #ccffcc; /* Highlight color */
        }}
        #timerDateContainer {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        #timer, #dateStamp {{
            color: #FFF;
            font-size: 20px;
            font-weight: bold;
            background-color: #333;
            padding: 10px;
            border-radius: 5px;
            display: block;
            margin: 0; 
        }}
        #dateStamp {{
            font-size: 15px;
        }}
    </style>
</head>
<body>
    <h1>Vehicle Counts at Junction</h1>
    <div class="lane-counts" id="laneCounts">
    {''.join(f'<div class="lane" id="lane{index}"><h2>{os.path.splitext(lane)[0]}</h2><span>{count}</span></div>' for index, (lane, count) in enumerate(sorted_counts))}
    </div>
    <div id="timerDateContainer">
        <div id="timer" style="margin-bottom: 8px;">Timer: 5</div>
        <div id="dateStamp" style="font-size: 14px;"></div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', (event) => {{
            let countdown = 8;
            const timerElement = document.getElementById('timer');
            const dateElement = document.getElementById('dateStamp'); // Get the date stamp element
            const updateTimerAndDate = () => {{
                const now = new Date();
                const dateString = now.toLocaleDateString(); // Get current date as a string
                const timeString = now.toLocaleTimeString(); // Get current time as a string
                timerElement.innerText = `Timer: ${{countdown}}`;
                dateElement.innerText = `Date: ${{dateString}}`; // Update date stamp
                countdown--;
                if (countdown < 0) {{
                    countdown = 8;
                }}
            }};

            // Initial timer and date update
            updateTimerAndDate();

            // Update the timer and date every second
            setInterval(updateTimerAndDate, 1000);
            
            const lanes = document.querySelectorAll('.lane');
            let currentIndex = 0;

            const highlightLane = () => {{
                // Set all to red first
                lanes.forEach(lane => {{
                    lane.style.backgroundColor = '#f69697';
                }});

                // Then highlight the current index green
                if (lanes[currentIndex]) {{
                    lanes[currentIndex].style.backgroundColor = '#ccffcc';
                }}
                
                // highlight the 2nd highest index yellow
                const secondIndex = (currentIndex + 1) % lanes.length;
                if (lanes[secondIndex]) {{
                    lanes[secondIndex].style.backgroundColor = '#feff78';
                }}
                
                currentIndex = (currentIndex + 1) % lanes.length;
            }};
            
            highlightLane();

            // Change highlight and reset timer every 10 seconds
            setInterval(highlightLane, 9000);
        }});
    </script>
</body>
</html>"""

    html_file_path = 'Simulation/index.html'
    with open(html_file_path, 'w') as file:
        file.write(html_content)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.set_window_size(800, 650)
    driver.get(f'file:///{os.path.abspath(html_file_path)}')
    driver.refresh()
    return driver 


if __name__ == "__main__":
    json_file = 'Object-Detection/object_counts.json'
    counts = read_vehicle_counts(json_file)
    browser_driver = display_html_ui(counts)
    sumo_binary = "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe"
    sumo_config_file = "Simulation/data/road.sumocfg"
    
    if not os.path.exists(sumo_binary) or not os.path.exists(sumo_config_file):
        print("Error: SUMO binary or configuration file not found.")
        browser_driver.quit()
        exit()
        
    try:
        traci.start([sumo_binary, "-c", sumo_config_file])
        generate_vehicles(counts)
        prioritize_high_count_lane(counts)
        while traci.simulation.getMinExpectedNumber() > 0:
            try:
                traci.simulationStep()
            except FatalTraCIError as e:
                print("\nSUMO GUI has been closed unexpectedly:", e)
                break
        traci.close()
        
        # Get the lane with the highest vehicle count
        lane_with_highest_count = find_lane_with_highest_count(counts)

        # Set initial phase to green for the lane with the highest count
        if lane_with_highest_count:
            green_duration = 30  # Adjust the green light duration as needed
            if lane_with_highest_count in ["NorthBound", "SouthBound"]:
                traci.trafficlight.setPhase("tl0", 0)  # Both North and South
            elif lane_with_highest_count in ["EastBound", "WestBound"]:
                traci.trafficlight.setPhase("tl0", 2)  # Both East and West
            traci.trafficlight.setPhaseDuration("tl0", green_duration)

        generate_vehicles(counts)

        try:
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()
        except traci.exceptions.FatalTraCIError:
            pass
    except traci.exceptions.FatalTraCIError:
        pass
    finally:
        try:
            traci.close()
        except:
            pass

