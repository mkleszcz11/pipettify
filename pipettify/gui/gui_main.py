import threading
import tkinter as tk
from tkinter import messagebox
from pipettify.controllers.controller_printer import PrinterController
from pipettify.controllers.controller_bed import BedController
from pipettify.gui.gui_manual_movement import ManualMovementWindow
from pipettify.gui.gui_tool_calibration import CalibrateToolWindow
from pipettify.gui.gui_grid_visualization import GuiGridVisualization
from pipettify.gui.gui_import_export_config import ConfigImportExport

from functools import partial

class PrinterGUI(tk.Tk):
    def __init__(self, printer_controller, bed_controller, state_machine):
        super().__init__()
        self.title("Pipettify app")
        self.gui_import_export = ConfigImportExport(interface = self)
        
        self.state_machine = state_machine # Used only when user starts program
        self.printer_controller = printer_controller
        self.bed_controller = bed_controller
        
        # State machine variables
        self.stop_flag = threading.Event()
        self.state_machine_polling_interval = 300  # Poll every 100ms

        # Add "Manual Movement" button
        tk.Button(self, text="Manual Movement", command=self.open_manual_movement).pack(pady=10)
        
        # # Add state display box
        # self.state_label = tk.Label(self, text=f"State: {self.state_machine.current_state.id}", font=("Arial", 16))
        # self.state_label.pack(pady=10)

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
        self.gui_grid_visualization = GuiGridVisualization(canvas=self.bed_canvas, bed_controller=self.bed_controller, printer_controller=self.printer_controller)
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

        # Probe Slot Position Calibration (Grid placement and probes height)
        slot_pos_frame = tk.Frame(right_panel)
        slot_pos_frame.pack(anchor="w", pady=5)

        # Add frame title
        slot_pos_frame_title = tk.Label(slot_pos_frame, text="Grid Settings", font=("Arial", 12, "bold"))
        slot_pos_frame_title.grid(row=0, column=0, columnspan=9, sticky="w")
        slot_pos_frame.grid_columnconfigure(0, weight=1)

        # Define padding
        slot_pos_frame_padding_x = 20  # Padding between columns for separation

        # Add configuration labels for Probes, Tips, and Tanks
        tk.Label(slot_pos_frame, text="Probes Config", font=("Arial", 10, "bold")).grid(row=1, column=1, columnspan=4, sticky="w")
        tk.Label(slot_pos_frame, text="Tips Config", font=("Arial", 10, "bold")).grid(row=1, column=4, columnspan=3, sticky="w", padx=(slot_pos_frame_padding_x, 0))
        tk.Label(slot_pos_frame, text="Tank Config", font=("Arial", 10, "bold")).grid(row=1, column=7, columnspan=3, sticky="w", padx=(slot_pos_frame_padding_x, 0))

        # Add grid configuration fields for Probes
        tk.Label(slot_pos_frame, text="Rows, Col. :").grid(row=2, column=0, sticky="w")
        self.probes_rows_entry = tk.Entry(slot_pos_frame, width=5)
        self.probes_rows_entry.grid(row=2, column=1)
        self.probes_columns_entry = tk.Entry(slot_pos_frame, width=5)
        self.probes_columns_entry.grid(row=2, column=2)

        # Add grid configuration fields for Tips
        self.tips_rows_entry = tk.Entry(slot_pos_frame, width=5)
        self.tips_rows_entry.grid(row=2, column=4, padx=(slot_pos_frame_padding_x, 0))
        self.tips_columns_entry = tk.Entry(slot_pos_frame, width=5)
        self.tips_columns_entry.grid(row=2, column=5)

        ##############################
        # Probes corners calibration
        ##############################
        tk.Label(slot_pos_frame, text="Bottom-Left:").grid(row=3, column=0, sticky="w")
        self.probe_tl_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.probe_tl_x_entry.grid(row=3, column=1)
        self.probe_tl_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.probe_tl_y_entry.grid(row=3, column=2)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "probe-top-left")).grid(row=3, column=3)

        tk.Label(slot_pos_frame, text="Bottom-Right:").grid(row=4, column=0, sticky="w")
        self.probe_tr_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.probe_tr_x_entry.grid(row=4, column=1)
        self.probe_tr_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.probe_tr_y_entry.grid(row=4, column=2)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "probe-top-right")).grid(row=4, column=3)

        tk.Label(slot_pos_frame, text="Top-Left:").grid(row=5, column=0, sticky="w")
        self.probe_bl_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.probe_bl_x_entry.grid(row=5, column=1)
        self.probe_bl_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.probe_bl_y_entry.grid(row=5, column=2)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "probe-bottom-left")).grid(row=5, column=3)

        tk.Label(slot_pos_frame, text="Top-Right:").grid(row=6, column=0, sticky="w")
        self.probe_br_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.probe_br_x_entry.grid(row=6, column=1)
        self.probe_br_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.probe_br_y_entry.grid(row=6, column=2)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "probe-bottom-right")).grid(row=6, column=3)

        ##############################
        # Tips corners calibration
        ##############################
        self.tip_tl_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.tip_tl_x_entry.grid(row=3, column=4, padx=(slot_pos_frame_padding_x, 0))
        self.tip_tl_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.tip_tl_y_entry.grid(row=3, column=5)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "tip-top-left")).grid(row=3, column=6)

        self.tip_tr_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.tip_tr_x_entry.grid(row=4, column=4, padx=(slot_pos_frame_padding_x, 0))
        self.tip_tr_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.tip_tr_y_entry.grid(row=4, column=5)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "tip-top-right")).grid(row=4, column=6)

        self.tip_bl_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.tip_bl_x_entry.grid(row=5, column=4, padx=(slot_pos_frame_padding_x, 0))
        self.tip_bl_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.tip_bl_y_entry.grid(row=5, column=5)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "tip-bottom-left")).grid(row=5, column=6)

        self.tip_br_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.tip_br_x_entry.grid(row=6, column=4, padx=(slot_pos_frame_padding_x, 0))
        self.tip_br_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.tip_br_y_entry.grid(row=6, column=5)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "tip-bottom-right")).grid(row=6, column=6)

        ##############################
        # Tank calibration
        ##############################
        tk.Label(slot_pos_frame, text="Refilling:").grid(row=2, column=7, sticky="w", padx=(slot_pos_frame_padding_x, 0))
        self.refilling_tank_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.refilling_tank_x_entry.grid(row=2, column=8)
        self.refilling_tank_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.refilling_tank_y_entry.grid(row=2, column=9)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "refilling_tank")).grid(row=2, column=10)

        tk.Label(slot_pos_frame, text="Disposal:").grid(row=3, column=7, sticky="w", padx=(slot_pos_frame_padding_x, 0))
        self.disposal_tank_x_entry = tk.Entry(slot_pos_frame, width=5)
        self.disposal_tank_x_entry.grid(row=3, column=8)
        self.disposal_tank_y_entry = tk.Entry(slot_pos_frame, width=5)
        self.disposal_tank_y_entry.grid(row=3, column=9)
        tk.Button(slot_pos_frame, text="set", command=partial(self.calibrate_slot, "disposal_tank")).grid(row=3, column=10)

        ##############################
        # Active slots calibration
        ##############################
        tk.Label(slot_pos_frame, text="Active Slots:").grid(row=7, column=0, sticky="w")
        self.active_probe_slots_entry = tk.Entry(slot_pos_frame, width=5)
        self.active_probe_slots_entry.grid(row=7, column=1)
        self.active_tip_slots_entry = tk.Entry(slot_pos_frame, width=5, )
        self.active_tip_slots_entry.grid(row=7, column=4, padx=(slot_pos_frame_padding_x, 0))

        ##############################
        # Z height calibration
        ##############################
        z_height_frame = tk.Frame(right_panel)
        z_height_frame.pack(anchor="w", pady=5)
        z_height_frame.grid_columnconfigure(1, weight=1)
        
        # Add frame title to show the user what the frame is for, make it bold
        z_height_frame_title = tk.Label(z_height_frame, text="Z Height Settings", font=("Arial", 12, "bold"))
        z_height_frame_title.pack()
        z_height_frame_title.grid(row=0, column=0, columnspan=2, sticky="w")

        tk.Label(z_height_frame, text="XY movement:").grid(row=1, column=0, sticky="w")
        self.safe_z_height_entry = tk.Entry(z_height_frame, width=5)
        self.safe_z_height_entry.grid(row=1, column=1)
        tk.Button(z_height_frame, text="set", command=partial(self.calibrate_slot, "safe_z")).grid(row=1, column=3, sticky="e")
        
        tk.Label(z_height_frame, text="Refilling:").grid(row=2, column=0, sticky="w")
        self.refilling_height_entry = tk.Entry(z_height_frame, width=5)
        self.refilling_height_entry.grid(row=2, column=1)
        tk.Button(z_height_frame, text="set", command=partial(self.calibrate_slot, "refilling_z")).grid(row=2, column=3, sticky="e")

        tk.Label(z_height_frame, text="Dispensing:").grid(row=3, column=0, sticky="w")
        self.dispensing_height_entry = tk.Entry(z_height_frame, width=5)
        self.dispensing_height_entry.grid(row=3, column=1)
        tk.Button(z_height_frame, text="set", command=partial(self.calibrate_slot, "dispensing_z")).grid(row=3, column=3, sticky="e")
        
        tk.Label(z_height_frame, text="Change tip:").grid(row=4, column=0, sticky="w")
        self.change_tip_height_entry = tk.Entry(z_height_frame, width=5)
        self.change_tip_height_entry.grid(row=4, column=1)
        tk.Button(z_height_frame, text="set", command=partial(self.calibrate_slot, "change_tip_z")).grid(row=4, column=3, sticky="e")
        
        tk.Label(z_height_frame, text="Drop tip:").grid(row=5, column=0, sticky="w")
        self.drop_tip_height_entry = tk.Entry(z_height_frame, width=5)
        self.drop_tip_height_entry.grid(row=5, column=1)
        tk.Button(z_height_frame, text="set", command=partial(self.calibrate_slot, "drop_tip_z")).grid(row=5, column=3, sticky="e")

        # Move to Coordinates Section
        move_frame = tk.Frame(right_panel)
        move_frame.pack(anchor="w", pady=5)

        tk.Label(move_frame, text="Move to (X,Y,Z):").grid(row=0, column=0, sticky="w")
        self.x_entry = tk.Entry(move_frame, width=5)
        self.x_entry.grid(row=0, column=1)
        self.y_entry = tk.Entry(move_frame, width=5)
        self.y_entry.grid(row=0, column=2)
        self.z_entry = tk.Entry(move_frame, width=5)
        self.z_entry.grid(row=0, column=3)
        tk.Button(move_frame, text="Move to Coordinates", command=self.move_to_coordinates).grid(row=0, column=4)

        # Configuration Load Buttons
        config_button_frame = tk.Frame(right_panel)
        config_button_frame.pack(anchor="w", pady=5)

        tk.Button(config_button_frame, text="Import Configuration", command=self.gui_import_export.import_config).grid(row=0, column=0)
        tk.Button(config_button_frame, text="Export Configuration", command=self.gui_import_export.export_config).grid(row=0, column=1)
        tk.Button(config_button_frame, text="Apply Configuration", command=self.load_new_config).grid(row=0, column=2)

        # Home XYZ button
        tk.Button(move_frame, text="Home", command=self.printer_controller.home).grid(row=0, column=5)

        # HOME E button
        tk.Button(move_frame, text="Home E", command=self.open_calibrate_tool).grid(row=0, column=6)

        # Execution Controls
        controls_frame = tk.Frame(self)
        controls_frame.pack(side="bottom", pady=10)
        self.stop_button = tk.Button(controls_frame, text="STOP", fg="red", command=self.stop_state_machine_execution)
        self.stop_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(controls_frame, text="Reset State", command=self.reset_state)
        self.reset_button.pack(side="left", padx=5)

        self.run_button = tk.Button(controls_frame, text="Run", fg="green", command=self.run_state_machine_execution)
        self.run_button.pack(side="left", padx=5)

        self.probes_rows_entry.insert(0, 5)
        self.probes_columns_entry.insert(0, 5)

        self.probe_tl_x_entry.insert(0, 42)
        self.probe_tl_y_entry.insert(0, 10)
        self.probe_tr_x_entry.insert(0, 250)
        self.probe_tr_y_entry.insert(0, 10)
        self.probe_bl_x_entry.insert(0, 42)
        self.probe_bl_y_entry.insert(0, 150)
        self.probe_br_x_entry.insert(0, 250)
        self.probe_br_y_entry.insert(0, 150)

        self.tips_rows_entry.insert(0, 5)
        self.tips_columns_entry.insert(0, 5)

        self.tip_tl_x_entry.insert(0, 200)
        self.tip_tl_y_entry.insert(0, 200)
        self.tip_tr_x_entry.insert(0, 280)
        self.tip_tr_y_entry.insert(0, 200)
        self.tip_bl_x_entry.insert(0, 200)
        self.tip_bl_y_entry.insert(0, 280)
        self.tip_br_x_entry.insert(0, 280)
        self.tip_br_y_entry.insert(0, 280)
        
        self.active_probe_slots_entry.insert(0, 25)
        self.active_tip_slots_entry.insert(0, 25)

        self.refilling_tank_x_entry.insert(0, 120)
        self.refilling_tank_y_entry.insert(0, 250)
        self.disposal_tank_x_entry.insert(0, 40)
        self.disposal_tank_y_entry.insert(0, 250)

        self.safe_z_height_entry.insert(0, 50)
        self.dispensing_height_entry.insert(0, 40)
        self.change_tip_height_entry.insert(0, 40)
        self.drop_tip_height_entry.insert(0, 40)
        self.refilling_height_entry.insert(0, 40)

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
        print("LOAD NEW CONFIG")
        try:
            probes_rows = int(self.probes_rows_entry.get())
            probes_columns = int(self.probes_columns_entry.get())
            probes_top_left_x = float(self.probe_tl_x_entry.get())
            probes_top_left_y = float(self.probe_tl_y_entry.get())
            probes_top_right_x = float(self.probe_tr_x_entry.get())
            probes_top_right_y = float(self.probe_tr_y_entry.get())
            probes_bottom_left_x = float(self.probe_bl_x_entry.get())
            probes_bottom_left_y = float(self.probe_bl_y_entry.get())
            probes_bottom_right_x = float(self.probe_br_x_entry.get())
            probes_bottom_right_y = float(self.probe_br_y_entry.get())

            tips_rows = int(self.tips_rows_entry.get())
            tips_columns = int(self.tips_columns_entry.get())
            tips_top_left_x = float(self.tip_tl_x_entry.get())
            tips_top_left_y = float(self.tip_tl_y_entry.get())
            tips_top_right_x = float(self.tip_tr_x_entry.get())
            tips_top_right_y = float(self.tip_tr_y_entry.get())
            tips_bottom_left_x = float(self.tip_bl_x_entry.get())
            tips_bottom_left_y = float(self.tip_bl_y_entry.get())
            tips_bottom_right_x = float(self.tip_br_x_entry.get())
            tips_bottom_right_y = float(self.tip_br_y_entry.get())

            refilling_tank_x = float(self.refilling_tank_x_entry.get())
            refilling_tank_y = float(self.refilling_tank_y_entry.get())
            disposal_tank_x = float(self.disposal_tank_x_entry.get())
            disposal_tank_y = float(self.disposal_tank_y_entry.get())

            probes_active_slots = int(self.active_probe_slots_entry.get())
            tips_active_slots = int(self.active_tip_slots_entry.get())

            safe_z = float(self.safe_z_height_entry.get())
            dispensing_z = float(self.dispensing_height_entry.get())
            change_tip_z = float(self.change_tip_height_entry.get())
            drop_tip_z = float(self.drop_tip_height_entry.get())
            refilling_z = float(self.refilling_height_entry.get())


            # Update ProbeGrid
            self.bed_controller.make_new_grid(
                probes_rows=probes_rows,
                probes_columns=probes_columns,
                probes_top_left= (probes_top_left_x, probes_top_left_y),
                probes_top_right = (probes_top_right_x, probes_top_right_y),
                probes_bottom_left = (probes_bottom_left_x, probes_bottom_left_y),
                probes_bottom_right=(probes_bottom_right_x, probes_bottom_right_y),
                tips_rows=tips_rows,
                tips_columns=tips_columns,
                tips_top_left=(tips_top_left_x, tips_top_left_y),
                tips_top_right=(tips_top_right_x, tips_top_right_y),
                tips_bottom_left=(tips_bottom_left_x, tips_bottom_left_y),
                tips_bottom_right=(tips_bottom_right_x, tips_bottom_right_y),
                refilling_tank=(refilling_tank_x, refilling_tank_y),
                disposal_tank=(disposal_tank_x, disposal_tank_y),
                probes_number=probes_active_slots,
                tips_number=tips_active_slots,
                safe_z = safe_z,
                dispensing_z = dispensing_z,
                change_tip_z = change_tip_z,
                drop_tip_z = drop_tip_z,
                refilling_z = refilling_z
            )

            self.gui_grid_visualization.draw_tank_position()
            self.gui_grid_visualization.draw_disposal_tank_position()

            messagebox.showinfo("Load Config", "New configuration loaded!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for configuration settings.")
    
    def refresh_display(self):
        """
        Refresh the display to show the current state of the grid and tool position. Do it every second.
        # # """
        # print(f"Refreshing display, tool position -> X: {self.printer_controller.curr_x}, Y: {self.printer_controller.curr_y}")
        self.gui_grid_visualization.draw_grid(grid = self.bed_controller.probes,
                                              rows = self.bed_controller.probes_rows,
                                              columns = self.bed_controller.probes_columns,
                                              outline_color = "black",
                                              tag="probes",
                                              taken_key="filled")

        self.gui_grid_visualization.draw_grid(grid = self.bed_controller.tips,
                                              rows = self.bed_controller.tips_rows,
                                              columns = self.bed_controller.tips_columns,
                                              outline_color = "red",
                                              tag="tips",
                                              taken_key="taken")
        self.gui_grid_visualization.draw_tool_position()
        self.after(300, self.refresh_display)
        
    def refresh_tool_position(self):
        """
        Refresh the tool position by sending request through printer controller Do it every 500 ms.
        """
        self.printer_controller.update_current_coordinates()
        self.after(400, self.refresh_tool_position)

    def calibrate_slot(self, slot: str):
        """
        Calibrate the slot with the specified name.
        1. Update position. (X,Y,Z)
        2. Parse the current position to the slot coordintaes field

        :param slot: Name of the slot to calibrate.
        """
        print(f"Calibrating slot: {slot}")
        self.printer_controller.update_current_coordinates()
        if slot == "probe-top-left":
            self.probe_tl_x_entry.delete(0, tk.END)
            self.probe_tl_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.probe_tl_y_entry.delete(0, tk.END)
            self.probe_tl_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "probe-top-right":
            self.probe_tr_x_entry.delete(0, tk.END)
            self.probe_tr_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.probe_tr_y_entry.delete(0, tk.END)
            self.probe_tr_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "probe-bottom-left":
            self.probe_bl_x_entry.delete(0, tk.END)
            self.probe_bl_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.probe_bl_y_entry.delete(0, tk.END)
            self.probe_bl_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "probe-bottom-right":
            self.probe_br_x_entry.delete(0, tk.END)
            self.probe_br_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.probe_br_y_entry.delete(0, tk.END)
            self.probe_br_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "tip-top-left":
            self.tip_tl_x_entry.delete(0, tk.END)
            self.tip_tl_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.tip_tl_y_entry.delete(0, tk.END)
            self.tip_tl_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "tip-top-right":
            self.tip_tr_x_entry.delete(0, tk.END)
            self.tip_tr_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.tip_tr_y_entry.delete(0, tk.END)
            self.tip_tr_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "tip-bottom-left":
            self.tip_bl_x_entry.delete(0, tk.END)
            self.tip_bl_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.tip_bl_y_entry.delete(0, tk.END)
            self.tip_bl_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "tip-bottom-right":
            self.tip_br_x_entry.delete(0, tk.END)
            self.tip_br_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.tip_br_y_entry.delete(0, tk.END)
            self.tip_br_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "refilling_tank":
            self.refilling_tank_x_entry.delete(0, tk.END)
            self.refilling_tank_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.refilling_tank_y_entry.delete(0, tk.END)
            self.refilling_tank_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "disposal_tank":
            self.disposal_tank_x_entry.delete(0, tk.END)
            self.disposal_tank_x_entry.insert(0, str(self.printer_controller.curr_x))
            self.disposal_tank_y_entry.delete(0, tk.END)
            self.disposal_tank_y_entry.insert(0, str(self.printer_controller.curr_y))
        elif slot == "safe_z":
            self.safe_z_height_entry.delete(0, tk.END)
            self.safe_z_height_entry.insert(0, str(self.printer_controller.curr_z))
        elif slot == "refilling_z":
            self.refilling_height_entry.delete(0, tk.END)
            self.refilling_height_entry.insert(0, str(self.printer_controller.curr_z))
        elif slot == "dispensing_z":
            self.dispensing_height_entry.delete(0, tk.END)
            self.dispensing_height_entry.insert(0, str(self.printer_controller.curr_z))
        elif slot == "change_tip_z":
            self.change_tip_height_entry.delete(0, tk.END)
            self.change_tip_height_entry.insert(0, str(self.printer_controller.curr_z))
        elif slot == "drop_tip_z":
            self.drop_tip_height_entry.delete(0, tk.END)
            self.drop_tip_height_entry.insert(0, str(self.printer_controller.curr_z))

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
        
    def open_calibrate_tool(self):
        # Create and display the manual movement window
        manual_movement_window = CalibrateToolWindow(self.printer_controller.tool_controller)
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
        if self.stop_flag.is_set():
            return

        state_completed = self.state_machine.poll()
        self.after(self.state_machine_polling_interval, self.start_state_machine_polling)

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
        self.printer_controller.emergency_stop()
        print("Execution stopped.")
