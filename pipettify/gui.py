import tkinter as tk
from tkinter import messagebox

class PrinterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pipettify app")
        
        # Default bed dimensions (in mm)
        self.bed_width = 220
        self.bed_height = 220
        
        # Canvas size and margin
        self.canvas_size = 400
        self.margin = 20  # Space around the bed

        # Left Panel (3D Printer Bed View and Calibration Fields)
        left_panel = tk.Frame(self)
        left_panel.pack(side="left", padx=10, pady=10)

        # 3D Printer Bed View
        self.bed_canvas = tk.Canvas(left_panel, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.bed_canvas.pack()
        self.draw_bed_grid()

        # Bed Dimension Calibration
        bed_dim_frame = tk.Frame(left_panel)
        bed_dim_frame.pack(pady=5)

        tk.Label(bed_dim_frame, text="Bed Width (mm):").grid(row=0, column=0)
        self.bed_width_entry = tk.Entry(bed_dim_frame, width=8)
        self.bed_width_entry.insert(0, str(self.bed_width))
        self.bed_width_entry.grid(row=0, column=1)
        
        tk.Label(bed_dim_frame, text="Bed Height (mm):").grid(row=1, column=0)
        self.bed_height_entry = tk.Entry(bed_dim_frame, width=8)
        self.bed_height_entry.insert(0, str(self.bed_height))
        self.bed_height_entry.grid(row=1, column=1)
        
        tk.Button(bed_dim_frame, text="Load New Bed Dimensions", command=self.load_new_bed).grid(row=2, column=0, columnspan=2, pady=5)

        # Right Panel (Configuration Controls)
        right_panel = tk.Frame(self)
        right_panel.pack(side="left", padx=(10, 10), pady=(0, 10), anchor="n")

        # Align everything to the left
        right_panel.grid_columnconfigure(0, weight=1)

        # Probe Slot Grid Configuration
        grid_config_frame = tk.Frame(right_panel)
        grid_config_frame.pack(anchor="w", pady=5)

        tk.Label(grid_config_frame, text="Probe Slot Grid Configuration").grid(row=0, column=0, columnspan=3, sticky="w")
        tk.Label(grid_config_frame, text="Rows:").grid(row=1, column=0, sticky="w")
        self.rows_entry = tk.Entry(grid_config_frame, width=5)
        self.rows_entry.grid(row=1, column=1, sticky="w")
        tk.Label(grid_config_frame, text="Columns:").grid(row=1, column=2, sticky="w")
        self.columns_entry = tk.Entry(grid_config_frame, width=5)
        self.columns_entry.grid(row=1, column=3, sticky="w")

        # Probe Slot Position Calibration
        slot_pos_frame = tk.Frame(right_panel)
        slot_pos_frame.pack(anchor="w", pady=5)

        tk.Label(slot_pos_frame, text="Top-Left Slot Position (X, Y):").grid(row=0, column=0, sticky="w")
        self.tl_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.tl_x_entry.grid(row=0, column=1)
        self.tl_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.tl_y_entry.grid(row=0, column=2)
        tk.Button(slot_pos_frame, text="Calibrate", command=self.calibrate_top_left_slot).grid(row=0, column=3)

        tk.Label(slot_pos_frame, text="Bottom-Right Slot Position (X, Y):").grid(row=1, column=0, sticky="w")
        self.br_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.br_x_entry.grid(row=1, column=1)
        self.br_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.br_y_entry.grid(row=1, column=2)
        tk.Button(slot_pos_frame, text="Calibrate", command=self.calibrate_bottom_right_slot).grid(row=1, column=3)

        # Probe Top Height
        top_height_frame = tk.Frame(right_panel)
        top_height_frame.pack(anchor="w", pady=5)

        tk.Label(top_height_frame, text="Probe Top Height (mm):").grid(row=0, column=0, sticky="w")
        self.top_height_entry = tk.Entry(top_height_frame, width=8)
        self.top_height_entry.grid(row=0, column=1)
        tk.Button(top_height_frame, text="Calibrate", command=self.calibrate_top_height).grid(row=0, column=2)

        # Probe Diameter and Active Slots
        probe_diameter_frame = tk.Frame(right_panel)
        probe_diameter_frame.pack(anchor="w", pady=5)
        tk.Label(probe_diameter_frame, text="Probe Diameter (mm):").grid(row=0, column=0, sticky="w")
        self.diameter_entry = tk.Entry(probe_diameter_frame, width=8)
        self.diameter_entry.grid(row=0, column=1)

        active_slots_frame = tk.Frame(right_panel)
        active_slots_frame.pack(anchor="w", pady=5)
        tk.Label(active_slots_frame, text="Number of Active Probe Slots:").grid(row=0, column=0, sticky="w")
        self.active_slots_entry = tk.Entry(active_slots_frame, width=8)
        self.active_slots_entry.grid(row=0, column=1)

        # Configuration Load Buttons
        config_button_frame = tk.Frame(right_panel)
        config_button_frame.pack(anchor="w", pady=5)

        tk.Button(config_button_frame, text="Load Existing Configuration", command=self.load_existing_config).grid(row=0, column=0)
        tk.Button(config_button_frame, text="Load New Configuration", command=self.load_new_config).grid(row=0, column=1)

        # Execution Controls
        controls_frame = tk.Frame(self)
        controls_frame.pack(side="bottom", pady=10)
        tk.Button(controls_frame, text="STOP", fg="red", command=self.stop_execution).pack(side="left", padx=5)
        tk.Button(controls_frame, text="Test Run", command=self.test_run).pack(side="left", padx=5)
        tk.Button(controls_frame, text="Run", fg="green", command=self.run_execution).pack(side="left", padx=5)

    def draw_bed_grid(self):
        self.bed_canvas.delete("grid_line", "bed_outline", "scale_text")
        
        # Determine scaling to fit bed dimensions inside canvas while preserving aspect ratio
        max_width = self.canvas_size - 2 * self.margin
        max_height = self.canvas_size - 2 * self.margin
        scale = min(max_width / self.bed_width, max_height / self.bed_height)

        # Calculate bed outline coordinates
        bed_outline_width = self.bed_width * scale
        bed_outline_height = self.bed_height * scale
        x0 = (self.canvas_size - bed_outline_width) / 2
        y0 = (self.canvas_size - bed_outline_height) / 2
        x1 = x0 + bed_outline_width
        y1 = y0 + bed_outline_height

        # Draw bed outline
        self.bed_canvas.create_rectangle(x0, y0, x1, y1, outline="blue", width=2, tag="bed_outline")

        # Draw grid and scale
        step = 20  # mm step for grid lines
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

    def load_new_bed(self):
        try:
            # Update bed dimensions
            self.bed_width = int(self.bed_width_entry.get())
            self.bed_height = int(self.bed_height_entry.get())
            self.draw_bed_grid()
            messagebox.showinfo("Load Bed Dimensions", "New bed dimensions loaded!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for bed dimensions.")

    # Placeholder functions for button actions
    def calibrate_top_left_slot(self):
        messagebox.showinfo("Calibration", "Top-left slot calibrated!")

    def calibrate_bottom_right_slot(self):
        messagebox.showinfo("Calibration", "Bottom-right slot calibrated!")

    def calibrate_top_height(self):
        messagebox.showinfo("Calibration", "Top height calibrated!")

    def load_existing_config(self):
        messagebox.showinfo("Load Config", "Existing configuration loaded!")

    def load_new_config(self):
        """
        Take all of the values provided in settings (beside bed dimensions) and draw the probe grid accordingly.
        """
        try:
            # Get configuration values
            rows = int(self.rows_entry.get())
            columns = int(self.columns_entry.get())
            top_left_x = int(self.tl_x_entry.get())
            top_left_y = int(self.tl_y_entry.get())
            bottom_right_x = int(self.br_x_entry.get())
            bottom_right_y = int(self.br_y_entry.get())
            probe_diameter = int(self.diameter_entry.get())
            active_slots = int(self.active_slots_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for configuration settings.")
            return

        # Clear existing probes
        self.bed_canvas.delete("probe")

        # Determine scaling for probe positions based on top-left and bottom-right coordinates
        grid_width = bottom_right_x - top_left_x
        grid_height = bottom_right_y - top_left_y
        probe_spacing_x = grid_width / (columns - 1) if columns > 1 else 0
        probe_spacing_y = grid_height / (rows - 1) if rows > 1 else 0

        # Calculate scale to fit within the bed outline
        max_width = self.canvas_size - 2 * self.margin
        max_height = self.canvas_size - 2 * self.margin
        scale = min(max_width / self.bed_width, max_height / self.bed_height)
        bed_outline_width = self.bed_width * scale
        bed_outline_height = self.bed_height * scale
        x0 = (self.canvas_size - bed_outline_width) / 2
        y0 = (self.canvas_size - bed_outline_height) / 2

        # Draw probes in grid
        probe_count = 0
        for i in range(rows):
            for j in range(columns):
                if probe_count >= active_slots:
                    break
                # Calculate position on canvas
                probe_x = x0 + (top_left_x + j * probe_spacing_x) * scale
                probe_y = y0 + (top_left_y + i * probe_spacing_y) * scale
                # Draw probe as a circle with a dot
                self.bed_canvas.create_oval(
                    probe_x - probe_diameter * scale / 2, probe_y - probe_diameter * scale / 2,
                    probe_x + probe_diameter * scale / 2, probe_y + probe_diameter * scale / 2,
                    outline="red", width=2, tag="probe"
                )
                self.bed_canvas.create_oval(
                    probe_x - 2, probe_y - 2,
                    probe_x + 2, probe_y + 2,
                    fill="red", tag="probe"
                )
                probe_count += 1

        messagebox.showinfo("Load Config", "New configuration loaded!")


    def stop_execution(self):
        messagebox.showwarning("Execution", "Execution stopped!")

    def test_run(self):
        messagebox.showinfo("Test Run", "Test run started!")

    def run_execution(self):
        messagebox.showinfo("Execution", "Run started!")

if __name__ == "__main__":
    app = PrinterGUI()
    app.mainloop()
