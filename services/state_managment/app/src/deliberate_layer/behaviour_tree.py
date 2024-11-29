from .bt_communication_interface import CommunicationInterface
import json
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import time

# Relative path to the .env file in the config directory
# Move up one level and into config
dotenv_path = Path('../../configurations/.env')

# Load the .env file
load_dotenv(dotenv_path=dotenv_path)

# Behaviour tree leaf nodes
class Leaf:
    def __init__(self, communication_interface=None):
        self.comm_interface = communication_interface

    def start(self):
        pass

    def update(self):
        # check if the behaviour is complete
        pass

    def end(self):
        pass

# For each behaviour mark the services that are critical to the behaviour to previent transition to another state while behaviour is running

class CheckIn(Leaf):
    def __init__(self, communication_interface=None):
        super().__init__(communication_interface)
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        # Start voice assistant
        self.comm_interface.check_in_status("start")
        self.comm_interface.publish("robot/cameraActive", "1")
        pass

    def update(self):
        # Check for errors in the services and pause or restart the check-in process
        pass

    def end(self):
        self.logger.info("Exiting check-in process")
        self.comm_interface.check_in_status("end")
        self.comm_interface.publish("robot/cameraActive", "0")
        pass

class AutonomousBhaviour(Leaf):
    def __init__(self, communication_interface=None):
        super().__init__(communication_interface)
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        # Face tracking
        # Autonomous roaming
        self.logger.info("Starting autonomous behaviour")
        pass

    def update(self):
        pass

    def end(self):
        self.logger.info("Exiting autonomous behaviour")
        pass

class EmotionGeneration(Leaf):
    def __init__(self, communication_interface=None):
        super().__init__(communication_interface)
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        # Enable the robots emotion generation system in robot behavior
        self.logger.info("Starting emotion generation")
        pass

    def update(self):
        pass

    def end(self):
        self.logger.info("Exiting emotion generation")
        pass

class AdministerSurvey(Leaf):
    def __init__(self, communication_interface=None):
        super().__init__(communication_interface)
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        # Start survey in user interface
        self.logger.info("Starting survey")
        pass

    def update(self):
        pass

    def end(self):
        self.logger.info("Exiting survey")
        pass


class TaskScheduler(Leaf):
    def __init__(self, communication_interface=None):
        super().__init__(communication_interface)
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        # Send message to the task scheduler to start scheduling tasks
        # Send message to user interface to show scheduled tasks
        self.logger.info("Starting task scheduler")
        if self.comm_interface:
            self.comm_interface.publish("service/start", "Starting Task Scheduler")
        pass

    def update(self):
        pass

    def end(self):
        self.logger.info("Exiting task scheduler")
        if self.comm_interface:
            self.comm_interface.publish("service/end", "Stopping Task Scheduler")
        pass


class Configurations(Leaf):
    def __init__(self, communication_interface=None):
        super().__init__(communication_interface)
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        # Show configuration options in user interface and start robot behaviour configuration
        self.logger.info("Starting configuration page")
        pass

    def update(self):
        pass

    def end(self):
        self.logger.info("Exiting configuration page")
        pass


class BehaviorBranch:
    """Represents a branch of behaviors accessible during a specific FSM state."""

    def __init__(self, name, communication_interface):
        self.name = name
        self.communication_interface = communication_interface
        self.behaviors = []
        self.all_services_available = False
        self.behaviour_running = False
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_behavior(self, behavior_class):
        behavior = behavior_class(self.communication_interface)
        self.behaviors.append(behavior)

    def update(self):
        """Update all active behaviors in this branch"""
        for behavior in self.behaviors:
            behavior.update()

    def end(self):
        # if behaviour is complete, set the behaviour_completion_status to True and end the behaviour
        """Stop all behaviors in this branch"""
        for behavior in self.behaviors:
            behavior.end()

    def activate_behavior(self):
        """Activate a specific behavior by name"""
        # If all services are available, start the behavior
        for behavior in self.behaviors:
            if self.behaviour_running is False:
                behavior.start()
                self.behaviour_running = True # Mark the behaviour as running

    def deactivate_behavior(self):
        """Deactivate a specific behavior by name"""
        for behavior in self.behaviors:
            behavior.end()
        self.behaviour_running = False


class BehaviorTree:
    def __init__(self, finite_state_machine_event_queue, behavior_tree_event_queue):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.communication_interface = CommunicationInterface(
            broker_address = str(os.getenv('MQTT_BROKER_ADDRESS')),
            port = int(os.getenv('MQTT_BROKER_PORT'))
        )

        self.finite_state_machine_event_queue = finite_state_machine_event_queue
        self.behavior_tree_event_queue = behavior_tree_event_queue

        self.current_branch = None
        self.current_state = None
        self.branches = {}

        # Service names to control
        self.behaviours =["reminder","check_in", "configurations"]

        # Dictionary to track acknowledgment status
        self.behaviour_branch_status = {behaviour: False for behaviour in self.behaviours}

        # Reminder
        self.reminder_branch = BehaviorBranch(self.behaviours[0], self.communication_interface)
        self.reminder_branch.add_behavior(TaskScheduler)
        self.add_branch(self.behaviours[0], self.reminder_branch)

        # Check-in
        self.check_in_dialog_branch = BehaviorBranch(self.behaviours[1], self.communication_interface)
        self.check_in_dialog_branch.add_behavior(CheckIn)
        self.check_in_dialog_branch.add_behavior(AutonomousBhaviour)
        self.check_in_dialog_branch.add_behavior(EmotionGeneration)
        self.check_in_dialog_branch.add_behavior(AdministerSurvey)
        self.add_branch(self.behaviours[1], self.check_in_dialog_branch)

        # Configuration
        self.configurations_branch = BehaviorBranch(self.behaviours[2], self.communication_interface)
        self.configurations_branch.add_behavior(Configurations)
        self.add_branch(self.behaviours[2], self.configurations_branch)

    def set_current_state(self, state):
        self.current_state = state

    def get_current_state(self):
        return self.current_state
    
    def get_current_branch(self):
        return self.current_branch.name if self.current_branch else None

    def add_branch(self, branch_name, branch):
        self.branches[branch_name] = branch

    def transition_to_branch(self, branch_name):
        """Transition to a specific branch of behaviors based on FSM state"""
        if branch_name in self.branches:
            if self.current_branch:
                self.current_branch.deactivate_behavior()  # Stop all behaviors in the current branch
            self.current_branch = self.branches[branch_name]
            if branch_name == self.behaviours[0]:
                self.communication_interface.set_behaviour_running_status(self.behaviours[0], True)
            self.current_branch.activate_behavior()  # Start all behaviors in the new branch
            self.logger.info(f"Transitioned to {self.current_branch.name} branch")

    def update(self):
        # Step 1: Check the high-level state in the finite state machine
        self.check_finite_state_machine_event_queue()

        # Step 2: Check if the user has requested a behavior
        self.check_for_user_requested_events()

        # Step 3: If no behavior is running, transition to the reminder branch
        if self.current_branch == None: # Default to reminder branch
            self.transition_to_branch(self.behaviours[0])

        
        # Step 4: Start and stop behaviors based on the current branch
        self.manage_behavior()

        # Step 5: Update all active behaviors in the current branch
        self.current_branch.update()

    def check_finite_state_machine_event_queue(self):
        if self.finite_state_machine_event_queue.empty() is False:
            self.logger.info("Checking FSM event queue...")
            state = self.finite_state_machine_event_queue.get()["state"]
            
            # Set current state if it's different from the existing one
            if self.current_state != state:
                self.set_current_state(state)
                
                # Transition based on the FSM state
                if state == 'Sleep':
                    self.transition_to_branch(self.behaviours[0])  # Reminder branch
                elif state == 'Active':
                    self.transition_to_branch(self.behaviours[0])  # Reminder branch
                elif state == 'Error':
                    pass
                    # Handle error state if required
    
    def check_for_user_requested_events(self):
        ''' Check if the user has requested a behavior '''
        behaviourRunning = self.communication_interface.get_behaviour_running_status()
        
        # Transition to appropriate branch if it is not already in that branch
        if behaviourRunning['check_in'] and self.current_branch.name != self.behaviours[1]:
            self.logger.info(f"Check-in event received event['check_in'] = {behaviourRunning['check_in']} and self.current_branch.name = {self.current_branch.name}")
            self.transition_to_branch(self.behaviours[1])
            self.set_current_state('interacting')
            self.logger.info("Fulfilling user request and transitioning to check-in branch")
        elif behaviourRunning['configurations'] and self.current_branch.name != self.behaviours[2]:
            self.logger.info("Configurations event received")
            self.transition_to_branch(self.behaviours[2])
            self.set_current_state('configuring')
            self.logger.info("Fulfilling user request and transitioning to configurations branch")

    def manage_behavior(self):
        """Activate or deactivate a specific behavior in the current branch"""
        behaviourIsRunning = self.communication_interface.get_behaviour_running_status()[self.current_branch.name] # Check if behaviour branch is running

        if behaviourIsRunning and self.current_branch.behaviour_running == False: # Activate the current branch if it's not running
            self.logger.info(f"Current branch is: {self.current_branch.name} and the behaviour is not running")
            self.current_branch.activate_behavior() # Activate the current branch if it's not running and not complete
        elif behaviourIsRunning == False and self.current_branch.behaviour_running: # Deactivate the current branch if it's running and complete
            self.logger.info(f"Current branch is: {self.current_branch.name} and the behaviour is complete")
            self.current_branch.deactivate_behavior()
            self.transition_to_branch(self.behaviours[0])
            self.set_current_state('active')
