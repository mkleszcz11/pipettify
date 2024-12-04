import threading
import tkinter as tk
from tkinter import messagebox
from pipettify.controllers.controller_printer import PrinterController
from pipettify.controllers.controller_bed import BedController
from pipettify.gui.gui_manual_movement import ManualMovementWindow
from pipettify.gui.gui_grid_visualization import GuiGridVisualization

class PrinterGUI(tk.Tk):
    def __init__(self, printer_controller, bed_controller, state_machine):
        super().__init__()
        self.title("Pipettify app")
        
        self.state_machine = state_machine # Used only when user starts program
        self.printer_controller = printer_controller
        self.bed_controller = bed_controller
        
        # State machine variables
        self.stop_flag = threading.Event()
        self.state_machine_polling_interval = 100  # Poll every 100ms

        # Add "Manual Movement" button
        tk.Button(self, text="Manual Movement", command=self.open_manual_movement).pack(pady=10)
        
        # Add state display box
        self.state_label = tk.Label(self, text=f"State: {self.state_machine.current_state.id}", font=("Arial", 16))
        self.state_label.pack(pady=10)

        # Default bed dimensions (in mm)
        self.bed_width = 300
        self.bed_height = 300
        
        # Canvas size and margin
        self.canvas_size = 400
        self.margin = 20  # Space around the bed

        # Left Panel (3D Printer Bed View and Calibration Fields)
        left_panel = tk.Frame(self)
        left_panel.pack(side="left", padx=10, pady=10)

        # 3D Printer Bed View
        self.bed_canvas = tk.Canvas(left_panel, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.bed_canvas.pack()
        self.gui_grid_visualization = GuiGridVisualization(canvas=self.bed_canvas, probe_grid=self.bed_controller, printer_controller=self.printer_controller)
        # self.gui_grid_visualization.draw_bed_grid()

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
        
        tk.Button(bed_dim_frame, text="Load New Bed Dimensions", command=lambda: self.gui_grid_visualization.load_new_bed(self.bed_width_entry, self.bed_height_entry)).grid(row=2, column=0, columnspan=2, pady=5)
        self.gui_grid_visualization.load_new_bed(self.bed_width_entry, self.bed_height_entry) # Draw the bed grid at the start

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

        # Probe Slot Position Calibration (Grid placement and probes height)
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

        tk.Label(slot_pos_frame, text="Probe Top Height (mm):").grid(row=2, column=0, sticky="w")
        self.top_height_entry = tk.Entry(slot_pos_frame, width=5)
        self.top_height_entry.grid(row=2, column=1)
        tk.Button(slot_pos_frame, text="Calibrate", command=self.calibrate_top_height).grid(row=2, column=3, sticky="e")

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

        # Move to Coordinates Section
        move_frame = tk.Frame(right_panel)
        move_frame.pack(pady=5)

        tk.Label(move_frame, text="Move to (X,Y,Z):").grid(row=0, column=0, sticky="w")
        self.x_entry = tk.Entry(move_frame, width=5)
        self.x_entry.grid(row=0, column=1)
        self.y_entry = tk.Entry(move_frame, width=5)
        self.y_entry.grid(row=0, column=2)
        self.z_entry = tk.Entry(move_frame, width=5)
        self.z_entry.grid(row=0, column=3)
        tk.Button(move_frame, text="Move to Coordinates", command=self.move_to_coordinates).grid(row=0, column=4)

        # Home XYZ button
        tk.Button(move_frame, text="Home", command=self.printer_controller.home).grid(row=0, column=5)

        # HOME E button
        tk.Button(move_frame, text="Home E", command=self.printer_controller.tool_controller.calibrate_neutral_position).grid(row=0, column=6)

        # Execution Controls
        controls_frame = tk.Frame(self)
        controls_frame.pack(side="bottom", pady=10)
        self.stop_button = tk.Button(controls_frame, text="STOP", fg="red", command=self.stop_state_machine_execution)
        self.stop_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(controls_frame, text="Reset State", command=self.reset_state)
        self.reset_button.pack(side="left", padx=5)

        self.run_button = tk.Button(controls_frame, text="Run", fg="green", command=self.run_state_machine_execution)
        self.run_button.pack(side="left", padx=5)

        self.rows_entry.insert(0, 5)
        self.columns_entry.insert(0, 10)
        self.tl_x_entry.insert(0, 42)
        self.tl_y_entry.insert(0, 10)
        self.br_x_entry.insert(0, 250)
        self.br_y_entry.insert(0, 150)
        self.top_height_entry.insert(0, 150)
        self.diameter_entry.insert(0, 5)
        self.active_slots_entry.insert(0, 49)
        
        self.refresh_display()
        self.refresh_tool_position()
        self.start_state_machine_polling()

    def update_state_display(self):
        """
        Update the state label with the current state of the state machine.
        """
        self.state_label.config(text=f"State: {self.state_machine.current_state.id}")

    def load_new_config(self):
        """
        Update ProbeGrid.
        """
        try:
            rows = int(self.rows_entry.get())
            columns = int(self.columns_entry.get())
            top_left_x = int(self.tl_x_entry.get())
            top_left_y = int(self.tl_y_entry.get())
            bottom_right_x = int(self.br_x_entry.get())
            bottom_right_y = int(self.br_y_entry.get())
            probe_diameter = int(self.diameter_entry.get())
            active_slots = int(self.active_slots_entry.get())

            # Update ProbeGrid
            self.bed_controller.make_new_grid(
                rows=rows,
                columns=columns,
                top_left=(top_left_x, top_left_y),
                bottom_right=(bottom_right_x, bottom_right_y),
                probe_diameter=probe_diameter,
                num_probes=active_slots,
            )

            messagebox.showinfo("Load Config", "New configuration loaded!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for configuration settings.")
    
    def refresh_display(self):
        """
        Refresh the display to show the current state of the grid and tool position. Do it every second.
        """
        self.gui_grid_visualization.draw_probe_grid()
        self.gui_grid_visualization.draw_tool_position()
        self.after(1000, self.refresh_display)
        
    def refresh_tool_position(self):
        """
        Refresh the tool position by sending request through printer controller Do it every 500 ms.
        """
        self.printer_controller.update_current_coordinates()
        self.after(500, self.refresh_tool_position)

    # Placeholder functions for button actions
    def calibrate_top_left_slot(self):
        messagebox.showinfo("Calibration", "Top-left slot calibrated!")

    def calibrate_bottom_right_slot(self):
        messagebox.showinfo("Calibration", "Bottom-right slot calibrated!")

    def calibrate_top_height(self):
        messagebox.showinfo("Calibration", "Top height calibrated!")

    def load_existing_config(self):
        messagebox.showinfo("Load Config", "Existing configuration loaded!")

    def move_to_coordinates(self):
        """
        Move to specified coordinates based on user input.
        """
        try:
            # Get values from input boxes
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())

            # Call the PrinterController function to move
            self.printer_controller.move_to_coordinates(x, y, z)
            messagebox.showinfo("Move to Coordinates", f"Moving to X: {x}, Y: {y}, Z: {z}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for X, Y, and Z.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def open_manual_movement(self):
        # Create and display the manual movement window
        manual_movement_window = ManualMovementWindow(self.printer_controller)
        manual_movement_window.grab_set()  # Focus on the new window

    def reset_state(self): #TODO -> change name
        """
        Reset the state machine to its initial state.
        """
        self.state_machine.reset()
        messagebox.showinfo("Reset", "State machine has been reset!")

    def start_state_machine_polling(self):
        """
        Start the periodic polling of the state machine.
        """
        # print("Starting state machine polling...")
        if self.stop_flag.is_set():
            return
        # print("POOOLIIINNNNGGGGG")
        state_completed = self.state_machine.poll()
        # if not state_completed:
        #     # Continue polling
        self.after(self.state_machine_polling_interval, self.start_state_machine_polling)
        # else:
        #     print("State machine step completed.")

    def run_state_machine_execution(self):
        """
        Start the state machine execution.
        """
        self.stop_flag.clear()
        self.state_machine.start_pipetting()
        self.start_state_machine_polling()

    def stop_state_machine_execution(self):
        """
        Stop the state machine execution.
        """
        self.stop_flag.set()
        print("Execution stopped.")
