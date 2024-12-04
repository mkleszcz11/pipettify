import tkinter as tk

class ManualMovementWindow(tk.Toplevel):
    def __init__(self, printer_controller):
        super().__init__()
        self.title("Manual Movement Controls")
        self.geometry("600x300")

        # Reference to PrinterController
        self.printer_controller = printer_controller

        # Movement Increment (in mm)
        self.step_size = 10

        # Add movement controls
        self.create_movement_controls()

    def create_movement_controls(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        # Movement buttons
        tk.Button(frame, text="+Y", command=self.move_y_positive).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame, text="-X", command=self.move_x_negative).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frame, text="+X", command=self.move_x_positive).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(frame, text="-Y", command=self.move_y_negative).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(frame, text="Up Z", command=self.move_up_z).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(frame, text="Down Z", command=self.move_down_z).grid(row=2, column=3, padx=5, pady=5)
        
        # Button to set the step size
        tk.Label(frame, text="Step Size (mm):").grid(row=3, column=0)        
        self.step_size_entry = tk.Entry(frame, width = 3)
        self.step_size_entry.grid(row=3, column=1)
        self.step_size_entry.insert(0, str(self.step_size))
        tk.Button(frame, text="Set step", command=self.set_step_size).grid(row=3, column=3)
        
        # Field and button to move to specific coordinates
        tk.Label(frame, text="Move to (X,Y,Z):").grid(row=4, column=0, sticky="w")
        self.x_entry = tk.Entry(frame, width=5)
        self.x_entry.grid(row=4, column=1)
        self.y_entry = tk.Entry(frame, width=5)
        self.y_entry.grid(row=4, column=2)
        self.z_entry = tk.Entry(frame, width=5)
        self.z_entry.grid(row=4, column=3)
        tk.Button(frame, text="Move to", command=self.move_to_coordinates).grid(row=4, column=4)

    def move_y_positive(self):
        # self.printer_controller.move_relative(0, self.step_size, 0)
        # self.printer_controller.update_current_coordinates()
        self.printer_controller.move_to_coordinates(self.printer_controller.curr_x,
                                                    self.printer_controller.curr_y + self.step_size,
                                                    self.printer_controller.curr_z)

    def move_y_negative(self):
        # self.printer_controller.move_relative(0, -self.step_size, 0)
        # self.printer_controller.update_current_coordinates()
        self.printer_controller.move_to_coordinates(self.printer_controller.curr_x,
                                                    self.printer_controller.curr_y - self.step_size,
                                                    self.printer_controller.curr_z)

    def move_x_negative(self):
        # self.printer_controller.move_relative(-self.step_size, 0, 0)
        # self.printer_controller.update_current_coordinates()
        self.printer_controller.move_to_coordinates(self.printer_controller.curr_x - self.step_size,
                                                    self.printer_controller.curr_y,
                                                    self.printer_controller.curr_z)

    def move_x_positive(self):
        # self.printer_controller.move_relative(self.step_size, 0, 0)
        # self.printer_controller.update_current_coordinates()
        self.printer_controller.move_to_coordinates(self.printer_controller.curr_x + self.step_size,
                                                    self.printer_controller.curr_y,
                                                    self.printer_controller.curr_z)

    def move_up_z(self):
        # self.printer_controller.move_relative(0, 0, self.step_size)
        # self.printer_controller.update_current_coordinates()
        self.printer_controller.move_to_coordinates(self.printer_controller.curr_x,
                                                    self.printer_controller.curr_y,
                                                    self.printer_controller.curr_z + self.step_size)

    def move_down_z(self):
        # self.printer_controller.move_relative(0, 0, -self.step_size)
        # self.printer_controller.update_current_coordinates()
        self.printer_controller.move_to_coordinates(self.printer_controller.curr_x,
                                                    self.printer_controller.curr_y,
                                                    self.printer_controller.curr_z - self.step_size)
        
    def set_step_size(self):
        self.step_size = float(self.step_size_entry.get())
        print(f"Step size set to {self.step_size} mm")
        
    def move_to_coordinates(self):
        self.printer_controller.update_current_coordinates()
        x = float(self.x_entry.get())
        y = float(self.y_entry.get())
        z = float(self.z_entry.get())
        self.printer_controller.move_to_coordinates(x, y, z)
        print(f"Moving to coordinates: X={x}, Y={y}, Z={z}")
