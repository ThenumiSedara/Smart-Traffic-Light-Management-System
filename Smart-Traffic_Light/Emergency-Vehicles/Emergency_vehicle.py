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
