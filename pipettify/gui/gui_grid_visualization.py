import tkinter as tk
from tkinter import messagebox

class GuiGridVisualization:
    def __init__(self, canvas, probe_grid, printer_controller):
        self.probe_grid = probe_grid
        self.bed_canvas = canvas
        self.canvas_size = 400
        self.margin = 30 # Space around the bed
        self.bed_width = 220
        self.bed_height = 220
        self.printer_controller = printer_controller

    def load_new_bed(self, width_field, height_field):
        try:            
            # Update bed dimensions
            self.bed_width = int(width_field.get())
            self.bed_height = int(height_field.get())
            self.draw_bed_grid()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for bed dimensions.")

    def invert_y(self, y):
        """
        Invert the Y-coordinate for the canvas to flip the Y-axis.
        """
        return self.canvas_size - y

    def draw_bed_grid(self):
        """
        Draw the bed grid outline on the canvas with an inverted Y-axis.
        """
        self.bed_canvas.delete("grid_line", "bed_outline", "scale_text")
        
        # Calculate scaling
        max_width = self.canvas_size - 2 * self.margin
        max_height = self.canvas_size - 2 * self.margin
        scale = min(max_width / self.bed_width, max_height / self.bed_height)

        # Define bed boundaries
        bed_outline_width = self.bed_width * scale
        bed_outline_height = self.bed_height * scale
        x0 = (self.canvas_size - bed_outline_width) / 2
        y0 = (self.canvas_size - bed_outline_height) / 2
        x1 = x0 + bed_outline_width
        y1 = y0 + bed_outline_height

        # Draw the bed outline with inverted Y
        self.bed_canvas.create_rectangle(x0, self.invert_y(y0), x1, self.invert_y(y1), outline="blue", width=2, tag="bed_outline")

        # Draw the grid lines
        step = 30 #max(max_height, max_width) // 10
        for i in range(0, int(self.bed_width) + step, step):
            x = x0 + i * scale
            if x < x1:
                self.bed_canvas.create_line(x, self.invert_y(y0), x, self.invert_y(y1), fill="gray", dash=(2, 2), tag="grid_line")
                self.bed_canvas.create_text(x, self.invert_y(y0) + 5, text=str(i), fill="blue", tag="scale_text", anchor="n")

        for i in range(0, int(self.bed_height) + step, step):
            y = y0 + i * scale
            if y < y1:
                self.bed_canvas.create_line(x0, self.invert_y(y), x1, self.invert_y(y), fill="gray", dash=(2, 2), tag="grid_line")
                self.bed_canvas.create_text(x0 - 5, self.invert_y(y), text=str(i), fill="blue", tag="scale_text", anchor="e")

    def draw_probe_grid(self):
        """
        Draw the probe grid based on the ProbeGrid instance with an inverted Y-axis.
        """
        self.bed_canvas.delete("probe")
        rows = self.probe_grid.rows
        columns = self.probe_grid.columns
        probe_diameter = self.probe_grid.probe_diameter

        max_width = self.canvas_size - 2 * self.margin
        max_height = self.canvas_size - 2 * self.margin
        scale = min(max_width / self.bed_width, max_height / self.bed_height)
        x0 = (self.canvas_size - max_width) / 2
        y0 = (self.canvas_size - max_height) / 2

        # Draw probes with inverted Y
        for row in range(rows):
            for col in range(columns):
                if (row, col) in self.probe_grid.probes:
                    probe_x = x0 + (self.probe_grid.probes[(row, col)]["coordinates"][0]) * scale
                    probe_y = y0 + (self.probe_grid.probes[(row, col)]["coordinates"][1]) * scale
                    filled = self.probe_grid.probes[(row, col)]["filled"]
                    color = "red" if filled else "white"
                    self.bed_canvas.create_oval(
                        probe_x - probe_diameter * scale / 2,
                        self.invert_y(probe_y + probe_diameter * scale / 2),
                        probe_x + probe_diameter * scale / 2,
                        self.invert_y(probe_y - probe_diameter * scale / 2),
                        outline="black",
                        fill=color,
                        width=2,
                        tag="probe",
                    )
                
    def draw_tool_position(self):
        """
        Draw the tool position on the bed canvas with an inverted Y-axis.
        """
        try:
            x_mm = self.printer_controller.curr_x
            y_mm = self.printer_controller.curr_y

            # Scale the coordinates to fit the canvas
            max_width = self.canvas_size - 2 * self.margin
            max_height = self.canvas_size - 2 * self.margin
            scale = min(max_width / self.bed_width, max_height / self.bed_height)
            bed_outline_width = self.bed_width * scale
            bed_outline_height = self.bed_height * scale
            x0 = (self.canvas_size - bed_outline_width) / 2
            y0 = (self.canvas_size - bed_outline_height) / 2

            # Convert tool position to canvas coordinates with inverted Y
            tool_x = x0 + x_mm * scale
            tool_y = y0 + y_mm * scale

            # Clear the previous tool position
            self.bed_canvas.delete("tool_position")

            # Draw a new tool position (as a blue circle)
            radius = 5  # Radius of the tool indicator
            self.bed_canvas.create_oval(
                tool_x - radius, self.invert_y(tool_y) - radius,
                tool_x + radius, self.invert_y(tool_y) + radius,
                fill="blue", tag="tool_position"
            )
        except Exception as e:
            print(f"Error updating tool position: {e}")
