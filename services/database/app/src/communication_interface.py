import json
import time
import sys
import os
import logging
import collections

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
        self.update_persistent_data_topic = "update_persistent_data"
        self.save_check_in_topic = "save_check_in"
        self.save_reminder_topic = "save_reminder"

        # Publish topics
        self.database_service_status_topic = "database_status"
        self.robot_control_state_topic = "robot_control_state"
        self.voice_assistant_state_topic = "voice_assistant_state"
        self.user_interface_state_topic = "user_interface_state"

        # Subscribe to necessary topics
        self.subscribe(self.service_status_requested_topic, self._respond_with_service_status)
        self.subscribe(self.service_control_cmd, self._handle_control_command)
        self.subscribe(self.save_check_in_topic, self._save_check_in)
        self.subscribe(self.update_persistent_data_topic, self._update_persistent_data)
        self.subscribe(self.save_reminder_topic, self._save_reminder)

        self._register_event_handlers()

    def _register_event_handlers(self):
        """Register event handlers for robot actions."""
        if self.dispatcher:
            self.dispatcher.register_event("publish_service_state", self.publish_service_states)
    
    def _respond_with_service_status(self, client, userdata, message):
        self.publish_database_status(self.service_status)
    
    def _handle_control_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            command = payload.get("cmd", "")

            if command == "update_system_state":
                self.dispatcher.dispatch_event("service_control_command", command)
                self.logger.info("Sending update system state to all services")

            status_response = {
                "set_up": "ready",
                "start": "running",
                "end": "completed",
                "update_system_state": "set_up"
            }
            self.publish_database_status(status_response.get(command, "running"))
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload. Using default retry parameters.")

    def _save_check_in(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"Saving check-in data: {payload}")
            self.dispatcher.dispatch_event("save_check_in", payload)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for check-in data. Unable to save check-in data.")
    
    def _save_reminder(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"Saving reminder: {payload}")
            reminder_message = payload.get("reminder_message", "")
            self.dispatcher.dispatch_event("create_new_reminder", reminder_message)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for reminder. Unable to save reminder data.")

    def _update_persistent_data(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"Updating persistent data: {payload}")
            self.dispatcher.dispatch_event("update_service_states", payload)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for persistent data. Unable to update persistent data.")
    
    def publish_service_states(self, upated_state):
        """
        Clusters service states and publishes them to the appropriate MQTT topics.
        """
        if type(upated_state) is collections.defaultdict:
            self.logger.info(f"Publishing service states: {upated_state}")
            for service_name, state_values in upated_state.items():
                topic = f"service/{service_name}/update_state"
                for state in state_values:
                    payload = {"state_name": state["state_name"], "state_value": state["state_value"]}
                    self.publish(topic, json.dumps(payload))
                # Publish that database has completed setting up the service
        else:
            payload = {"state_name": upated_state["state_name"], "state_value": upated_state["state_value"]}
            service_name = upated_state["service_name"]
            topic = f"service/{service_name}/update_state"
            self.publish(topic, json.dumps(payload))
    
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