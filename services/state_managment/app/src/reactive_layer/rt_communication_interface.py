import sys
import os
import logging

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../../"))
sys.path.insert(0, project_root)

from shared_libraries.mqtt_client_base import MQTTClientBase

class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port):
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.criticalEvents = {
            'switch_state': False,
            'reminder': False,
            'error': False
        }

        # Subscription topics
        self.switch_state_topic = "system_switch_state"
        self.critial_error_topic = "error_message"
        self.critical_error_resolved_topic = "critical_event_resolved"

        # Subscribe to topics with custom handlers
        self.subscribe(self.switch_state_topic, self._process_switch_state)
        self.subscribe(self.critial_error_topic, self._process_error_message)
        self.subscribe(self.critical_error_resolved_topic, self._process_error_resolved_message)

    def _process_switch_state(self, client, userdata, message):
        self.logger.info("Processing switch state")
        self.criticalEvents['switch_state'] = message.payload.decode()

    def _process_error_message(self, client, userdata, message):
        self.logger.info("Processing error message")
        self.criticalEvents['error'] = True

    def _process_error_resolved_message(self, client, userdata, message):
        self.logger.info("Processing resolved error message")
        self.criticalEvents['error'] = False

    def get_critical_events(self):
        return self.criticalEvents
