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


def generate_vehicles(counts):
    for direction, count in counts.items():
        for i in range(count):
            depart_speed = 10.0
            depart_pos = 50
            traci.vehicle.add(
                vehID=f"vehicle_{direction}_{i}",
                routeID=direction,
                departLane="random",
                departPos=depart_pos,
                departSpeed=depart_speed
            )

    # Generate emergency vehicles
    traci.vehicle.add(vehID="emergency_north_1", routeID="NorthBound", departLane="random", departPos=depart_pos,
                      departSpeed=depart_speed, typeID="emergency")
    traci.vehicle.add(vehID="emergency_north_2", routeID="NorthBound", departLane="random", departPos=depart_pos,
                      departSpeed=depart_speed, typeID="emergency")
    traci.vehicle.add(vehID="emergency_north_3", routeID="NorthBound", departLane="random", departPos=depart_pos,
                      departSpeed=depart_speed, typeID="emergency")

    traci.vehicle.add(vehID="emergency_south_1", routeID="SouthBound", departLane="random", departPos=depart_pos,
                      departSpeed=depart_speed, typeID="emergency")
    traci.vehicle.add(vehID="emergency_south_2", routeID="SouthBound", departLane="random", departPos=depart_pos,
                      departSpeed=depart_speed, typeID="emergency")

    traci.vehicle.add(vehID="emergency_west_1", routeID="WestBound", departLane="random", departPos=depart_pos,
                      departSpeed=depart_speed, typeID="emergency")


def find_lane_with_highest_count(counts):
    max_count = max(counts.values())
    for direction, count in counts.items():
        if count == max_count:
            return direction
    return None

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
            time.sleep(2)
        else:
            print("Error: SUMO binary or configuration file not found.")
            exit()

        traci.start([sumo_binary, "-c", "road.sumocfg"])

        print("SUMO started successfully.")

        lane_with_highest_count = find_lane_with_highest_count(counts)
        print("Lane with highest count:", lane_with_highest_count)

        if lane_with_highest_count:
            green_duration = 30  # Adjust the green light duration as needed
            if lane_with_highest_count in ["NorthBound", "SouthBound"]:
                traci.trafficlight.setPhase("tl0", 0)  # Both North and South
            elif lane_with_highest_count in ["EastBound", "WestBound"]:
                traci.trafficlight.setPhase("tl0", 2)  # Both East and West
            traci.trafficlight.setPhaseDuration("tl0", green_duration)
            print("Setting traffic light phase and duration...")

        generate_vehicles(counts)

        print("Generating vehicles...")

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()

        print("Simulation completed.")

        traci.close()

        print("Closing SUMO.")

        subprocess.Popen([sumo_binary, "-c", sumo_config_file])

        print("Restarting SUMO...")
