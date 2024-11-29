from statemachine import StateMachine, State
from pipettify.controllers.controller_printer import PrinterController
from pipettify.controllers.controller_bed import BedController

class PipettifyStateMachine(StateMachine):
    # States
    idle = State("Idle", initial=True)
    moving_to_refill = State("Moving to Refill")
    refilling = State("Refilling")
    moving_to_next_probe = State("Moving to Next Probe")
    dispensing = State("Dispensing")
    completed = State("Completed")

    # Transitions
    start_pipetting = idle.to(moving_to_refill)
    arrive_at_refill = moving_to_refill.to(refilling)
    finish_refill = refilling.to(moving_to_next_probe)
    arrive_at_probe = moving_to_next_probe.to(dispensing)
    finish_dispensing = dispensing.to(moving_to_refill)
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
        self.flags = {
            "moving_to_refill_moved": False,
            "refilling_waited_before_moving_down": False,
            "refilling_moved_down": False,
            "refilling_refilled": False,
            "refilling_waited_before_moving_up": False,
            "refilling_moved_up": False,
            "moving_to_next_probe_moved": False,
            "dispensing_waited_before_moving_down": False,
            "dispensing_moved_down": False,
            "dispensing_dispensed": False,
            "dispensing_waited_before_moving_up": False,
            "dispensing_moved_up": False,
        }
        super().__init__()

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
        if self.current_state == self.moving_to_refill:
            return self.poll_moving_to_refill()
        elif self.current_state == self.refilling:
            return self.poll_refilling()
        elif self.current_state == self.moving_to_next_probe:
            return self.poll_moving_to_next_probe()
        elif self.current_state == self.dispensing:
            return self.poll_dispensing()
        # Add similar handlers for other states as needed
        return False

    def poll_moving_to_refill(self):
        """
        Logic for polling the 'moving_to_refill' state.
        """
        # Condition to move to the next state
        if not self.flags["moving_to_refill_moved"]:
            target_x = self.bed_controller.refilling_tank_x
            target_y = self.bed_controller.refilling_tank_y
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
        
        if not self.flags["refilling_moved_down"]:
            print("Moving down to refill.")
            self.printer_controller.move_to_coordinates(
                self.bed_controller.refilling_tank_x,
                self.bed_controller.refilling_tank_y,
                self.bed_controller.refilling_tank_z
            )
            
            if self.printer_controller.is_at_position(self.bed_controller.refilling_tank_x,
                                                      self.bed_controller.refilling_tank_y,
                                                      self.bed_controller.refilling_tank_z):
                print("Printer moved to refill position.")
                self.flags["refilling_moved_down"] = True

            return False
        
        if not self.flags["refilling_refilled"]:
            print("Refilling...")
            ###
            print("HERE REFILLING SHOULD BE IMPLEMENTED.")
            self.flags["refilling_refilled"] = True
            ###
            # self.pipette_controller.press_push_button()
            
            # if self.pipette_controller.last_operation == "refill":
            #     print("Refilling completed.")
            #     self.flags["refilling_refilled"] = True
                
            return False
        
        if not self.flags["refilling_waited_before_moving_up"]:
            print("Waiting before moving up.")
            self.flags["refilling_waited_before_moving_up"] = True # TODO -> For now there is no delay.
            return False
        
        if not self.flags["refilling_moved_up"]:
            print("Moving up after refilling.")
            self.printer_controller.move_to_coordinates(
                self.bed_controller.refilling_tank_x,
                self.bed_controller.refilling_tank_y,
                self.bed_controller.safe_z
            )
            
            if self.printer_controller.is_at_position(self.bed_controller.refilling_tank_x,
                                                      self.bed_controller.refilling_tank_y,
                                                      self.bed_controller.safe_z):
                print("Printer moved to safe position.")
                self.flags["refilling_moved_up"] = True

            return False
        
        print("All refilling state flags are marked, transitioning to moving_to_the_next_probe state.")
        self.finish_refill()
        return True

    def poll_moving_to_next_probe(self):
        """
        Start the pipetting sequence.
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
        Start the pipetting sequence.
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
        
        if not self.flags["dispensing_dispensed"]:
            print("Dispensing...")
            ###
            print("HERE DISPENSING SHOULD BE IMPLEMENTED.")
            self.flags["dispensing_dispensed"] = True
            ###
            self.pipette_controller.execute_dispense(probe = self.current_probe)
            
            # if self.pipette_controller.last_operation == "dispense":
            #     print("Dispensing completed.")
            #     self.flags["dispensing_dispensed"] = True
                
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
        
        print("All dispensing state flags are marked, transitioning to moving_to_the_next_probe state.")
        self.finish_dispensing()
        self.clear_flags() # THE LAST STEP - CLEAR ALL FLAGS AND REPEAT THE CYCLE
        return True
