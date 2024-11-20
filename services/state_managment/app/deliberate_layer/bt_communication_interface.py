import sys
import os

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from shared_libraries.mqtt_client_base import MQTTClientBase


class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port):
        super().__init__(broker_address, port)
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
        self.subscribe("user/check_in", self._process_check_in)
        self.subscribe("user/configurations", self._process_configurations)
        self.subscribe("robot/reminder", self._process_reminder_status)
        self.subscribe("robot/check_in_status", self._process_check_in_status)
        self.subscribe("robot/error", self._process_error_message)

    def _process_check_in(self, client, userdata, message):
        print("Processing check in")
        print("Check in message received")
        if message.payload.decode() == '1':
            self.userEvents['check_in'] = True
        else:
            self.userEvents['check_in'] = False
            self.userEvents['configurations'] = False

    def _process_configurations(self, client, userdata, message):
        print("Processing configurations")
        print("Configurations message received")
        if message.payload.decode() == '1':
            self.userEvents['configurations'] = True
        else:
            self.userEvents['configurations'] = False
            self.userEvents['check_in'] = False

    def _process_reminder_status(self, client, userdata, message):
        print("Processing reminder status")
        print("Reminder message received")
        if message.payload.decode() == 'running':
            self.behaviourCompletionStatus['reminder'] = True
        elif message.payload.decode() == 'completed':
            self.behaviourCompletionStatus['reminder'] = False
            self.userEvents['configurations'] = False
            self.userEvents['check_in'] = False

    def _process_check_in_status(self, client, userdata, message):
        print("Processing check in status")
        print("Check in message received")
        if message.payload.decode() == 'running':
            self.behaviourCompletionStatus['check_in'] = True
        elif message.payload.decode() == 'completed':
            self.behaviourCompletionStatus['check_in'] = False
            self.userEvents['configurations'] = False
            self.userEvents['check_in'] = False

    def _process_error_message(self, client, userdata, message):
        print("Processing error message")
        self.criticalEvents['error'] = message.payload.decode()
    
    def get_user_event(self):
        return self.userEvents
    
    def get_behaviour_completion_status(self):
        return self.behaviourCompletionStatus