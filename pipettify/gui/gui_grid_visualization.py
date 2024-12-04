import tkinter as tk
from tkinter import messagebox

class GuiGridVisualization:
    def __init__(self, canvas, probe_grid, printer_controller):
        self.probe_grid = probe_grid
        self.bed_canvas = canvas
        self.canvas_size = 400
        self.margin = 20 # Space around the bed
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

    def draw_bed_grid(self):
        """
        Draw the bed grid outline on the canvas.
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

        # Draw the bed outline
        self.bed_canvas.create_rectangle(x0, y0, x1, y1, outline="blue", width=2, tag="bed_outline")

        # Draw the grid lines
        step = 20
        for i in range(0, int(self.bed_width) + step, step):
            x = x0 + i * scale
            if x < x1:
                self.bed_canvas.create_line(x, y0, x, y1, fill="gray", dash=(2, 2), tag="grid_line")
                self.bed_canvas.create_text(x, y0 - 5, text=str(i), fill="blue", tag="scale_text", anchor="s")

        for i in range(0, int(self.bed_height) + step, step):
            y = y0 + i * scale
            if y < y1:
                self.bed_canvas.create_line(x0, y, x1, y, fill="gray", dash=(2, 2), tag="grid_line")
                self.bed_canvas.create_text(x0 - 5, y, text=str(i), fill="blue", tag="scale_text", anchor="e")

    def draw_probe_grid(self):
        """
        Draw the probe grid based on the ProbeGrid instance.
        """
        self.bed_canvas.delete("probe")
        rows = self.probe_grid.rows
        columns = self.probe_grid.columns
        # top_left_x, top_left_y = self.probe_grid.top_left
        # bottom_right_x, bottom_right_y = self.probe_grid.bottom_right
        probe_diameter = self.probe_grid.probe_diameter

        # # Calculate spacing and scaling
        # probe_spacing_x = (bottom_right_x - top_left_x) / (columns - 1) if columns > 1 else 0
        # probe_spacing_y = (bottom_right_y - top_left_y) / (rows - 1) if rows > 1 else 0

        max_width = self.canvas_size - 2 * self.margin
        max_height = self.canvas_size - 2 * self.margin
        scale = min(max_width / self.bed_width, max_height / self.bed_height)
        x0 = (self.canvas_size - max_width) / 2
        y0 = (self.canvas_size - max_height) / 2

        # Draw probes
        for row in range(rows):
            for col in range(columns):
                if (row, col) in self.probe_grid.probes:
                    probe_x = x0 + (self.probe_grid.probes[(row,col)]["coordinates"][0]) * scale
                    probe_y = y0 + (self.probe_grid.probes[(row,col)]["coordinates"][1]) * scale
                    filled = self.probe_grid.probes[(row, col)]["filled"]
                    color = "red" if filled else "white"
                    self.bed_canvas.create_oval(
                        probe_x - probe_diameter * scale / 2,
                        probe_y - probe_diameter * scale / 2,
                        probe_x + probe_diameter * scale / 2,
                        probe_y + probe_diameter * scale / 2,
                        outline="black",
                        fill=color,
                        width=2,
                        tag="probe",
                    )
                
    def draw_tool_position(self):
        """
        Draw the tool position on the bed canvas based on the printer's current coordinates.
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

            # Convert tool position to canvas coordinates
            tool_x = x0 + x_mm * scale
            tool_y = y0 + y_mm * scale

            # Clear the previous tool position
            self.bed_canvas.delete("tool_position")

            # Draw a new tool position (as a blue circle)
            radius = 5  # Radius of the tool indicator
            self.bed_canvas.create_oval(
                tool_x - radius, tool_y - radius,
                tool_x + radius, tool_y + radius,
                fill="blue", tag="tool_position"
                )
        except Exception as e:
            print(f"Error updating tool position: {e}")

