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
        self.serial = None

    def configure_serial_connection(self, port='/dev/ttyUSB0', baudrate=115200):
        """
        Connect to printer using Serial interface
        If Serial object cannot be set, yeild an error.
        """
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        if ser is None:
            raise Exception('Serial connection could not be established.')

        print(f"Serial connection established on port {port} with baudrate {baudrate}")
        self.serial = ser

    def send_gcode(self, command):
        self.serial.write((command + '\n').encode())
        response = self.serial.readline().decode().strip()
        return response

    def update_current_coordinates(self):
        # TODO - IT IS NOT WORKING !!!
        """
        Update current 3D printer coordinates.
        """
        self.send_gcode('M114')
        response = self.serial.readlines()
        print(f"Response -> {response}")
        self.curr_x = 1
        self.curr_y = 2
        self.curr_z = 3

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
        command = f"G1 X{x} Y{y} Z{z} F500"  # G-code to move to specified X, Y, Z with a feed rate of 1500 mm/min
        self.send_gcode(command)

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
            send_gcode(command)
