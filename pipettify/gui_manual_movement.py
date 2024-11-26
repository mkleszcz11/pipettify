import tkinter as tk

class ManualMovementWindow(tk.Toplevel):
    def __init__(self, printer_controller):
        super().__init__()
        self.title("Manual Movement Controls")
        self.geometry("300x300")

        # Reference to PrinterController
        self.printer_controller = printer_controller

        # Movement Increment (in mm)
        self.step_size = 10

        # Add movement controls
        self.create_movement_controls()

    def create_movement_controls(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Button(frame, text="Up", command=self.move_up).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame, text="Left", command=self.move_left).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frame, text="Right", command=self.move_right).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(frame, text="Down", command=self.move_down).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(frame, text="Up Z", command=self.move_up_z).grid(row=0, column=3, padx=5, pady=5)
        tk.Button(frame, text="Down Z", command=self.move_down_z).grid(row=2, column=3, padx=5, pady=5)

    def move_up(self):
        self.printer_controller.move_relative(0, self.step_size, 0)

    def move_down(self):
        self.printer_controller.move_relative(0, -self.step_size, 0)

    def move_left(self):
        self.printer_controller.move_relative(-self.step_size, 0, 0)

    def move_right(self):
        self.printer_controller.move_relative(self.step_size, 0, 0)

    def move_up_z(self):
        self.printer_controller.move_relative(0, 0, self.step_size)

    def move_down_z(self):
        self.printer_controller.move_relative(0, 0, -self.step_size)
