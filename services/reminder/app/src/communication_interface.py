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
    def __init__(self, broker_address, port, event_dispatcher):
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dispatcher = event_dispatcher

        self.command = "" # used in main loop to determine what to do

        self.service_status = "Awake" # As soon as the reminder starts, it is awake

        # Subscription topics
        self.service_status_requested_topic = "request/service_status"
        self.control_cmd = "reminder_control_cmd"
        self.update_reminder_time = "update_reminder_time"

        # Publish topics
        self.reminder_status_topic = "reminder_status"
        self.reminder_hearbeat_topic = "reminder_heartbeat"
        self.start_reminder_topic = "start_reminder"

        # subscribe to topics
        self.subscribe(self.service_status_requested_topic, self._respond_with_service_status)
        self.subscribe(self.control_cmd, self._handle_command)
        self.subscribe(self.update_reminder_time, self._update_reminder_time)

        self._register_event_handlers()

    def _register_event_handlers(self):
        if self.dispatcher:
            self.dispatcher.register_event("send_reminder", self._send_reminder)

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

            status = {
                "set_up": "ready",
                "start": "running",
                "end": "completed"
            }
            
            self.publish_reminder_status(status[cmd])
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for control commands. Using default retry parameters.")

    def _update_reminder_time(self, client, userdata, message):
        try:
            time = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"Reminder time updated to {time}")
            self.dispatcher.dispatch_event("set_reminder", time)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for setting reminder time. Using default retry parameters.")

    def publish_reminder_status(self, status, message="", details=None):        
        payload = {
            "service_name": "reminder",
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.reminder_status_topic, json.dumps(payload))

        self.service_status = status

    def _send_reminder(self):
        self.logger.info("Sending reminder")
        self.publish(self.start_reminder_topic, "1")

    def publish_reminder_heartbeat(self):
        payload = {
            "service_name": "reminder",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.vocie_assistant_hearbeat_topic, json.dumps(payload))

    def get_command(self):
        return self.command