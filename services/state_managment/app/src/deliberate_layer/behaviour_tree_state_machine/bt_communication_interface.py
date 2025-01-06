import json
import sys
import os
import logging
import time

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)

from shared_libraries.mqtt_client_base import MQTTClientBase

class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port):
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.subscriptions = {}

        # Behaviour running status used activate/deactivate certain behaviours
        self.behaviourRunningStatus = {
            'reminder': "disabled",
            'check_in': "disabled",
            'configurations': "disabled"
        }

        self.systemStatus = {
            "speech_recognition": "",
            "robot_control": "",
            "user_interface": "",
            "reminder": "",
            "database": "",
            "peripherals": ""
        }

        self.robot_behaviour_completion_status = {}
        self.user_response = ""

        # Subscription topics
        self.reminder_status_topic = "reminder_status"
        self.reminder_heartbeat_topic = "reminder_heartbeat"
        self.speech_recognition_status_topic = "speech_recognition_status"
        self.speech_recognition_heartbeat_topic = "speech_recognition_heartbeat"
        self.robot_status_topic = "robot_status"
        self.robot_heartbeat_topic = "robot_heartbeat"
        self.user_interface_status_topic = "user_interface_status"
        self.user_interface_heartbeat_topic = "user_interface_heartbeat"
        self.configure_topic = "configure"
        self.service_error_topic = "service_error"
        self.robot_control_status_topic = "robot_control_status"
        self.conversation_history_topic = "conversation/history"
        self.send_reminder_topic = "start_reminder"
        self.database_status_topic = "database_status"
        self.peripherals_status_topic = "peripherals_status"

        # Publish topics
        self.request_service_status_topic = "request/service_status"
        self.publish_system_status_topic = "publish/system_status"
        self.robot_speech_topic = "robot_tts"
        self.robot_behaviour_topic = "robot_behaviour_command"
        self.service_control_command_topic = lambda service_name : service_name + "_control_cmd"
        self.save_reminder_topic = "save_reminder"
        self.peripheral_control_cmd = "peripherals_control_cmd" # Replace with service_control_command_topic
        self.behaviour_status_update_topic = "behaviour_status_update"

        # Subscriber and publisher topics
        self.check_in_controls_topic = "check_in_controller"

        # Subscribe to topics with custom handlers
        self.subscribe(self.check_in_controls_topic, self._process_check_in_request)
        self.subscribe(self.speech_recognition_status_topic, self._process_service_status)
        # self.subscribe(self.speech_recognition_heartbeat_topic, self._process_heartbeat)
        self.subscribe(self.robot_status_topic, self._process_service_status)
        # self.subscribe(self.robot_control_status_topic, self._process_heartbeat)
        self.subscribe(self.user_interface_status_topic, self._process_service_status)
        # self.subscribe(self.user_interface_status_topic, self._process_heartbeat)
        self.subscribe(self.reminder_status_topic, self._process_service_status)
        # self.subscribe(self.reminder_heartbeat_topic, self._process_heartbeat)
        self.subscribe(self.database_status_topic, self._process_service_status)
        self.subscribe(self.peripherals_status_topic, self._process_service_status)
        self.subscribe(self.configure_topic, self._process_configurations)
        self.subscribe(self.service_error_topic, self._process_error_message)
        self.subscribe(self.robot_control_status_topic, self._process_robot_behaviour_status)
        self.subscribe(self.conversation_history_topic, self._handle_user_response)
        self.subscribe(self.send_reminder_topic, self._send_reminder)

    def _process_check_in_request(self, client, userdata, message):
        '''
        Process the check in request from the user interface
        
        Args:
            message (str): A string flag indicating the check in status
                '1' - Start check in
                '0' - End check in
        '''
        self.logger.info("Processing check in")
        if message.payload.decode() == '1':
            self.behaviourRunningStatus['check_in'] = "enabled"
            # Transition to check in branch
            self.logger.info("Starting check in")
        else:
            for behaviour in self.behaviourRunningStatus:
                self.behaviourRunningStatus[behaviour] = "disabled"
            self.logger.info("Ending check in")

    def _process_service_status(self, client, uesrdata, message):
        '''
        Process the status of the services to update the current of the entier system status
        
        Args:
            message (dict): A dictionary containing the message payload
                message = {
                    "service_name": str,
                    "status": str,
                    "message": str,
                    "details": str,
                    "timestamp": "%Y-%m-%d %H:%M:%S"
                }
        '''
        payload = json.loads(message.payload.decode("utf-8"))
        service = payload.get("service_name", "")
        status = payload.get("status", "")

        self.systemStatus[service] = status

    def _process_configurations(self, client, userdata, message):
        self.logger.info("Processing configurations")
        if message.payload.decode() == '1':
            self.behaviourRunningStatus['configurations'] = "enabled"
        else:
            self.behaviourRunningStatus['configurations'] = "disabled"

    def _process_error_message(self, client, userdata, message):
        self.logger.info("Processing error message")
        # self.criticalEvents['error'] = message.payload.decode()

    def _process_robot_behaviour_status(self, client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        behaviour_name = payload.get("behaviour_name", "")
        behaviour_status = payload.get("status", "")
        self.logger.info(f"behaviour status recived = {behaviour_status} for behaviour name = {behaviour_name}")
        self.robot_behaviour_completion_status[behaviour_name] = behaviour_status

    def _handle_user_response(self, client, userdata, message):
        self.logger.info(f"the user response is {message.payload.decode()}")
        payload = json.loads(message.payload.decode("utf-8"))
        self.user_response = payload.get("content", None)

    def _send_reminder(self, client, userdata, message):
        self.logger.info("Processing reminder request")
        if message.payload.decode() == '1':
            self.behaviourRunningStatus['reminder'] = "enabled"
            self.logger.info("enable reminder")
        else:
            self.behaviourRunningStatus['reminder'] = "disabled"
            self.logger.info("disable reminder")

    def request_service_status(self):
        '''
        Request a response from all services to get their status
        '''
        # self.logger.info("Requesting service status")
        self.publish(self.request_service_status_topic, "")

    def publish_system_status(self):
        '''
        Publish the system status to all services
        '''
        self.logger.info("Publishing system status")
        self.publish(self.publish_system_status_topic, json.dumps(self.systemStatus))

    def publish_robot_speech(self, content, message_type="request"):
        message = {
            "sender": "orchestrator",
            "message_type": message_type,
            "content": content
        }
        self.logger.info(f"sending message {message}")
        json_message = json.dumps(message)
        # This is what the robot should say
        self.publish(self.robot_speech_topic, json_message)

    def publish_robot_behaviour_command(self, cmd, message_type="request"):
        message = {
            "sender": "orchestrator",
            "message_type": message_type,
            "cmd": cmd,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        json_message = json.dumps(message)
        # This is what the robot should do
        self.publish(self.robot_behaviour_topic, json_message)

    def publish_collect_response(self, expected_format):
        self.logger.info("Publishing record response")
        service_name = "speech_recognition"
        payload = {
            "service_name": service_name,
            "cmd": expected_format,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.service_control_command_topic(service_name), json.dumps(payload))

    def publish_reminder_sent(self, payload):
        self.logger.info("Saving reminder message to the database")
        self.publish(self.save_reminder_topic, json.dumps(payload))

    def publish_behaviour_status_update(self, status):
        self.logger.info(f"Publishing behaviour status update: {status}")
        # payload = {
        #     "status": status,
        #     "time": time.strftime("%Y-%m-%d %H:%M:%S")
        # }
        self.publish(self.behaviour_status_update_topic, status)

    def behaviour_timeout(self, command):
        payload = {
            "service_name": "robot_control",
            "cmd": command + "_timeout",
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.logger.info(f"Publishing service control command to {self.service_control_command_topic('robot_control')} with command: {command}")
        self.publish(self.service_control_command_topic('robot_control'), json.dumps(payload))

    def behaviour_controller(self, service_name, cmd):
        payload = {
            "service_name": service_name,
            "cmd": cmd,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.logger.info(f"Publishing service control command to {self.service_control_command_topic(service_name)} with command: {cmd}")
        self.publish(self.service_control_command_topic(service_name), json.dumps(payload))

    def end_check_in(self):
        logging.info("Ending check-in")
        self.publish(self.check_in_controls_topic, "0")

    def get_system_status(self):
        '''
        A method to expose the service status or all services
        '''
        return self.systemStatus

    def get_behaviour_running_status(self):
        return self.behaviourRunningStatus
    
    def set_behaviour_running_status(self, behaviour, status):
        self.behaviourRunningStatus[behaviour] = status

    def get_robot_behaviour_completion_status(self, behaviour_name):
        status = self.robot_behaviour_completion_status.get(behaviour_name, "")
        return status
    
    def acknowledge_robot_behaviour_completion_status(self, behaviour_name):
        self.robot_behaviour_completion_status.pop(behaviour_name)
    
    def get_user_response(self):
        return self.user_response