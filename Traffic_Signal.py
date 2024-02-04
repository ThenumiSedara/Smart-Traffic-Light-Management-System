import tkinter as tk
from time import sleep

class TrafficLightSimulator:
    def __init__(self, master):
        self.master = master
        self.master.title("Traffic Light Simulator")

        # Create canvas for the traffic lights
        self.canvas = tk.Canvas(self.master, width=500, height=800)
        self.canvas.pack()

        # Initialize lights attribute
        self.lights = []

        # Draw traffic lights
        self.draw_traffic_lights()

        # Start the simulation
        self.simulate_traffic_lights()

    def draw_traffic_lights(self):
        # Draw the traffic light poles for each direction
        self.draw_traffic_light_pole(50, 100)  # North
        self.draw_traffic_light_pole(200, 250)  # East
        self.draw_traffic_light_pole(150, 400)  # South
        self.draw_traffic_light_pole(0, 250)    # West

    def draw_traffic_light_pole(self, x, y):
        # Draw the traffic light pole
        self.canvas.create_rectangle(x + 95, y, x + 105, y + 300, fill="gray")

        # Draw the traffic lights (initially set to red)
        red_light = self.canvas.create_oval(x + 90, y + 10, x + 110, y + 50, fill="red", outline="black")
        yellow_light = self.canvas.create_oval(x + 90, y + 80, x + 110, y + 120, fill="gray", outline="black")
        green_light = self.canvas.create_oval(x + 90, y + 150, x + 110, y + 190, fill="gray", outline="black")

        # Save lights in a list for simulation
        self.lights.append((red_light, yellow_light, green_light))

    def simulate_traffic_lights(self):
        while True:
            for lights_set in self.lights:
                # Turn on the red light
                self.canvas.itemconfig(lights_set[0], fill="red")
                self.canvas.itemconfig(lights_set[1], fill="gray")
                self.canvas.itemconfig(lights_set[2], fill="gray")
                self.master.update()
                sleep(3)

                # Turn on the yellow light
                self.canvas.itemconfig(lights_set[0], fill="gray")
                self.canvas.itemconfig(lights_set[1], fill="yellow")
                self.canvas.itemconfig(lights_set[2], fill="gray")
                self.master.update()
                sleep(2)

                # Turn on the green light
                self.canvas.itemconfig(lights_set[0], fill="gray")
                self.canvas.itemconfig(lights_set[1], fill="gray")
                self.canvas.itemconfig(lights_set[2], fill="green")
                self.master.update()
                sleep(3)

                # Transition back to red before changing to the next set of lights
                self.canvas.itemconfig(lights_set[0], fill="red")
                self.canvas.itemconfig(lights_set[1], fill="gray")
                self.canvas.itemconfig(lights_set[2], fill="gray")
                self.master.update()
                sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    simulator = TrafficLightSimulator(root)
    root.mainloop()
