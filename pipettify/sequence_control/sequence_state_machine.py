from statemachine import StateMachine, State
from pipettify.controllers.controller_printer import PrinterController
from pipettify.controllers.controller_bed import BedController

class PipettifyStateMachine(StateMachine):
    # States
    idle = State("Idle", initial=True)
    moving_to_next_tip = State("Moving to Next Tip")
    changing_tip = State("Changing Tip")
    moving_to_refill = State("Moving to Refill")
    refilling = State("Refilling")
    moving_to_next_probe = State("Moving to Next Probe")
    dispensing = State("Dispensing")
    moving_to_disposal = State("Moving to Disposal")
    disposing_tip = State("Disposing Tip")
    completed = State("Completed")

    # Transitions
    start_pipetting = idle.to(moving_to_next_tip)
    arrive_at_tip = moving_to_next_tip.to(changing_tip)
    finish_changing_tip = changing_tip.to(moving_to_refill)
    arrive_at_refill = moving_to_refill.to(refilling)
    finish_refill = refilling.to(moving_to_next_probe)
    arrive_at_probe = moving_to_next_probe.to(dispensing)
    finish_dispensing = dispensing.to(moving_to_disposal)
    arrive_at_disposal = moving_to_disposal.to(disposing_tip)
    finish_disposing_tip = disposing_tip.to(moving_to_next_tip)
    complete_pipetting = dispensing.to(completed)
    reset_to_idle = (
        moving_to_refill.to(idle) |
        refilling.to(idle) |
        moving_to_next_probe.to(idle) |
        dispensing.to(idle) |
        completed.to(idle)
    )

    def __init__(self, printer_controller, pipette_controller, bed_controller):
        self.printer_controller = printer_controller
        self.pipette_controller = pipette_controller
        self.bed_controller = bed_controller
        self.current_probe = None
        self.current_tip = None
        self.flags = {
            "moving_to_next_tip_moved_up_to_safe_z": False,
            "moving_to_next_tip_moved": False,
            "changing_tip_moved_down": False,
            "changing_tip_moved_up": False,
            "moving_to_refill_moved": False,
            "refilling_waited_before_moving_down": False,
            "refilling_pressed_button": False,
            "refilling_moved_down": False,
            "refilling_released_button": False,
            "refilling_waited_before_moving_up": False,
            "refilling_moved_up": False,
            "moving_to_next_probe_moved": False,
            "dispensing_waited_before_moving_down": False,
            "dispensing_moved_down": False,
            "dispensing_pressed_button": False,
            "dispensing_waited_before_moving_up": False,
            "dispensing_moved_up": False,
            "dispensing_released_button": False,
            "moving_to_disposal_moved": False,
            "disposing_tip_moved_up": False, # TODO -> for now keep movement as 0
            "disposing_tip_moved_down": False,
        }
        super().__init__()
        
    # If there is a state change - update the GUI (display)

    def clear_flags(self):
        """
        Clear all flags.
        """
        for flag in self.flags:
            self.flags[flag] = False

    def poll(self):
        """
        Periodic polling logic. Calls the current state's polling method.
        """
        if self.current_state == self.idle:
            return False
        elif self.current_state == self.moving_to_next_tip:
            return self.pool_moving_to_next_tip()
        elif self.current_state == self.changing_tip:
            return self.poll_changing_tip()
        elif self.current_state == self.moving_to_refill:
            return self.poll_moving_to_refill()
        elif self.current_state == self.refilling:
            return self.poll_refilling()
        elif self.current_state == self.moving_to_next_probe:
            return self.poll_moving_to_next_probe()
        elif self.current_state == self.dispensing:
            return self.poll_dispensing()
        elif self.current_state == self.moving_to_disposal:
            return self.pool_moving_to_disposal()
        elif self.current_state == self.disposing_tip:
            return self.pool_disposing_tip()
        # Add similar handlers for other states as needed
        return False

    def pool_moving_to_next_tip(self):
        """
        Logic for polling the 'moving_to_tip_rack' state.
        """
        print("Polling moving to next tip.")
        
        if not self.flags["moving_to_next_tip_moved_up_to_safe_z"]:
            print("Moving up to safe z.")
            self.printer_controller.move_to_coordinates(self.printer_controller.curr_x,
                                                        self.printer_controller.curr_y,
                                                        self.bed_controller.safe_z)
            self.flags["moving_to_next_tip_moved_up_to_safe_z"] = True
            return False
            
        
        # Condition to move to the next state
        if not self.flags["moving_to_next_tip_moved"]:
            self.current_tip = self.bed_controller.next_tip()
            next_tip_x = self.bed_controller.tips[self.current_tip]["coordinates"][0]
            next_tip_y = self.bed_controller.tips[self.current_tip]["coordinates"][1]

            self.printer_controller.move_to_coordinates(next_tip_x,
                                                        next_tip_y,
                                                        self.bed_controller.safe_z)

            # Condition to mark a flag
            if self.printer_controller.is_at_position(next_tip_x,
                                                      next_tip_y,
                                                      self.bed_controller.safe_z):
                print("Printer moved to next tip position.")
                self.flags["moving_to_next_tip_moved"] = True
                
            return False

        print("All moving to refill satte flags are marked, transitioning to refilling state.")
        self.arrive_at_tip()
        return True  # State completed
        

    def poll_changing_tip(self):
        """
        Logic for polling the 'changing_tip' state.
        1. Move Down
        2. Move Up
        """
        if not self.flags["changing_tip_moved_down"]:
            print("Moving down to change tip.")
            self.printer_controller.move_to_coordinates(
                self.bed_controller.tips[self.current_tip]["coordinates"][0],
                self.bed_controller.tips[self.current_tip]["coordinates"][1],
                self.bed_controller.change_tip_z
            )
            
            if self.printer_controller.is_at_position(self.bed_controller.tips[self.current_tip]["coordinates"][0],
                                                      self.bed_controller.tips[self.current_tip]["coordinates"][1],
                                                      self.bed_controller.change_tip_z):
                print("Printer moved down to tip position.")
                self.flags["changing_tip_moved_down"] = True

            return False
        
        if not self.flags["changing_tip_moved_up"]:
            print("Moving up after changing tip.")
            self.printer_controller.move_to_coordinates(
                self.bed_controller.tips[self.current_tip]["coordinates"][0],
                self.bed_controller.tips[self.current_tip]["coordinates"][1],
                self.bed_controller.safe_z
            )
            
            if self.printer_controller.is_at_position(self.bed_controller.tips[self.current_tip]["coordinates"][0],
                                                      self.bed_controller.tips[self.current_tip]["coordinates"][1],
                                                      self.bed_controller.safe_z):
                print("Printer moved up to safe position.")
                self.flags["changing_tip_moved_up"] = True

            return False
        
        self.bed_controller.update_tip_state(self.current_tip[0], self.current_tip[1], True)
        print("All changing tip state flags are marked, transitioning to moving_to_refill state.")
        self.finish_changing_tip()
        return True


    def poll_moving_to_refill(self):
        """
        Logic for polling the 'moving_to_refill' state.
        """
        # Condition to move to the next state
        if not self.flags["moving_to_refill_moved"]:
            target_x = self.bed_controller.refilling_tank[0]
            target_y = self.bed_controller.refilling_tank[1]
            safe_z = self.bed_controller.safe_z

            self.printer_controller.move_to_coordinates(target_x, target_y, safe_z)

            # Condition to mark a flag
            if self.printer_controller.is_at_position(target_x, target_y, safe_z):
                print("Printer moved to refill position.")
                self.flags["moving_to_refill_moved"] = True
                
            return False

        print("All moving to refill satte flags are marked, transitioning to refilling state.")
        self.arrive_at_refill()
        return True  # State completed


    def poll_refilling(self):
        """
        Logic for polling the 'refilling' state.
        """
        if not self.flags["refilling_waited_before_moving_down"]:
            print("Waiting before moving down.")
            self.flags["refilling_waited_before_moving_down"] = True # TODO -> For now there is no delay.
            return False
        
        if not self.flags["refilling_pressed_button"]:
            print("Pressing button to refill.")
            self.pipette_controller.press_push_button()
            
            if self.pipette_controller.state == "push_button_pressed":
                print("Button pressed.")
                self.flags["refilling_pressed_button"] = True
                
            return False
        
        if not self.flags["refilling_moved_down"]:
            print("Moving down to refill.")
            self.printer_controller.move_to_coordinates(
                self.bed_controller.refilling_tank[0],
                self.bed_controller.refilling_tank[1],
                self.bed_controller.refilling_z
            )
            
            if self.printer_controller.is_at_position(self.bed_controller.refilling_tank[0],
                                                      self.bed_controller.refilling_tank[1],
                                                      self.bed_controller.refilling_z):
                print("Printer moved to refill position.")
                self.flags["refilling_moved_down"] = True

            return False
        
        if not self.flags["refilling_released_button"]:
            print("Releasing button after refilling.")
            self.pipette_controller.move_to_neutral()
            
            if self.pipette_controller.state == "neutral":
                print("Button released.")
                self.flags["refilling_released_button"] = True
                
            return False
        
        if not self.flags["refilling_waited_before_moving_up"]:
            print("Waiting before moving up.")
            self.flags["refilling_waited_before_moving_up"] = True # TODO -> For now there is no delay.
            return False
        
        if not self.flags["refilling_moved_up"]:
            print("Moving up after refilling.")
            self.printer_controller.move_to_coordinates(
                self.bed_controller.refilling_tank[0],
                self.bed_controller.refilling_tank[1],
                self.bed_controller.safe_z
            )
            
            if self.printer_controller.is_at_position(self.bed_controller.refilling_tank[0],
                                                      self.bed_controller.refilling_tank[1],
                                                      self.bed_controller.safe_z):
                print("Printer moved to safe position.")
                self.flags["refilling_moved_up"] = True

            return False
        
        print("All refilling state flags are marked, transitioning to moving_to_the_next_probe state.")
        self.finish_refill()
        return True

    def poll_moving_to_next_probe(self):
        """
        Move to the next probe position.
        """
        print("Polling moving to next probe.")
        # Condition to move to the next state
        if not self.flags["moving_to_next_probe_moved"]:
            self.current_probe = self.bed_controller.next_probe()
            next_probe_x = self.bed_controller.probes[self.current_probe]["coordinates"][0]
            next_probe_y = self.bed_controller.probes[self.current_probe]["coordinates"][1]

            self.printer_controller.move_to_coordinates(next_probe_x,
                                                        next_probe_y,
                                                        self.bed_controller.safe_z)

            # Condition to mark a flag
            if self.printer_controller.is_at_position(next_probe_x,
                                                      next_probe_y,
                                                      self.bed_controller.safe_z):
                print("Printer moved to next probe position.")
                self.flags["moving_to_next_probe_moved"] = True
                
            return False

        print("All moving to refill satte flags are marked, transitioning to refilling state.")
        self.arrive_at_probe()
        return True  # State completed
    
    def poll_dispensing(self):
        """
        Dispense the liquid.
        """
        # Condition to move to the next state
        if not self.flags["dispensing_waited_before_moving_down"]:
            print("Waiting before moving down.")
            self.flags["dispensing_waited_before_moving_down"] = True # TODO -> For now there is no delay.
            return False
        
        if not self.flags["dispensing_moved_down"]:
            print("Moving down to dispense.")
            
            self.printer_controller.move_to_coordinates(
                self.printer_controller.curr_x,
                self.printer_controller.curr_y,
                self.bed_controller.dispensing_z
            )
            
            if self.printer_controller.is_at_position(self.printer_controller.curr_x,
                                                      self.printer_controller.curr_y,
                                                      self.bed_controller.dispensing_z):
                print("Printer moved to dispense position.")
                self.flags["dispensing_moved_down"] = True

            return False
        
        if not self.flags["dispensing_pressed_button"]:
            print("Pressing button to dispense.")
            self.pipette_controller.press_push_button()
            
            if self.pipette_controller.state == "push_button_pressed":
                print("Button pressed.")
                self.flags["dispensing_pressed_button"] = True
                
            return False
        
        if not self.flags["dispensing_waited_before_moving_up"]:
            print("Waiting before moving up.")
            self.flags["dispensing_waited_before_moving_up"] = True # `TODO -> For now there is no delay.
            return False
        
        if not self.flags["dispensing_moved_up"]:
            print("Moving up after dispensing.")
            self.printer_controller.move_to_coordinates(
                self.printer_controller.curr_x,
                self.printer_controller.curr_y,
                self.bed_controller.safe_z
            )
            
            if self.printer_controller.is_at_position(self.printer_controller.curr_x,
                                                      self.printer_controller.curr_y,
                                                      self.bed_controller.safe_z):
                print("Printer moved to safe position.")
                self.flags["dispensing_moved_up"] = True

            return False
        
        if not self.flags["dispensing_released_button"]:
            print("Releasing button after dispensing.")
            self.pipette_controller.move_to_neutral()
            
            if self.pipette_controller.state == "neutral":
                print("Button released.")
                self.flags["dispensing_released_button"] = True
                
            return False
        
        print("All dispensing state flags are marked, transitioning to moving_to_the_next_probe state.")
        self.finish_dispensing()
        return True

    def pool_moving_to_disposal(self):
        """
        Logic for polling the 'moving_to_disposal' state.
        """
        if not self.flags["moving_to_disposal_moved"]:
            print("Moving to disposal...")
            self.printer_controller.move_to_coordinates(self.bed_controller.disposal_tank[0],
                                                        self.bed_controller.disposal_tank[1],
                                                        self.bed_controller.safe_z)

            if self.printer_controller.is_at_position(self.bed_controller.disposal_tank[0],
                                                      self.bed_controller.disposal_tank[1],
                                                      self.bed_controller.safe_z):
                print("Printer moved to disposal position.")
                self.flags["moving_to_disposal_moved"] = True
            return False
        
        print("All moving to disposal state flags are marked, transitioning to disposing_tip state.")
        self.arrive_at_disposal()
        return True

    def pool_disposing_tip(self):
        """
        Logic for polling the 'disposing_tip' state.
        """
        if not self.flags["disposing_tip_moved_up"]:
            print("Moving up after disposing tip...")
            self.printer_controller.move_to_coordinates(self.bed_controller.disposal_tank[0],
                                                        self.bed_controller.disposal_tank[1],
                                                        self.bed_controller.drop_tip_z)
            if self.printer_controller.is_at_position(self.bed_controller.disposal_tank[0],
                                                      self.bed_controller.disposal_tank[1],
                                                      self.bed_controller.drop_tip_z):
                print("Printer moved up to safe position.")
                self.flags["disposing_tip_moved_up"] = True
            return False
        
        if not self.flags["disposing_tip_moved_down"]:
            print("Moving down to dispose tip...")
            self.printer_controller.move_to_coordinates(self.bed_controller.disposal_tank[0],
                                                        self.bed_controller.disposal_tank[1],
                                                        self.bed_controller.safe_z)
            if self.printer_controller.is_at_position(self.bed_controller.disposal_tank[0],
                                                      self.bed_controller.disposal_tank[1],
                                                      self.bed_controller.safe_z):
                print("Printer moved down to disposal position.")
                self.flags["disposing_tip_moved_down"] = True
            return False
        
        print("All disposing tip state flags are marked, transitioning to moving_to_next_tip state.")
        self.clear_flags() # THE LAST STEP - CLEAR ALL FLAGS AND REPEAT THE CYCLE
        self.finish_disposing_tip()
        return True