import logging
import time

class BehaviourBranch:
    """Represents a branch of behaviours accessible during a specific FSM state."""

    def __init__(self, name, communication_interface, orchestrator=None):
        self.branch_name = name
        self.communication_interface = communication_interface
        self.services = []
        self.all_services_available = False
        self.behaviour_running = "disabled"
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(self.__class__.__name__)
        self.branch_in_error_state = False  # Tracks if the branch is in an error state
    
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

        retry_counter = 4
        current_attempts = 1
        while True:
            for service in self.services:
                logging.info(f"{service.name} is in the {self.branch_name} behaviour branch" )

            for service in self.services:
                logging.info(f"Setting up {service.name} service")
                service.set_up()

            time.sleep(0.5)
            self.communication_interface.request_service_status()
            
            logging.info(f"Waiting for services to be available for {self.branch_name} branch")

            # Wait until all services are available
            waiting = True
            while True:
                waiting = False
                for service in self.services:
                    serviceStatus = self.communication_interface.get_system_status()[service.name]
                    if serviceStatus != "ready":
                        logging.info(f"{service.name} is not ready")
                        current_attempts += 1
                        waiting = True
                    time.sleep(0.5)
                if not waiting or current_attempts > retry_counter: # Once all services are ready, continue with the behaviour
                    current_attempts = 1
                    break
            
            if not waiting:
                logging.info(f"Exiting waiting loop for {self.branch_name} branch")
                break

        logging.info(f"All services are ready for {self.branch_name} branch")
        for service in self.services:
            service.start()
            time.sleep(0.4) # give service time to process the start command
        logging.info(f"{self.branch_name} branch has started")

        self.behaviour_running = "standby" 

    def update(self, fsm_state):
        if fsm_state == "Error" and not self.branch_in_error_state:
            # Transition to error state
            if self.orchestrator:
                self.logger.info("Pausing orchestrator due to error.")
                self.orchestrator.error()
                self.branch_in_error_state = True
            return
        elif fsm_state == "Error" and self.branch_in_error_state:
            self.logger.info("Branch is in error state.")
            return
        elif fsm_state != "Error" and self.branch_in_error_state:
            self.branch_in_error_state = False
            for service in self.services:
                service.set_up()
            if self.orchestrator:
                self.logger.info("Resuming orchestrator.")
                self.orchestrator.resume()
            time.sleep(0.5)

        """Update all active behaviours in this branch"""
        for behaviour in self.services:
            # TODO: Check if critical behaviours are running
            behaviour.update()
        
        # Check for behaviour start trigger
        if self.behaviour_running == "standby" and self.communication_interface.get_behaviour_running_status()[self.branch_name] == "enabled":
            # logging.info(f"{self.branch_name} is being requested to start")
            if self.orchestrator:
                self.orchestrator.start()
                self.behaviour_running = "running"
                self.communication_interface.set_behaviour_running_status(self.branch_name, self.behaviour_running)
        
        # Update the orchestrator if present
        # Check for a behaviour start command...
        if self.orchestrator:
            self.orchestrator.update()
            if self.orchestrator.is_complete():
                # If the orchestrator signals completion, 
                # handle that logic here (e.g., transition back to a default branch)
                # self.logger.info(f"{self.branch_name} scenario completed.")
                # Possibly communicate to the BehaviourTree or set a flag.
                # The BehaviourTree might detect this on the next update and transition out.  
                pass
        
    def deactivate_behaviour(self):
        """Deactivate a specific behaviour by name"""
        # Ensure all services has ended gracefully
        for behaviour in self.services:
            behaviour.end()
            # call orchestrator.end to start a shut down sequence...

        if self.orchestrator:
            # if you have an end or reset method for orchestrator
            pass 

        self.behaviour_running = "disabled"