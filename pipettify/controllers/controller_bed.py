# This file implements a class that stores info about the grid for our probes
# It knows how many probes do we have and how big is the grid, it also knows the current state of the probe
# (filled or not). This class is used by our GUI to display the current state of the grid and by the sequence controller
# to move to the next probe.

import numpy as np

class BedController:
    """
    Class containg everything related to bed.
    1. Probe grid definition
    2. Z levels for different processes
    3. TODO
    """
    def __init__(self):
        """
        Initialize an empty ProbeGrid with dynamic grid size and probes.
        """
        self.rows = 0
        self.columns = 0
        self.num_probes = 0
        self.probes = {}  # Dictionary to store probe states: {(row, col): {"filled": False, "coordinates": (x, y)}}
        self.top_left = (0, 0)  # Coordinates of the top-left corner of the grid
        self.top_right = (0, 0)  # Coordinates of the top-right corner
        self.bottom_left = (0, 0)  # Coordinates of the bottom-left corner
        self.bottom_right = (0, 0)  # Coordinates of the bottom-right corner
        self.probe_diameter = 0  # Diameter of the probes
        
        # Define cooordinates and z values
        self.safe_z = 35  # Safe Z height for the end effector
        
        self.refilling_tank = (0, 0)  # X, Y center coordinates of the refilling tank
        self.refilling_tank_z = 30  # Z coordinate that tool needs to achieve to begin refilling
        
        self.dispensing_z = 30  # Z coordinate that tool needs to achieve to begin dispensing

    def make_new_grid(self,
                      rows,
                      columns,
                      top_left,
                      top_right,
                      bottom_left,
                      bottom_right,
                      refilling_tank,
                      probe_diameter,
                      num_probes):
        """
        Make a new grid and initialize probes accordingly.

        :param rows: Number of rows in the grid.
        :param columns: Number of columns in the grid.
        :param top_left: Tuple (x, y) of the top-left corner coordinates.
        :param bottom_right: Tuple (x, y) of the bottom-right corner coordinates.
        :param probe_diameter: Diameter of the probes.
        :param num_probes: Number of active probes.
        """
        self.rows = rows
        self.columns = columns
        self.top_left = top_left
        self.top_right = top_right
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right
        self.refilling_tank = refilling_tank
        self.probe_diameter = probe_diameter
        self.num_probes = min(num_probes, rows * columns)
        self._initialize_probes()

    def _initialize_probes(self):
        """
        Initialize or update the probe grid based on the current attributes.
        """
        self.probes = {}
        count = 0
        for row in range(self.rows):
            for col in range(self.columns):
                if count < self.num_probes:
                    self.probes[(row, col)] = {"filled": False, "coordinates": None}
                    count += 1
                else:
                    break
        self._calculate_probes_coordinates()

    def _calculate_probes_coordinates(self):
        """
        Calculate coordinates for all probes in an irregular grid (grid lake).
        The probes are evenly distributed within the quadrilateral defined by the four corners.
        """
        # Extract corner coordinates
        top_left_x, top_left_y = self.top_left
        top_right_x, top_right_y = self.top_right
        bottom_left_x, bottom_left_y = self.bottom_left
        bottom_right_x, bottom_right_y = self.bottom_right

        # top_x_diff = top_right_x - top_left_x

        for row in range(self.rows):
            for col in range(self.columns):
                # Calculate interpolation factors
                t = row / (self.rows - 1) if self.rows > 1 else 0
                u = col / (self.columns - 1) if self.columns > 1 else 0

                # Interpolate top edge
                top_x = top_left_x + u * (top_right_x - top_left_x)
                top_y = top_left_y + u * (top_right_y - top_left_y)

                # Interpolate bottom edge
                bottom_x = bottom_left_x + u * (bottom_right_x - bottom_left_x)
                bottom_y = bottom_left_y + u * (bottom_right_y - bottom_left_y)

                # Interpolate between top and bottom edges
                probe_x = top_x + t * (bottom_x - top_x)
                probe_y = top_y + t * (bottom_y - top_y)

                # Assign the calculated coordinates to the probe
                if (row, col) in self.probes:
                    self.probes[(row, col)]["coordinates"] = (probe_x, probe_y)


    def update_probe_state(self, row, column, new_state):
        """
        Update the state of a specific probe.

        :param row: Row index of the probe.
        :param column: Column index of the probe.
        :param new_state: New state for the probe (True = filled, False = not filled).
        """
        if (row, column) not in self.probes:
            raise KeyError(f"No probe exists at position ({row}, {column}).")
        self.probes[(row, column)]["filled"] = new_state

    def get_probe_state(self, row, column):
        """
        Get the state of a specific probe.

        :param row: Row index of the probe.
        :param column: Column index of the probe.
        :return: State of the probe (True = filled, False = not filled).
        """
        if (row, column) not in self.probes:
            raise KeyError(f"No probe exists at position ({row}, {column}).")
        return self.probes[(row, column)]["filled"]

    def next_probe(self):
        """
        Find the next unfilled probe based on the grid layout.

        :return: Tuple (row, column) of the next unfilled probe, or None if all probes are filled.
        """
        for position, probe in self.probes.items():
            if not probe["filled"]:
                return position
        return None  # All probes are filled

    def is_configured(self):
        """
        Check if the grid has been configured.

        :return: True if the grid has been configured, False otherwise.
        """
        return self.rows > 0 and self.columns > 0 and self.num_probes > 0
