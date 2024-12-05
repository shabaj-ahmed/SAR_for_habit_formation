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
    def __init__(self, communication_interface=None, priority='critical'):
        self.comm_interface = communication_interface
        self.name = None
        self.priority = priority
    
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

class voice_assistant(Leaf):
    def __init__(self, communication_interface=None, priority='critical'):
        super().__init__(communication_interface, priority)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = "voice_assistant"

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

class robot_controller(Leaf):
    def __init__(self, communication_interface=None, priority='critical'):
        super().__init__(communication_interface, priority)
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

class TaskScheduler(Leaf):
    def __init__(self, communication_interface=None, priority='critical'):
        super().__init__(communication_interface, priority)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = "task_manager"

    def set_up(self):
        payload = {
            "service_name": "task_manager",
            "status": "ready",
            "message": "",
            "details": "",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.comm_interface.publish(
            topic="task_manager_status", 
            message=json.dumps(payload))
        pass

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
    def __init__(self, communication_interface=None, priority='critical'):
        super().__init__(communication_interface, priority)
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


class BehaviorBranch:
    """Represents a branch of behaviours accessible during a specific FSM state."""

    def __init__(self, name, communication_interface,):
        self.name = name
        self.communication_interface = communication_interface
        self.services = []
        self.all_services_available = False
        self.behaviour_running = False
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_behaviour(self, behaviour_class, priority='critical'):
        behaviour = behaviour_class(self.communication_interface, priority)
        
        self.services.append(behaviour)

    def activate_behaviour(self):
        """Activate a specific behaviour by name"""
        # If all services are available, start the behaviour
        logging.info(f"Activating {self.name} branch")
        for service in self.services:
            if self.behaviour_running is False:
                service.set_up()
        
        logging.info(f"Waiting for services to be available for {self.name} branch")
        # Wait until all services are available
        waiting = True
        while True:
            waiting = False
            for service in self.services:
                serviceStatus = self.communication_interface.get_service_status(service.name)
                print(f"{service.name} has a service status: {serviceStatus}")
                if serviceStatus != "ready":
                    waiting = True
                time.sleep(0.2)
            if not waiting: # Once all services are ready, continue with the behaviour
                break
        
        for service in self.services:
            if self.behaviour_running is False:
                service.start()
        
        self.behaviour_running = True # Mark the behaviour as running

    def update(self):
        """Update all active behaviours in this branch"""
        for behaviour in self.services:
            # TODO: Check if critical behaviours are running
            behaviour.update()

    def deactivate_behaviour(self):
        """Deactivate a specific behaviour by name"""
        # Ensure all services has ended gracefully
        for behaviour in self.services:
            behaviour.end()
        self.behaviour_running = False


class BehaviorTree:
    def __init__(self, finite_state_machine_event_queue, behaviour_tree_event_queue):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.communication_interface = CommunicationInterface(
            broker_address = str(os.getenv('MQTT_BROKER_ADDRESS')),
            port = int(os.getenv('MQTT_BROKER_PORT'))
        )

        self.finite_state_machine_event_queue = finite_state_machine_event_queue
        self.behaviour_tree_event_queue = behaviour_tree_event_queue

        self.current_branch = None
        self.current_state = None
        self.branches = {}

        # Service names to control
        self.behaviours =["reminder","check_in", "configuring"]

        # Dictionary to track acknowledgment status
        self.behaviour_branch_status = {behaviour: False for behaviour in self.behaviours}

        # Reminder
        self.reminder_branch = BehaviorBranch(self.behaviours[0], self.communication_interface)
        self.reminder_branch.add_behaviour(TaskScheduler)
        self.add_branch(self.behaviours[0], self.reminder_branch)

        # Check-in
        self.check_in_dialog_branch = BehaviorBranch(self.behaviours[1], self.communication_interface)
        self.check_in_dialog_branch.add_behaviour(voice_assistant)
        self.check_in_dialog_branch.add_behaviour(robot_controller, priority="optional")
        self.add_branch(self.behaviours[1], self.check_in_dialog_branch)

        # Configuration
        self.configurations_branch = BehaviorBranch(self.behaviours[2], self.communication_interface)
        self.configurations_branch.add_behaviour(Configurations)
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
        """Transition to a specific branch of behaviours based on FSM state"""
        if branch_name in self.branches:
            if self.current_branch:
                self.current_branch.deactivate_behaviour()  # Stop all behaviours in the current branch
            self.current_branch = self.branches[branch_name]
            if branch_name == self.behaviours[0]:
                self.communication_interface.set_behaviour_running_status(self.behaviours[0], True)
            self.current_branch.activate_behaviour()  # Start all behaviours in the new branch
            self.logger.info(f"Transitioned to {self.current_branch.name} branch")
            self.behaviour_tree_event_queue.put({"state": branch_name})

    def update(self):
        """Update the behaviour tree"""
        # Step 1: Check the high-level state in the finite state machine
        self.check_finite_state_machine_event_queue()

        # Step 2: Check if the user has requested a behaviour
        self.check_for_user_requested_events()

        # Step 3: If no behaviour is running, transition to the reminder branch
        if self.current_branch == None: # Default to reminder branch
            self.transition_to_branch(self.behaviours[0])

        
        # Step 4: Start and stop behaviours based on the current branch
        self.manage_behaviour()

        # Step 5: Update all active behaviours in the current branch
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
        ''' Check if the user has requested a behaviour '''
        behaviourRunning = self.communication_interface.get_behaviour_running_status()

        # Transition to appropriate branch if it is not already in that branch
        if behaviourRunning['check_in'] and self.current_branch.name != self.behaviours[1]:
            self.logger.info(f"Check-in event received event['check_in'] = {behaviourRunning['check_in']} and self.current_branch.name = {self.current_branch.name}")
            self.transition_to_branch(self.behaviours[1])
            self.set_current_state('interacting')
            self.logger.info("Fulfilled user request and transitioning to check-in branch")
        elif behaviourRunning['configurations'] and self.current_branch.name != self.behaviours[2]:
            self.logger.info("Configurations event received")
            self.transition_to_branch(self.behaviours[2])
            self.set_current_state('configuring')
            self.logger.info("Fulfilled user request and transitioning to configurations branch")

    def manage_behaviour(self):
        """Activate or deactivate a specific behaviour in the current branch"""
        behaviourIsRunning = self.communication_interface.get_behaviour_running_status()[self.current_branch.name] # Check if behaviour branch is running

        if behaviourIsRunning and self.current_branch.behaviour_running == False: # Activate the current branch if it's not running
            self.logger.info(f"Current branch is: {self.current_branch.name} and the behaviour is not running")
            self.current_branch.activate_behaviour() # Activate the current branch if it's not running and not complete
        elif behaviourIsRunning == False and self.current_branch.behaviour_running: # Deactivate the current branch if it's running and complete
            self.logger.info(f"Current branch is: {self.current_branch.name} and the behaviour is complete")
            self.current_branch.deactivate_behaviour()
            self.transition_to_branch(self.behaviours[0])
            self.set_current_state('active')
