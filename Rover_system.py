import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random

# --- Config ---
WINDOW_W, WINDOW_H = 900, 600
CONTROL_PANEL_W = 250
OBSTACLE_SIZE = 50
ROVER_SIZE = 70
OBSTACLE_SPEED = 10
ROVER_MOVE_STEP = 5
BG_SCROLL_SPEED = 2
MAX_OBSTACLES = 3
DODGE_DISTANCE = 100       # horizontal dodge distance
DETECTION_DISTANCE = 100   # distance to start dodge before collision
LEFT_BOUND = 100           # safe lane left
RIGHT_BOUND = WINDOW_W - CONTROL_PANEL_W - 100  # safe lane right

class RoverSim:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Rover Simulation")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.configure(bg="#1e1e2f")

        # --- Left Control Panel ---
        control_frame = tk.Frame(root, bg="#252540", width=CONTROL_PANEL_W, padx=15, pady=15)
        control_frame.pack(side="left", fill="y")

        tk.Label(control_frame, text="🎛️ Controls", fg="white", bg="#252540",
                 font=("Arial", 16, "bold")).pack(pady=10)

        # Throttle buttons
        self.throttle_on_btn = ttk.Button(control_frame, text="Throttle ON", command=self.throttle_on_func)
        self.throttle_on_btn.pack(pady=10, ipadx=10, ipady=5)
        self.throttle_off_btn = ttk.Button(control_frame, text="Throttle OFF", command=self.throttle_off_func)
        self.throttle_off_btn.pack(pady=10, ipadx=10, ipady=5)

        # Rudder controls
        tk.Label(control_frame, text="Rudder Angle", fg="white", bg="#252540").pack(pady=5)
        self.rudder_entry = ttk.Entry(control_frame, width=10)
        self.rudder_entry.pack(pady=5)
        ttk.Button(control_frame, text="Set Angle", command=self.set_rudder).pack(pady=5)

        # --- Right Canvas Simulation Area ---
        self.canvas = tk.Canvas(root, width=WINDOW_W - CONTROL_PANEL_W, height=WINDOW_H, bg="black", highlightthickness=0)
        self.canvas.pack(side="right", fill="both", expand=True)

        # Background image
        bg_img = Image.open("C:/Users/Lenovo/OneDrive/Desktop/Anant_Photo/Obstacle_BK.jpg")
        bg_img = bg_img.resize((WINDOW_W - CONTROL_PANEL_W, WINDOW_H))
        self.bg_img = ImageTk.PhotoImage(bg_img)
        self.bg_y1 = 0
        self.bg_y2 = -WINDOW_H
        self.bg1 = self.canvas.create_image(0, self.bg_y1, anchor="nw", image=self.bg_img)
        self.bg2 = self.canvas.create_image(0, self.bg_y2, anchor="nw", image=self.bg_img)

        # Rover image
        rover_img = Image.open("C:/Users/Lenovo/OneDrive/Desktop/Anant_Photo/Rover_image.jpg")
        rover_img = rover_img.resize((ROVER_SIZE, ROVER_SIZE))
        self.rover_img = ImageTk.PhotoImage(rover_img)
        self.rover_x = (WINDOW_W - CONTROL_PANEL_W)//2
        self.rover_y = WINDOW_H - 100
        self.rover = self.canvas.create_image(self.rover_x, self.rover_y, image=self.rover_img)
        self.rover_target_x = self.rover_x
        self.rover_home_x = self.rover_x

        # Load CA button images
        self.ca_on_img = ImageTk.PhotoImage(Image.open("C:/Users/Lenovo/OneDrive/Desktop/Anant_Photo/ON.png").resize((70,70)))
        self.ca_off_img = ImageTk.PhotoImage(Image.open("C:/Users/Lenovo/OneDrive/Desktop/Anant_Photo/OFF.png").resize((70,70)))

        # Fixed Collision Avoidance Buttons (bottom center)
        self.ca_frame = tk.Frame(root, bg="#1e1e2f")
        self.ca_frame.place(relx=0.5, rely=0.95, anchor="s")
        self.ca_on_btn = tk.Button(self.ca_frame, image=self.ca_on_img, command=self.ca_on_func,
                                   bd=0, bg="#1e1e2f", activebackground="#1e1e2f")
        self.ca_on_btn.grid(row=0, column=0, padx=10)
        self.ca_off_btn = tk.Button(self.ca_frame, image=self.ca_off_img, command=self.ca_off_func,
                                    bd=0, bg="#1e1e2f", activebackground="#1e1e2f")
        self.ca_off_btn.grid(row=0, column=1, padx=10)

        # Game state
        self.throttle_on = False
        self.ca_on = False
        self.obstacles = []

        # Start game loop
        self.update_game()

    # --- Throttle Functions ---
    def throttle_on_func(self):
        self.throttle_on = True

    def throttle_off_func(self):
        self.throttle_on = False

    # --- Rudder Function ---
    def set_rudder(self):
        try:
            angle = int(self.rudder_entry.get())
            self.rover_target_x = self.rover_x + angle
            self.rover_target_x = max(LEFT_BOUND, min(self.rover_target_x, RIGHT_BOUND))
            self.animate_rover()
        except:
            messagebox.showerror("Error", "Enter a valid integer angle")

    # --- Animate Rover ---
    def animate_rover(self):
        if self.rover_x < self.rover_target_x:
            self.rover_x += ROVER_MOVE_STEP
            if self.rover_x > self.rover_target_x: self.rover_x = self.rover_target_x
        elif self.rover_x > self.rover_target_x:
            self.rover_x -= ROVER_MOVE_STEP
            if self.rover_x < self.rover_target_x: self.rover_x = self.rover_target_x
        self.canvas.coords(self.rover, self.rover_x, self.rover_y)
        if self.rover_x != self.rover_target_x:
            self.root.after(20, self.animate_rover)

    # --- Collision Avoidance ---
    def ca_on_func(self):
        self.ca_on = True

    def ca_off_func(self):
        self.ca_on = False

    # --- Obstacles ---
    def spawn_obstacle(self):
        x = random.randint(LEFT_BOUND, RIGHT_BOUND - OBSTACLE_SIZE)
        obs = self.canvas.create_rectangle(x, 0, x + OBSTACLE_SIZE, OBSTACLE_SIZE, fill="red", outline="")
        self.obstacles.append(obs)

    def move_obstacles(self):
        for obs in self.obstacles[:]:
            self.canvas.move(obs, 0, OBSTACLE_SPEED)
            ox1, oy1, ox2, oy2 = self.canvas.coords(obs)

            # Dodge BEFORE collision using DETECTION_DISTANCE
            if oy2 >= self.rover_y - ROVER_SIZE//2 - DETECTION_DISTANCE and self.ca_on:
                # Move rover left or right within safe lane
                if self.rover_x < (WINDOW_W - CONTROL_PANEL_W)//2:
                    self.rover_target_x = min(self.rover_x + DODGE_DISTANCE, RIGHT_BOUND)
                else:
                    self.rover_target_x = max(self.rover_x - DODGE_DISTANCE, LEFT_BOUND)
                self.animate_rover()
                self.canvas.delete(obs)
                self.obstacles.remove(obs)
                continue

            if oy1 > WINDOW_H:
                self.canvas.delete(obs)
                self.obstacles.remove(obs)

    # --- Scroll Background ---
    def scroll_background(self):
        self.bg_y1 += BG_SCROLL_SPEED
        self.bg_y2 += BG_SCROLL_SPEED
        if self.bg_y1 >= WINDOW_H:
            self.bg_y1 = -WINDOW_H
        if self.bg_y2 >= WINDOW_H:
            self.bg_y2 = -WINDOW_H
        self.canvas.coords(self.bg1, 0, self.bg_y1)
        self.canvas.coords(self.bg2, 0, self.bg_y2)

    # --- Game Loop ---
    def update_game(self):
        # Randomly spawn 0-3 obstacles if throttle is on and total obstacles < MAX_OBSTACLES
        if self.throttle_on:
            spawn_count = random.randint(0, 3)
            for _ in range(spawn_count):
                if len(self.obstacles) < MAX_OBSTACLES:
                    self.spawn_obstacle()

        self.move_obstacles()
        self.scroll_background()
        self.root.after(100, self.update_game)  # frame rate

# --- Run App ---
root = tk.Tk()
style = ttk.Style()
style.configure("TButton", font=("Arial", 12, "bold"), padding=6)
app = RoverSim(root)
root.mainloop()