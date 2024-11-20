from .rt_communication_interface import CommunicationInterface
from dotenv import load_dotenv
from pathlib import Path
import os

# Relative path to the .env file in the config directory
# Move up one level and into config
dotenv_path = Path('../../configurations/.env')

# Load the .env file
load_dotenv(dotenv_path=dotenv_path)

class ReactiveLayer:
    def __init__(self, event_queue):
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
        elif inputs['switch_state'] == False: # Emergency stop
            if self.previous_state != "Sleep":
                self.event_queue.put({"state": "Sleep"})
                self.previous_state = "Sleep"
        elif inputs['switch_state'] == True:
            if self.previous_state != "Active":
                self.event_queue.put({"state": "Active"})
                self.previous_state = "Active"
        elif inputs['reminder'] == True: # If user has turned the system off no reminder should be sent
            if self.previous_state != "Active":
                self.event_queue.put({"state": "Active"})
                self.previous_state = "Active"
        else: # default to sleep
            if self.previous_state != "Sleep":
                self.event_queue.put({"state": "Sleep"})
                self.previous_state = "Sleep"

        # If the transition from one state to another requires a specific sequence of events
        # to occur to safely transition, then the deliberate layer would be responsible for
        # managing it.