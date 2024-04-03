import json
import subprocess
import os
import traci
import random
import time

def read_vehicle_counts(json_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return None

def map_video_id_to_route_id(video_id):
    route_mapping = {
        "video2": "EastBound",
        "video4": "WestBound",
        "video5": "SouthBound",
        "video6": "NorthBound"
    }
    return route_mapping.get(video_id, None)

def extract_video_frame_info(image_file):
    parts = image_file.split("_")
    video_id = parts[0]
    frame_number = int(parts[-1].split(".")[0])
    return video_id, frame_number

def generate_vehicles(counts):
    for image_file, count in counts.items():
        video_id, frame_number = extract_video_frame_info(image_file)
        route_id = map_video_id_to_route_id(video_id)
        if route_id:
            for i in range(count):
                depart_speed = 10.0
                depart_pos = 50
                traci.vehicle.add(
                    vehID=f"vehicle_{video_id}_{frame_number}_{i}",
                    routeID=route_id,  # Use the correct route ID
                    departLane="random",
                    departPos=depart_pos,
                    departSpeed=depart_speed
                )
            # Generate one emergency vehicle for each direction
            if video_id in ["video5", "video6"]:
                # Define the depart position and speed for the emergency vehicle
                emergency_depart_pos = 50  # Adjust as needed
                emergency_depart_speed = 20.0  # Adjust as needed
                # Add the emergency vehicle with red color
                traci.vehicle.add(
                    vehID=f"emergency_{video_id}_{frame_number}",
                    routeID=route_id,
                    departLane="random",
                    departPos=emergency_depart_pos,
                    departSpeed=emergency_depart_speed,
                    typeID="emergency"
                )
        else:
            print(f"Error: No route ID found for video ID '{video_id}'")

if __name__ == "__main__":
    json_file = 'object_counts.json'
    counts = read_vehicle_counts(json_file)
    if counts is not None:
        print("Vehicle counts read from JSON file:")
        for direction, count in counts.items():
            print(f"{direction}: {count}")

        sumo_binary = r'C:\Program Files (x86)\Eclipse\Sumo\bin\sumo-gui.exe'
        sumo_config_file = 'road.sumocfg'
        if os.path.exists(sumo_binary) and os.path.exists(sumo_config_file):
            print("Launching SUMO...")
            proc = subprocess.Popen([sumo_binary, "-c", sumo_config_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            print("SUMO output:", stdout.decode())
            print("SUMO errors:", stderr.decode())
            time.sleep(10)
        else:
            print("Error: SUMO binary or configuration file not found.")
            exit()

        traci.start([sumo_binary, "-c", "road.sumocfg"])

        generate_vehicles(counts)

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

        traci.close()

        subprocess.Popen([sumo_binary, "-c", sumo_config_file])
