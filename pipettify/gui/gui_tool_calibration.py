import tkinter as tk
from functools import partial

class CalibrateToolWindow(tk.Toplevel):
    def __init__(self, tool_controller):
        super().__init__()
        self.title("Tool Calibration")
        self.geometry("400x200")

        # Reference to the tool controller
        self.tool_controller = tool_controller

        # Movement Increment (in degrees)
        self.step_size = 10

        # Create the GUI controls
        self.create_controls()

        # Ensure focus for the window
        self.grab_set()
        self.focus_set()

    def create_controls(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)

        # Rotate clockwise button
        tk.Button(frame, text="Rotate Clockwise", command=self.rotate_clockwise).grid(row=0, column=0, padx=5, pady=5)

        # Rotate counterclockwise button
        tk.Button(frame, text="Rotate Counterclockwise", command=self.rotate_counterclockwise).grid(row=0, column=1, padx=5, pady=5)

        # Step size input
        tk.Label(frame, text="Step Size (degrees):").grid(row=1, column=0, padx=5, pady=5)
        self.step_size_entry = tk.Entry(frame, width=5)
        self.step_size_entry.grid(row=1, column=1, padx=5, pady=5)
        self.step_size_entry.insert(0, str(self.step_size))

        # Set as neutral button
        tk.Button(frame, text="Set as Neutral", command=self.set_as_neutral).grid(row=2, column=0, columnspan=2, pady=10)

    def rotate_clockwise(self):
        """Rotate the extruder clockwise by the step size."""
        try:
            step = self.get_step_size()
            self.tool_controller.move_to_position(self.tool_controller.current_position + step)
            print(f"Rotated clockwise by {step} degrees.")
        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))

    def rotate_counterclockwise(self):
        """Rotate the extruder counterclockwise by the step size."""
        try:
            step = self.get_step_size()
            self.tool_controller.move_to_position(self.tool_controller.current_position - step)
            print(f"Rotated counterclockwise by {step} degrees.")
        except ValueError as e:
            tk.messagebox.showerror("Error", str(e))

    def set_as_neutral(self):
        """Set the current extruder rotation as neutral."""
        try:
            self.tool_controller.neutral_position = self.tool_controller.current_position
            print(f"Set current rotation ({self.tool_controller.neutral_position} degrees) as neutral.")
            tk.messagebox.showinfo("Neutral Set", "Current rotation set as neutral.")
        except Exception as e:
            tk.messagebox.showerror("Error", str(e))

    def get_step_size(self):
        """Get the step size from the input field."""
        try:
            step_size = float(self.step_size_entry.get())
            if step_size <= 0:
                raise ValueError("Step size must be positive.")
            return step_size
        except ValueError:
            raise ValueError("Invalid step size. Please enter a positive number.")
