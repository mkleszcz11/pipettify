import time

from pipettify.controllers.controller_bed import BedController

class EndEffectorController:
    """
    End effector controller class. This class is responsible for controlling the end effector.
    """
    def __init__(self, send_gcode_func, bed_controller: BedController):
        self.send_gcode = send_gcode_func
        self.bed_controller = bed_controller
        self.neutral_position = self._get_absolute_motor_position()
        self.state = "neutral"  # Track the end effector state (push_button_pressed, tip_button_pressed, neutral)
        self.last_operation = None  # Track the last operation performed ("drop_tip", "refill")

    def press_push_button(self, timeout=10, poll_interval=0.1):
        """
        Press push button. It should keep the button pressed.
        """
        target_position = self._calculate_button_press_position("push")
        return self._move_and_wait(target_position, timeout, poll_interval)

    def press_drop_tip_button(self, timeout=10, poll_interval=0.1):
        """
        Press drop tip button.
        """
        target_position = self._calculate_button_press_position("drop_tip")
        return self._move_and_wait(target_position, timeout, poll_interval)
    
    def execute_drop_tip(self, timeout=10, poll_interval=0.1):
        """
        Perform drop tip operation. This means pressing drop tip button and getting back to neutral.
        """
        if not self.press_drop_tip_button(timeout, poll_interval):
            print("Failed to press drop tip button.")
            return False
        
        # Return to neutral after pressing drop tip button
        if not self.move_to_neutral(timeout, poll_interval):
            print("Failed to return to neutral after dropping tip.")
            return False
        
        print("Drop tip operation completed.")
        return True
    
    def execute_refill(self, timeout=10, poll_interval=0.1): # TODO -> NO QA
        """
        Perform refill operation. This means pressing push button and getting back to neutral.
        """
        if not self.press_push_button(timeout, poll_interval):
            print("Failed to press push button.")
            return False
        
        # Return to neutral after pressing push button
        if not self.move_to_neutral(timeout, poll_interval):
            print("Failed to return to neutral after refilling.")
            return False

        print("Refill operation completed.")
        return True
    
    def execute_dispense(self, probe, timeout=10, poll_interval=0.1): # TODO -> NO QA
        """
        Perform dispense operation. This means pressing push button and getting back to neutral.
        """
        # if not self.press_push_button(timeout, poll_interval):
        #     print("Failed to press push button.")
        #     return False
        
        # # Return to neutral after pressing push button
        # if not self.move_to_neutral(timeout, poll_interval):
        #     print("Failed to return to neutral after dispensing.")
        #     return False

        self.bed_controller.update_probe_state(probe[0], probe[1], True)
        print("Dispense operation completed.")
        return True

    def move_to_neutral(self, timeout=10, poll_interval=0.1):
        """
        No matter the motor position, move back to neutral. Choose the correct movement direction.
        """
        return self._move_and_wait(self.neutral_position, timeout, poll_interval)

    def _move_to_position(self, position):
        """
        Move the motor to the specified position.
        """
        print(f"Moving motor to position: {position} mm")
        self.send_gcode("M302 P1")  # Enable cold extrusion
        self.send_gcode("G92 E0")  # Reset extruder position to 0
        self.send_gcode(f"G1 E{position} F500")  # Move extruder motor by 'position' (linear mm)
        time.sleep(0.5)  # Simulate motor movement command sending
        return True

    def _move_and_wait(self, target_position, timeout=10, poll_interval=0.1):
        """
        Move the motor to the specified target position and wait until it reaches the position.
        """
        self._move_to_position(target_position)
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._is_at_position(target_position):
                print(f"Reached target position: {target_position} mm")
                return True
            time.sleep(poll_interval)
        
        print(f"Timeout while moving to target position: {target_position} mm")
        return False

    def _is_at_position(self, target_position, tolerance=0.1):
        """
        Check if the motor has reached the specified target position within a given tolerance.
        """
        current_position = self._get_absolute_motor_position()
        return abs(current_position - target_position) <= tolerance

    def _calculate_button_press_position(self, button_type):
        """
        Calculate the target position for the specified button press type.
        """
        if button_type == "push":
            return self.neutral_position + 5  # Example: 5 mm for push button
        elif button_type == "drop_tip":
            return self.neutral_position - 5  # Example: -5 mm for drop tip button
        else:
            raise ValueError(f"Unknown button type: {button_type}")

    def _get_relative_motor_position(self):
        """
        Get current motor position relative to the neutral position.
        """
        current_position = self._get_absolute_motor_position()
        return current_position - self.neutral_position

    def _get_absolute_motor_position(self):
        """
        Get current absolute motor position.
        Simulated example - Replace with real sensor data.
        """
        # Simulated motor position (e.g., replace with actual sensor reading)
        return 0.0

    def get_position(self):
        """
        Get the current state of the end effector (push_button_pressed, tip_button_pressed, neutral).
        """
        current_position = self._get_relative_motor_position()
        if abs(current_position) < 1:  # Close to neutral
            return "neutral"
        elif current_position > 1: # TODO
            return "push_button_pressed"
        elif current_position < -1: # TODO
            return "tip_button_pressed"
