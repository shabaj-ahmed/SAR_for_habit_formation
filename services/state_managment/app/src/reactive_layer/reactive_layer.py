from .rt_communication_interface import CommunicationInterface
import os
import logging

class ReactiveLayer:
    def __init__(self, event_queue):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.communication_interface = CommunicationInterface(
            broker_address = str(os.getenv('MQTT_BROKER_ADDRESS')),
            port = int(os.getenv('MQTT_BROKER_PORT'))
        )
        self.event_queue = event_queue
        self.previous_state = None

    def detect_critical_condition(self):
        inputs = self.communication_interface.get_critical_events()

        # The logic below follows the subsumption design architecture. It monitors the
        # inputs from critical events. based on the priority of the event it would
        # trigger the appropriate state change.
        if inputs['error'] == True: # Heighest priority
            if self.previous_state != "Error":
                self.event_queue.put({"state": "Error"})
                self.previous_state = "Error"
                self.logger.info("Transitioning to Error state")
        elif inputs['switch_state'] == False: # Emergency stop
            if self.previous_state != "Sleep":
                self.event_queue.put({"state": "Sleep"})
                self.previous_state = "Sleep"
                self.logger.info("Transitioning to Sleep state")
        elif inputs['switch_state'] == True:
            if self.previous_state != "Active":
                self.event_queue.put({"state": "Active"})
                self.previous_state = "Active"
                self.logger.info("Transitioning to Active state")
        elif inputs['reminder'] == True: # If user has turned the system off no reminder should be sent
            if self.previous_state != "Active":
                self.event_queue.put({"state": "Active"})
                self.previous_state = "Active"
                self.logger.info("Transitioning to Active state")
        else: # default to sleep
            if self.previous_state != "Sleep":
                self.event_queue.put({"state": "Sleep"})
                self.previous_state = "Sleep"
                self.logger.info("Transitioning to Sleep state")

        # If the transition from one state to another requires a specific sequence of events
        # to occur to safely transition, then the deliberate layer would be responsible for
        # managing it.