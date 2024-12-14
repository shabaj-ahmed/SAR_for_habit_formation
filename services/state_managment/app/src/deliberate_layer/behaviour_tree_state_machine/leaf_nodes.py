import logging

# Behaviour tree leaf nodes
class Leaf:
    def __init__(self, communication_interface=None, priority='critical', branch_name=""):
        '''
        A subclass with the critical variables and methods for running the service that need to be created for the behaviour tree to operate

        args:

        '''
        self.comm_interface = communication_interface
        self.name = None
        self.priority = priority
        self.branch = branch_name
    
    def set_up(self):
        pass

    def start(self):
        pass

    def update(self):
        # check if the behaviour is complete
        pass

    def end(self):
        pass

# For each behaviour mark the services that are critical to the behaviour to previent transition to another state while behaviour is running

class UserInterface(Leaf):
    '''
    The user interface is always active in each of the branches of the behaviour tree
    The behaviour tree controls the response of the user interface when different behaviours are running
    '''
    def __init__(self, communication_interface=None, priority='critical', branch_name=''):
        super().__init__(communication_interface, priority, branch_name)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = "user_interface"

    def set_up(self):
        self.logger.info("Setting up user interface")
        self.comm_interface.behaviour_controller(self.name, "set_up")
        pass

    def start(self):
        self.logger.info("Starting user interface")
        self.comm_interface.behaviour_controller(self.name, "start")
        pass

    def update(self):
        pass

    def end(self):
        self.logger.info("Stopping behaviour in user interface")
        if self.branch == "check_in":
            self.comm_interface.end_check_in()
            pass
        self.comm_interface.behaviour_controller(self.name, "end")
        pass

class VoiceAssistant(Leaf):
    def __init__(self, communication_interface=None, priority='critical', branch_name=''):
        super().__init__(communication_interface, priority, branch_name)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = "speech_recognition"

    def set_up(self):
        self.comm_interface.behaviour_controller(self.name, "set_up")

    def start(self):
        # Start voice assistant
        self.comm_interface.behaviour_controller(self.name, "start")
        pass

    def update(self):
        # Check for errors in the services and pause or restart the check-in process
        pass

    def end(self):
        self.logger.info("Exiting check-in process")
        self.comm_interface.behaviour_controller(self.name, "end")
        pass

class RobotController(Leaf):
    def __init__(self, communication_interface=None, priority='critical', branch_name=''):
        super().__init__(communication_interface, priority, branch_name)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = "robot_control"

    def set_up(self):
        self.comm_interface.behaviour_controller(self.name, "set_up")

    def start(self):
        # Face tracking
        # Autonomous roaming
        self.logger.info("Starting autonomous behaviour")
        self.comm_interface.behaviour_controller(self.name, "start")
        pass

    def update(self):
        pass

    def end(self):
        self.logger.info("Exiting autonomous behaviour")
        self.comm_interface.behaviour_controller(self.name, "end")
        pass

class Reminder(Leaf):
    def __init__(self, communication_interface=None, priority='critical', branch_name=''):
        super().__init__(communication_interface, priority, branch_name)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = "reminder"

    def set_up(self):
        pass

    def start(self):
        self.logger.info("Starting reminder")
        # Check if its time to provide a reminder
        pass

    def update(self):
        # Check if its time to provide a reminder
            # Start reminder
        pass

    def remind_behaviour(self):
        # Wake up robot
            # Start a animation
            # Wait for the animation to complete
        # Drive off charging station
            # Request robot to drive off charging station
            # Wait for robot to drive off charging station
        # Provide reminder
            # Ask voice assistant to send reminder message
            # Wait for robot to provide reminder
        # Return to charging station
            # Request robot to return to charging station
        pass

    def end(self):
        self.logger.info("Exiting reminder")
        pass


class Configurations(Leaf):
    def __init__(self, communication_interface=None, priority='critical', branch_name=''):
        super().__init__(communication_interface, priority, branch_name)
        self.logger = logging.getLogger(self.__class__.__name__)

    def set_up(self):
        pass

    def start(self):
        # Show configuration options in user interface and start robot behaviour configuration
        self.logger.info("Starting configuration page")
        pass

    def update(self):
        pass

    def end(self):
        self.logger.info("Exiting configuration page")
        pass