import time

from pipettify.controllers.controller_bed import BedController

class EndEffectorController:
    """
    End effector controller class. This class is responsible for controlling the end effector.
    """
    def __init__(self, send_gcode_func, update_current_coordinates, bed_controller: BedController):
        self.send_gcode = send_gcode_func
        self.update_current_coordinates = update_current_coordinates
        self.bed_controller = bed_controller
        self.neutral_position = 0.0
        self.current_position = None
        self.pushed_half_position_diff = -17.5  # -15.5 mm for half push
        self.pushed_position_diff = -30.5       # -31 mm for full push
        self.state = "neutral"  # Track the end effector state (push_button_pressed, tip_button_pressed, neutral)
        self.last_operation = None  # Track the last operation performed ("drop_tip", "refill")

    def press_push_button_half(self, timeout=10, poll_interval=0.1):
        """
        Press push button halfway. It should keep the button pressed halfway.
        """
        # target_position = self._calculate_button_press_position("push")
        result = self._move_and_wait(self.neutral_position + self.pushed_half_position_diff, timeout, poll_interval)
        if result:
            self.state = "push_button_pressed"
        return

    def press_push_button_full(self, timeout=10, poll_interval=0.1):
        """
        Press push button. It should keep the button pressed.
        """
        # target_position = self._calculate_button_press_position("push")
        result = self._move_and_wait(self.neutral_position + self.pushed_position_diff, timeout, poll_interval)
        if result:
            self.state = "push_button_pressed"
        return result

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
        print("EXECUTE REFILL")
        if not self.press_push_button_full(timeout, poll_interval):
            print("Failed to press push button.")
            return False
        
        # Return to neutral after pressing push button
        if not self.move_to_neutral(timeout, poll_interval):
            print("Failed to return to neutral after refilling.")
            return False

        print("Refill operation completed.")
        self.last_operation = "refill"
        return True
    
    def execute_dispense(self, probe, timeout=10, poll_interval=0.1): # TODO -> NO QA
        """
        Perform dispense operation. This means pressing push button and getting back to neutral.
        """
        print(f"EXECUTE DISPENSE on probe {probe}")
    
        # Press the push button to dispense
        if not self.press_push_button_full(timeout, poll_interval):
            print("Failed to press push button for dispensing.")
            return False
        
        # Return to neutral after pressing push button
        if not self.move_to_neutral(timeout, poll_interval):
            print("Failed to return to neutral after dispensing.")
            return False

        # Update the probe state to filled
        self.bed_controller.update_probe_state(probe[0], probe[1], True)

        print(f"Dispense operation completed on probe {probe}.")
        self.last_operation = "dispense"
        return True


    def move_to_neutral(self, timeout=10, poll_interval=0.1):
        """
        No matter the motor position, move back to neutral. Choose the correct movement direction.
        """
        result = self._move_and_wait(self.neutral_position, timeout, poll_interval)
        if result:
            self.state = "neutral"
        return result

    def move_to_position(self, position):
        """
        Move the motor to the specified position.
        """
        print(f"Moving motor to position: {position} mm")
        self.send_gcode("M302 P1")  # Enable cold extrusion
        # self.send_gcode("G92 E0")  # Reset extruder position to 0
        self.send_gcode(f"G1 E{position} F500")  # Move extruder motor by 'position' (linear mm)
        return True

    def _move_and_wait(self, target_position, timeout=10, poll_interval=0.1):
        """
        Move the motor to the specified target position and wait until it reaches the position.
        """
        self.move_to_position(target_position)
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
        # current_position = self._get_absolute_motor_position()
        self._get_absolute_motor_position()
        # print(f"Current position: {self.current_position} | Target position: {target_position} | diff: {abs(self.current_position - target_position)}")
        return abs(self.current_position - target_position) <= tolerance

    def _calculate_button_press_position(self, button_type):
        """
        Calculate the target position for the specified button press type.
        """
        print(f"Neutral position: {self.neutral_position}, type: {type(self.neutral_position)}")
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
        # current_position = self._get_absolute_motor_position()
        return self.current_position - self.neutral_position

    def _get_absolute_motor_position(self):
        """
        Get current absolute motor position by sending the M114 command
        and parsing the response.
        """
        self.update_current_coordinates()
        # try:
        #     # Send M114 to query current positions
        #     response = self.send_gcode("M114")
        #     print(" //////// ")
        #     print(response)
        #     print(" //////// ")
        #     # Parse the response to extract the extruder position (E)
        #     if "E:" in response:
        #         parts = response.split()
        #         for part in parts:
        #             if part.startswith("E:"):
        #                 position = float(part[2:])  # Extract the numeric part
        #                 print(f"Absolute motor position: {position} mm")
        #                 return position

        #     print(f"Failed to parse absolute motor position from response, response -> {response}")
        # except Exception as e:
        #     print(f"Error while getting absolute motor position: {e}")

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
        
    def calibrate_neutral_position(self):
        """
        Calibrate the neutral position of the end effector by moving to the current position.
        """
        self.neutral_position = 0.0
