import logging
import time

class BehaviourBranch:
    """Represents a branch of behaviours accessible during a specific FSM state."""

    def __init__(self, name, communication_interface,):
        self.branch_name = name
        self.communication_interface = communication_interface
        self.services = []
        self.all_services_available = False
        self.behaviour_running = False
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_service(self, behaviour_class, priority='critical'):
        behaviour = behaviour_class(
            communication_interface = self.communication_interface,
            priority = priority,
            branch_name = self.branch_name
            )
        self.services.append(behaviour)

    def activate_behaviour(self):
        """Activate a specific behaviour by name"""
        # If all services are available, start the behaviour
        logging.info(f"Activating {self.branch_name} branch")
        for service in self.services:
            logging.info(f"{service.name} is in the {self.branch_name} behaviour branch" )
            if self.behaviour_running is False:
                service.set_up()
        
        logging.info(f"Waiting for services to be available for {self.branch_name} branch")

        # Wait until all services are available
        waiting = True
        while True:
            waiting = False
            for service in self.services:
                serviceStatus = self.communication_interface.get_system_status()[service.name]
                if serviceStatus != "ready":
                    waiting = True
                time.sleep(0.2)
            if not waiting: # Once all services are ready, continue with the behaviour
                break
        
        for service in self.services:
            service.start()
            time.sleep(0.4) # give service time to process the start command
        logging.info(f"{self.branch_name} branch has started")
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