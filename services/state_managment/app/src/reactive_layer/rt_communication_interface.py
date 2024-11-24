import sys
import os
import logging

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
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

        # Subscribe to topics with custom handlers
        self.subscribe("robot/switch_state", self._process_switch_state)
        self.subscribe("robot/reminder", self._process_reminder_status)
        self.subscribe("robot/error", self._process_error_message)

    def _process_switch_state(self, client, userdata, message):
        self.logger.info("Processing switch state")
        self.criticalEvents['switch_state'] = message.payload.decode()

    def _process_reminder_status(self, client, userdata, message):
        self.logger.info("Processing reminder status")
        if message.payload.decode() == 'running':
            self.behaviourCompletionStatus['reminder'] = True
        elif message.payload.decode() == 'completed':
            self.behaviourCompletionStatus['reminder'] = False
            self.userEvents['configurations'] = False
            self.userEvents['check_in'] = False

    def _process_error_message(self, client, userdata, message):
        self.logger.info("Processing error message")
        self.criticalEvents['error'] = message.payload.decode()

    def get_critical_events(self):
        return self.criticalEvents
