import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

class ConfigImportExport:
    def __init__(self, interface):
        """
        Initialize the import/export utility.
        :param interface: Reference to the PrinterGUI instance for accessing field values.
        """
        self.interface = interface

    def export_config(self):
        """
        Export the current configuration to a JSON file.
        """
        config = {
            "bed_width": self.interface.bed_width_entry.get(),
            "bed_height": self.interface.bed_height_entry.get(),
            "probes_rows": self.interface.probes_rows_entry.get(),
            "probes_columns": self.interface.probes_columns_entry.get(),
            "probes": {
                "top_left": (self.interface.probe_tl_x_entry.get(), self.interface.probe_tl_y_entry.get()),
                "top_right": (self.interface.probe_tr_x_entry.get(), self.interface.probe_tr_y_entry.get()),
                "bottom_left": (self.interface.probe_bl_x_entry.get(), self.interface.probe_bl_y_entry.get()),
                "bottom_right": (self.interface.probe_br_x_entry.get(), self.interface.probe_br_y_entry.get()),
            },
            "active_probe_slots": self.interface.active_probe_slots_entry.get(),
            "tips_rows": self.interface.tips_rows_entry.get(),
            "tips_columns": self.interface.tips_columns_entry.get(),
            "tips": {
                "top_left": (self.interface.tip_tl_x_entry.get(), self.interface.tip_tl_y_entry.get()),
                "top_right": (self.interface.tip_tr_x_entry.get(), self.interface.tip_tr_y_entry.get()),
                "bottom_left": (self.interface.tip_bl_x_entry.get(), self.interface.tip_bl_y_entry.get()),
                "bottom_right": (self.interface.tip_br_x_entry.get(), self.interface.tip_br_y_entry.get()),
            },
            "active_tip_slots": self.interface.active_tip_slots_entry.get(),
            "refilling_tank": (self.interface.refilling_tank_x_entry.get(), self.interface.refilling_tank_y_entry.get()),
            "disposal_tank": (self.interface.disposal_tank_x_entry.get(), self.interface.disposal_tank_y_entry.get()),
            "z_heights": {
                "safe_z": self.interface.safe_z_height_entry.get(),
                "dispensing_z": self.interface.dispensing_height_entry.get(),
                "change_tip_z": self.interface.change_tip_height_entry.get(),
                "drop_tip_z": self.interface.drop_tip_height_entry.get(),
                "refilling_z": self.interface.refilling_height_entry.get(),
            }
        }

        # Save to a file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Configuration"
        )
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    json.dump(config, file, indent=4)
                messagebox.showinfo("Export Configuration", "Configuration exported successfully!")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export configuration: {e}")

    def import_config(self):
        """
        Import a configuration from a JSON file and update GUI fields.
        """
        # Load from a file
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Configuration"
        )
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    config = json.load(file)

                # Update GUI fields
                self.interface.bed_width_entry.delete(0, tk.END)
                self.interface.bed_width_entry.insert(0, config["bed_width"])
                self.interface.bed_height_entry.delete(0, tk.END)
                self.interface.bed_height_entry.insert(0, config["bed_height"])

                self.interface.probes_rows_entry.delete(0, tk.END)
                self.interface.probes_rows_entry.insert(0, config["probes_rows"])
                self.interface.probes_columns_entry.delete(0, tk.END)
                self.interface.probes_columns_entry.insert(0, config["probes_columns"])

                self.interface.probe_tl_x_entry.delete(0, tk.END)
                self.interface.probe_tl_x_entry.insert(0, config["probes"]["top_left"][0])
                self.interface.probe_tl_y_entry.delete(0, tk.END)
                self.interface.probe_tl_y_entry.insert(0, config["probes"]["top_left"][1])

                self.interface.probe_tr_x_entry.delete(0, tk.END)
                self.interface.probe_tr_x_entry.insert(0, config["probes"]["top_right"][0])
                self.interface.probe_tr_y_entry.delete(0, tk.END)
                self.interface.probe_tr_y_entry.insert(0, config["probes"]["top_right"][1])

                self.interface.probe_bl_x_entry.delete(0, tk.END)
                self.interface.probe_bl_x_entry.insert(0, config["probes"]["bottom_left"][0])
                self.interface.probe_bl_y_entry.delete(0, tk.END)
                self.interface.probe_bl_y_entry.insert(0, config["probes"]["bottom_left"][1])

                self.interface.probe_br_x_entry.delete(0, tk.END)
                self.interface.probe_br_x_entry.insert(0, config["probes"]["bottom_right"][0])
                self.interface.probe_br_y_entry.delete(0, tk.END)
                self.interface.probe_br_y_entry.insert(0, config["probes"]["bottom_right"][1])

                self.interface.active_probe_slots_entry.delete(0, tk.END)
                self.interface.active_probe_slots_entry.insert(0, config["active_probe_slots"])

                self.interface.tips_rows_entry.delete(0, tk.END)
                self.interface.tips_rows_entry.insert(0, config["tips_rows"])
                self.interface.tips_columns_entry.delete(0, tk.END)
                self.interface.tips_columns_entry.insert(0, config["tips_columns"])

                self.interface.tip_tl_x_entry.delete(0, tk.END)
                self.interface.tip_tl_x_entry.insert(0, config["tips"]["top_left"][0])
                self.interface.tip_tl_y_entry.delete(0, tk.END)
                self.interface.tip_tl_y_entry.insert(0, config["tips"]["top_left"][1])

                self.interface.tip_tr_x_entry.delete(0, tk.END)
                self.interface.tip_tr_x_entry.insert(0, config["tips"]["top_right"][0])
                self.interface.tip_tr_y_entry.delete(0, tk.END)
                self.interface.tip_tr_y_entry.insert(0, config["tips"]["top_right"][1])

                self.interface.tip_bl_x_entry.delete(0, tk.END)
                self.interface.tip_bl_x_entry.insert(0, config["tips"]["bottom_left"][0])
                self.interface.tip_bl_y_entry.delete(0, tk.END)
                self.interface.tip_bl_y_entry.insert(0, config["tips"]["bottom_left"][1])

                self.interface.tip_br_x_entry.delete(0, tk.END)
                self.interface.tip_br_x_entry.insert(0, config["tips"]["bottom_right"][0])
                self.interface.tip_br_y_entry.delete(0, tk.END)
                self.interface.tip_br_y_entry.insert(0, config["tips"]["bottom_right"][1])

                self.interface.refilling_tank_x_entry.delete(0, tk.END)
                self.interface.refilling_tank_x_entry.insert(0, config["refilling_tank"][0])
                self.interface.refilling_tank_y_entry.delete(0, tk.END)
                self.interface.refilling_tank_y_entry.insert(0, config["refilling_tank"][1])

                self.interface.disposal_tank_x_entry.delete(0, tk.END)
                self.interface.disposal_tank_x_entry.insert(0, config["disposal_tank"][0])
                self.interface.disposal_tank_y_entry.delete(0, tk.END)
                self.interface.disposal_tank_y_entry.insert(0, config["disposal_tank"][1])
                
                self.interface.active_tip_slots_entry.delete(0, tk.END)
                self.interface.active_tip_slots_entry.insert(0, config["active_tip_slots"])

                self.interface.safe_z_height_entry.delete(0, tk.END)
                self.interface.safe_z_height_entry.insert(0, config["z_heights"]["safe_z"])
                self.interface.dispensing_height_entry.delete(0, tk.END)
                self.interface.dispensing_height_entry.insert(0, config["z_heights"]["dispensing_z"])
                self.interface.change_tip_height_entry.delete(0, tk.END)
                self.interface.change_tip_height_entry.insert(0, config["z_heights"]["change_tip_z"])
                self.interface.drop_tip_height_entry.delete(0, tk.END)
                self.interface.drop_tip_height_entry.insert(0, config["z_heights"]["drop_tip_z"])
                self.interface.refilling_height_entry.delete(0, tk.END)
                self.interface.refilling_height_entry.insert(0, config["z_heights"]["refilling_z"])

                messagebox.showinfo("Import Configuration", "Configuration imported successfully!")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import configuration: {e}")
