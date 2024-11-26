import serial
import time


class PrinterController:
    """
    Class for controlling 3D printer. To controll the end effector, use end effector class.
    """
    def __init__(self):
        self.curr_x = None
        self.curr_y = None
        self.curr_z = None
        self.max_speed = 500
        self.serial = None

    def configure_serial_connection(self, port='/dev/ttyUSB0', baudrate=115200):
        """
        Connect to printer using Serial interface
        If Serial object cannot be set, yeild an error.
        """
        ser = serial.Serial(port, baudrate, timeout=0)
        time.sleep(2)
        if ser is None:
            raise Exception('Serial connection could not be established.')

        print(f"Serial connection established on port {port} with baudrate {baudrate}")
        self.serial = ser

    def send_gcode(self, command):
        """
        Send a G-code command to the printer and return the response.
        """
        self.serial.write((command + '\n').encode())
        response = self.serial.readline().decode().strip()
        return response

    def update_current_coordinates(self):
        """
        Update current 3D printer coordinates by sending the M114 command
        and parsing the response.
        """
        try:
            # Send the M114 command
            self.serial.write(b'M114\n')
            time.sleep(0.5)  # Wait for the printer to respond

            # Read the response
            response_lines = []
            start_time = time.time()
            timeout = 5  # Timeout in seconds

            while time.time() - start_time < timeout:
                if self.serial.in_waiting > 0:
                    line = self.serial.readline().decode('utf-8').strip()
                    response_lines.append(line)
                    if line == "ok":  # Stop when "ok" is received
                        break
                time.sleep(0.1)

            # # Combine response for debugging
            # response = "\n".join(response_lines)
            # print(f"Full response:\n{response}")

            # Parse the coordinates from the response
            for line in response_lines:
                if 'X:' in line and 'Y:' in line and 'Z:' in line:
                    parts = line.split(' ')
                    self.curr_x = float(next((p[2:] for p in parts if p.startswith('X:')), 0))
                    self.curr_y = float(next((p[2:] for p in parts if p.startswith('Y:')), 0))
                    self.curr_z = float(next((p[2:] for p in parts if p.startswith('Z:')), 0))
                    print(f"Updated Coordinates -> X: {self.curr_x}, Y: {self.curr_y}, Z: {self.curr_z}")
                    return

            # If coordinates are not found
            print("Failed to parse coordinates from the response.")
        except Exception as e:
            print(f"Error while updating coordinates: {e}")

    def print_current_coordinates(self):
        """
        Print current 3D printer coordinates.
        """
        self.update_current_coordinates()
        print(f"Current coordinates: {self.curr_x}, {self.curr_y}, {self.curr_z}")

    def move_to_coordinates(self, x, y, z):
        """
        End effector moves to x,y,z.
        """
        command = "M302 S0"
        self.send_gcode(command)
        command = f"G1 X{x} Y{y} Z{z} F{self.max_speed}"  # G-code to move to specified X, Y, Z with a feed rate of 1500 mm/min
        self.send_gcode(command)
        
    def move_relative(self, dx, dy, dz):
        """
        Move the end effector by the specified amount in each axis.
        """
        command = "M302 S0"
        self.send_gcode(command)  # Allow movement without extruder temperature restrictions

        # Enable relative positioning mode
        command = f"G91"
        self.send_gcode(command)

        # Move by the specified relative distances
        command = f"G1 X{dx} Y{dy} Z{dz} F{self.max_speed}"
        self.send_gcode(command)

        # Return to absolute positioning mode
        command = f"G90"
        self.send_gcode(command)
        
    
    def home(self):
        """
        Home the printer.
        """
        command = "G28"
        self.send_gcode(command)
        self.curr_x = 0.0
        self.curr_y = 0.0
        self.curr_z = 0.0
        

    def play_crazy_frog(self): # TODO - IMPLEMENT
        """
        Play crazy frog using command M300, as it is a melody.
        """
        # Define the melody as a list of tuples (frequency in Hz, duration in ms)
        melody = [
            (659, 200), (784, 200), (659, 200), (659, 200), (880, 200), (659, 200), (587, 200),
            (659, 200), (988, 200), (659, 200), (523, 200), (659, 200), (659, 200), (880, 200),
            (659, 200), (587, 200), (659, 200), (988, 200), (659, 200), (523, 200), (659, 200),
            (659, 200), (880, 200), (659, 200), (587, 200), (659, 200), (988, 200), (659, 200),
            (523, 200), (659, 200), (659, 200), (880, 200), (659, 200), (587, 200), (659, 200),
            (988, 200), (659, 200), (523, 200), (659, 200), (659, 200), (880, 200), (659, 200),
            (587, 200), (659, 200), (988, 200), (659, 200), (523, 200), (659, 200), (659, 200),
            (880, 200), (659, 200), (587, 200), (659, 200), (988, 200), (659, 200), (523, 200)
        ]

        # Send each note to the printer
        for frequency, duration in melody:
            command = f"M300 S{frequency} P{duration} D10"
            self.send_gcode(command)
