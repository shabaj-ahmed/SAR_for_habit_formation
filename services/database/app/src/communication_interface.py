import json
import time
from PIL import Image
import io
import sys
import os
import logging

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)

from shared_libraries.mqtt_client_base import MQTTClientBase

class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port, event_dispatcher):
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dispatcher = event_dispatcher

        self.start_command = ""

        self.service_status = "Awake" # As soon as the robot controller starts, it is awake

        # Subscription topics
        self.service_status_requested_topic = "request/service_status"
        self.service_control_cmd = "database_control_cmd"
        self.update_robot_settings = "update_robot_settings"

        # Publish topics
        self.database_service_status_topic = "database_status"
        self.robot_control_state_topic = "robot_control_state"
        self.voice_assistant_state_topic = "voice_assistant_state"
        self.user_interface_state_topic = "user_interface_state"

        # Subscribe to necessary topics
        self.subscribe(self.service_status_requested_topic, self._respond_with_service_status)
        self.subscribe(self.service_control_cmd, self._handle_control_command)
    
    def _respond_with_service_status(self, client, userdata, message):
        self.publish_database_status(self.service_status)
    
    def _handle_control_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            command = payload.get("cmd", "")
            self.dispatcher.dispatch_event("control_command", command)

            status_response = {
                "set_up": "ready",
                "start": "running",
                "end": "completed"
            }

            self.publish_database_status(status_response.get(command, "running"))
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload. Using default retry parameters.")
    
    
    def publish_database_status(self, status, message="", details=None):
        logging.info(f"Publishing database status: {status}")        
        payload = {
            "service_name": "database",
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.database_service_status_topic, json.dumps(payload))

        self.service_status = status