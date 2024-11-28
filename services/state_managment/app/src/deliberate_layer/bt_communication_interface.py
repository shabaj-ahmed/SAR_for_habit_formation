import json
import sys
import os
import logging
import time

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from shared_libraries.mqtt_client_base import MQTTClientBase


class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port):
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.subscriptions = {}

        self.userEvents = {
            'check_in': False,
            'configurations': False
        }
        self.behaviourCompletionStatus = {
            'reminder': False,
            'check_in': False,
            'configurations': False
        }

        # Subscribe to topics with custom handlers
        self.subscribe("start_check_in", self._process_check_in_request)
        self.subscribe("voice_assistant_status", self._process_voice_assistant_status)
        self.subscribe("configure", self._process_configurations)
        self.subscribe("reminder", self._process_reminder_status)
        self.subscribe("service_error", self._process_error_message)

    def _process_check_in_request(self, client, userdata, message):
        self.logger.info("Processing check in")
        if message.payload.decode() == '1':
            self.userEvents['check_in'] = True
            self.logger.info("Starting check in")
        else:
            self.userEvents['check_in'] = False
            self.logger.info("Ending check in")
    
    def _process_voice_assistant_status(self, client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        message = payload.get("status", "")
        self.logger.info(f"Processing voice assistant status: {message}")
        if message == 'completed':
            self.behaviourCompletionStatus['check_in'] = False
        elif message == 'running':
            self.behaviourCompletionStatus['check_in'] = True

    def _process_configurations(self, client, userdata, message):
        self.logger.info("Processing configurations")
        if message.payload.decode() == '1':
            self.userEvents['configurations'] = True
        else:
            self.userEvents['configurations'] = False

    def _process_reminder_status(self, client, userdata, message):
        self.logger.info("Processing reminder status")
        if message.payload.decode() == 'running':
            self.behaviourCompletionStatus['reminder'] = True
        elif message.payload.decode() == 'completed':
            self.behaviourCompletionStatus['reminder'] = False
            self.userEvents['check_in'] = False

    def _process_error_message(self, client, userdata, message):
        self.logger.imfo("Processing error message")
        self.criticalEvents['error'] = message.payload.decode()

    def check_in_status(self, message):
        if message == "completed":
            self.userEvents['check_in'] = True
        payload = {
            "message": message,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish("check_in_status", json.dumps(payload))

    def get_user_event(self):
        return self.userEvents

    def get_behaviour_completion_status(self):
        return self.behaviourCompletionStatus