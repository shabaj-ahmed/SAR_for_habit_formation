import json
import time
import sys
import os
import logging

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)

from shared_libraries.mqtt_client_base import MQTTClientBase

class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port, reminder_controler):
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.reminder_controler = reminder_controler

        self.command = "" # used in main loop to determine what to do

        self.service_status = "Awake" # As soon as the reminder starts, it is awake

        # Subscription topics
        self.service_status_requested_topic = "request/service_status"
        self.control_cmd = "reminder_control_cmd"
        self.update_reminder_time = "update_reminder_time"

        # Publish topics
        self.reminder_status_topic = "reminder_status"
        self.reminder_hearbeat_topic = "reminder_heartbeat"

        # subscribe to topics
        self.subscribe(self.service_status_requested_topic, self._respond_with_service_status)
        self.subscribe(self.control_cmd, self._handle_command)
        self.subscribe(self.update_reminder_time, self._update_reminder_time)

    def _respond_with_service_status(self, client, userdata, message):
        self.publish_reminder_status(self.service_status)
    
    def _handle_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            cmd = payload.get("cmd", "")
            logging.info(f"vocie assistant received the command: {cmd}")
            self.logger.info(f"cmd = {cmd}")
            if cmd == "end":
                self.command = ""
            elif cmd == "set_up" or cmd == "start":
                self.command = cmd
            else:
                self.command = ""
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for control commands. Using default retry parameters.")

    def _update_reminder_time(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            hours = int(payload.get("hours", 0))
            minutes = int(payload.get("minutes", 0))
            ampm = payload.get("ampm", "AM")
            self.reminder_controler.set_reminder_time(hours, minutes, ampm)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for setting reminder time. Using default retry parameters.")

    def publish_reminder_status(self, status, message="", details=None):
        if status == "running":
            self.publish(self.audio_active_topic, "1")
        if status == "completed":
            self.command = False
            self.publish(self.audio_active_topic, "0")
        
        payload = {
            "service_name": "reminder",
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.reminder_status_topic, json.dumps(payload))

        self.service_status = status

    def publish_reminder_heartbeat(self):
        payload = {
            "service_name": "reminder",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.vocie_assistant_hearbeat_topic, json.dumps(payload))

    def get_command(self):
        return self.command