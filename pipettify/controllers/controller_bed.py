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
        self.probes_rows = 0
        self.probes_columns = 0

        self.probes_number = 0
        self.probes = {}  # Dictionary to store probe states: {(row, col): {"filled": False, "coordinates": (x, y)}}
        self.probes_top_left = (0, 0)  # Coordinates of the top-left corner of the grid
        self.probes_top_right = (0, 0)  # Coordinates of the top-right corner
        self.probes_bottom_left = (0, 0)  # Coordinates of the bottom-left corner
        self.probes_bottom_right = (0, 0)  # Coordinates of the bottom-right corner
        
        self.tips_rows = 0
        self.tips_columns = 0

        self.tips_number = 0  # Number of tips in the tip rack
        self.tips = {}  # Dictionary to store tip states: {(row, col): {"taken": False, "coordinates": (x, y)}}
        self.tips_top_left = (0, 0)  # Coordinates of the top-left corner of the tip rack
        self.tips_top_right = (0, 0)  # Coordinates of the top-right corner
        self.tips_bottom_left = (0, 0)  # Coordinates of the bottom-left corner
        self.tips_bottom_right = (0, 0)  # Coordinates of the bottom-right corner
        self.tip_diameter = 0  # Diameter of the tips
        
        self.refilling_tank = (0, 0)  # X, Y center coordinates of the refilling tank        
        self.disposal_tank = (0, 0)  # X, Y center coordinates of the disposal tank
        
        # Define cooordinates and z values
        self.safe_z = 35  # Safe Z height for the end effector -> XY travel Z
        self.dispensing_z = 30  # Z coordinate that tool needs to achieve to begin dispensing
        self.change_tip_z = 25  # Z coordinate that tool needs to achieve to change the tip (take a new one)
        self.drop_tip_z = 40    # Z coordinate that tool needs to achieve to drop the tip
        self.refilling_z = 30

        
    def make_new_grid(self,
                      probes_rows,
                      probes_columns,
                      probes_top_left,
                      probes_top_right,
                      probes_bottom_left,
                      probes_bottom_right,
                      tips_rows,
                      tips_columns,
                      tips_top_left,
                      tips_top_right,
                      tips_bottom_left,
                      tips_bottom_right,
                      refilling_tank,
                      disposal_tank,
                      probes_number,
                      tips_number,
                      safe_z,
                      change_tip_z,
                      refilling_z,
                      dispensing_z,
                      drop_tip_z):
        """
        Make a new grid and initialize probes accordingly.

        :param rows: Number of rows in the grid.
        :param columns: Number of columns in the grid.
        :param top_left: Tuple (x, y) of the top-left corner coordinates.
        :param bottom_right: Tuple (x, y) of the bottom-right corner coordinates.
        :param num_probes: Number of active probes.
        """
        self.probes_rows = probes_rows
        self.probes_columns = probes_columns

        self.probes_top_left = probes_top_left
        self.probes_top_right = probes_top_right
        self.probes_bottom_left = probes_bottom_left
        self.probes_bottom_right = probes_bottom_right
        
        self.tips_rows = tips_rows
        self.tips_columns = tips_columns

        self.tips_top_left = tips_top_left
        self.tips_top_right = tips_top_right
        self.tips_bottom_left = tips_bottom_left
        self.tips_bottom_right = tips_bottom_right

        self.refilling_tank = refilling_tank
        self.disposal_tank = disposal_tank
        
        self.probes_number = min(probes_number, probes_rows * probes_columns)
        self.tips_number = min(tips_number, tips_rows * tips_columns)
        
        self.safe_z = safe_z
        self.dispensing_z = dispensing_z
        self.change_tip_z = change_tip_z
        self.drop_tip_z = drop_tip_z
        self.refilling_z = refilling_z

        self._initialize_probes()
        self._initialize_tips()

    def _initialize_probes(self):
        """
        Initialize or update the probe grid based on the current attributes.
        """
        self.probes = {}
        count = 0
        for row in range(self.probes_rows):
            for col in range(self.probes_columns):
                if count < self.probes_number:
                    self.probes[(row, col)] = {"filled": False, "coordinates": None}
                    count += 1
                else:
                    break
        self._calculate_grid_coordinates(self.probes,
                                         self.probes_top_left,
                                         self.probes_top_right,
                                         self.probes_bottom_left,
                                         self.probes_bottom_right,
                                         self.probes_rows,
                                         self.probes_columns)
        
    def _initialize_tips(self):
        """
        Initialize or update the tip rack based on the current attributes.
        """
        self.tips = {}
        count = 0
        for row in range(self.tips_rows):
            for col in range(self.tips_columns):
                if count < self.tips_number:
                    self.tips[(row, col)] = {"taken": False, "coordinates": None}
                    count += 1
                else:
                    break
        self._calculate_grid_coordinates(self.tips,
                                         self.tips_top_left,
                                         self.tips_top_right,
                                         self.tips_bottom_left,
                                         self.tips_bottom_right,
                                         self.tips_rows,
                                         self.tips_columns)

    def _calculate_grid_coordinates(self, grid, top_left, top_right, bottom_left, bottom_right, rows, columns):
        """
        Calculate coordinates for all probes in an irregular grid.
        The probes are evenly distributed within the quadrilateral defined by the four corners.
        """
        # Extract corner coordinates
        top_left_x, top_left_y = top_left
        top_right_x, top_right_y = top_right
        bottom_left_x, bottom_left_y = bottom_left
        bottom_right_x, bottom_right_y = bottom_right

        # top_x_diff = top_right_x - top_left_x

        for row in range(rows):
            for col in range(columns):
                # Calculate interpolation factors
                t = row / (rows - 1) if rows > 1 else 0
                u = col / (columns - 1) if columns > 1 else 0

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
                if (row, col) in grid:
                    grid[(row, col)]["coordinates"] = (probe_x, probe_y)


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

    def is_configured(self): # TODO -> add check for tip grid
        """
        Check if the grid has been configured.

        :return: True if the grid has been configured, False otherwise.
        """
        return self.probes_rows > 0 and self.probes_columns > 0 and self.probes_number > 0

    ########
    # TODO -> MERGE WITH FUNCTIONS ABOVE
    ########
    def update_tip_state(self, row, column, new_state):
        """
        Update the state of a specific tip.

        :param row: Row index of the tip.
        :param column: Column index of the tip.
        :param new_state: New state for the tip (True = filled, False = not filled).
        """
        if (row, column) not in self.tips:
            raise KeyError(f"No tip exists at position ({row}, {column}).")
        self.tips[(row, column)]["taken"] = new_state

    def get_tip_state(self, row, column):
        """
        Get the state of a specific tip.

        :param row: Row index of the tip.
        :param column: Column index of the tip.
        :return: State of the tip (True = taken, False = not taken).
        """
        if (row, column) not in self.tips:
            raise KeyError(f"No tip exists at position ({row}, {column}).")
        return self.tips[(row, column)]["taken"]

    def next_tip(self):
        """
        Find the next unfilled tip based on the grid layout.

        :return: Tuple (row, column) of the next unfilled tip, or None if all tips are filled.
        """
        for position, tip in self.tips.items():
            if not tip["taken"]:
                return position
        return None  # All tips are taken
