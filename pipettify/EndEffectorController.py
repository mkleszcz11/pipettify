
class EndEffectorController():
    """
    End effector controller class. This class is responsible for controlling the end effector.
    """
    def __init__(self, robot, end_effector):
        pass

    def press_button_1(self, position):
        """
        Press button 1 on the pipette
        """
        pass

    def press_button_2(self, object):
        """
        Press button 2 on the pipette
        """
        pass

    def move_to_neutral_position(self):
        """
        Move end effector to neutral position (no buttons pressed)
        """
        pass

    def get_position(self):
        """
        Get current state of end effector (button 1, button 2, neutral)
        """
        pass

    def get_orientation(self):
        return self.end_effector.get_orientation()

    def get_state(self):
        return self.end_effector.get_state()