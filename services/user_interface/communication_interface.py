import json
import sys
import os
import time
import logging

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.insert(0, project_root)
print(f"project_root: {project_root}")

from shared_libraries.mqtt_client_base import MQTTClientBase

class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port, event_dispatcher):
        # Initialize QObject explicitly (no arguments are required for QObject)
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dispatcher = event_dispatcher

        self.service_status = "Awake"

        self.inputs = {
            'switch_state': False,
            'error': False,
            'audioActive': False,
            'cameraActive': False,
            'wifiActive': False,
        }
        self.system_status = {}
        self.check_in_status = False

        # Set up the message callbacks
        self.message_callback = None
        self.error_callback = None
        self.socketio = None

        # Subscription topics
        self.service_status_requested_topic = "request/service_status"
        self.update_system_status_topic = "publish/system_status"
        self.user_interface_control_cmd_topic = "user_interface_control_cmd"
        self.silence_detected_topic = "speech_recognition/silence_detected"
        self.conversation_history_topic = "conversation/history"
        self.camera_active_topic = "robot/cameraActive"
        self.audio_active_topic = "audio_active"
        self.update_state_topic = "service/user_interface/update_state"
        self.error_message_topic = "error_message"
        self.behaviour_status_update_topic = "behaviour_status_update"
        self.robot_connection_status_topic = "robot_connection_status"
        self.network_status_topic = "network_status"
        self.network_speed_topic = "network_speed"
        self.study_history_topic = "study_history"

        # Publish topics
        self.user_interface_status_topic = "user_interface_status"
        self.robot_volume_topic = "robot_volume"
        self.robot_colour_topic = "robot_colour"
        self.update_persistent_data = "update_persistent_data"
        self.save_check_in_topic = "save_check_in"
        self.service_error_topic = "service_error"
        self.reconnect_request_topic = "reconnect_robot_request"
        self.wake_up_screen_topic = "wake_up_screen"
        self.update_persistent_data_topic = "update_persistent_data"
        self.service_control_cmd = "database_control_cmd"
        self.configuration_controls_topic = "configuration_controller"

        # Subscriber and publisher topics
        self.check_in_controls_topic = "check_in_controller"

        # Subscribe to topics
        self.subscribe(self.service_status_requested_topic, self._respond_with_service_status)
        self.subscribe(self.update_system_status_topic, self._update_system_status)
        self.subscribe(self.check_in_controls_topic, self._process_check_in_commands)
        self.subscribe(self.user_interface_control_cmd_topic, self._process_control_command)
        self.subscribe(self.silence_detected_topic, self._process_silence_detected)
        self.subscribe(self.conversation_history_topic, self._on_message)
        self.subscribe(self.camera_active_topic, self._process_camera_active)
        self.subscribe(self.audio_active_topic, self._process_audio_active)
        self.subscribe(self.error_message_topic, self._process_error_message)
        self.subscribe(self.update_state_topic, self._update_service_state)
        self.subscribe(self.behaviour_status_update_topic, self._process_behaviour_status_update)
        self.subscribe(self.robot_connection_status_topic, self._process_robot_connection_status)
        self.subscribe(self.network_status_topic, self._process_network_connection_status)
        self.subscribe(self.network_speed_topic, self._process_network_connection_speed)
        self.subscribe(self.study_history_topic, self._process_study_history)

        self._register_event_handlers()

    def _register_event_handlers(self):
        self.dispatcher.register_event("send_service_error", self.publish_service_error)
        self.dispatcher.register_event("all_states_updated", self.all_states_updated)

    def _respond_with_service_status(self, client, userdata, message):
        self.logger.info(f"service_status_requested_topic received, current status: {self.service_status}")
        self.publish_UI_status(self.service_status)

    def _update_system_status(self, client, userdata, message):
        serviceStatus = json.loads(message.payload.decode("utf-8"))
        self.logger.info(f"User interface service status dictionary: {serviceStatus}")

        # Rename the keys to make it more user-friendly
        re_name_service = {
            "user_interface": "User Interface",
            "speech_recognition": "Speech Recognition",
            "peripherals": "Peripheral Devices",
            "database": "Database",
            "reminder": "Reminder",
            "robot_control": "Study Condition",
        }
        for old_key, new_key in re_name_service.items():
            serviceStatus[new_key] = serviceStatus.pop(old_key)

        self.socketio.emit('service_status', serviceStatus)
        self.system_status = serviceStatus
        still_loading = False
        self.logger.info(f"Service status: {serviceStatus}")
        for key, value in serviceStatus.items():
            if value != "set_up":
                still_loading = True
        if still_loading == False:
            self.logger.info("Sending loading_complete event")
            self.socketio.emit('loading_complete')

    def _process_check_in_commands(self, client, userdata, message):
        if message.payload.decode() == '1':
            self.logger.info("Starting check-in")
            self.check_in_status = True
        elif message.payload.decode() == '0':
            self.logger.info("Ending check-in")
            self.socketio.emit('check_in_complete')
            self.check_in_status = False

    def _process_control_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            message = payload.get("cmd", "")
            self.logger.info(f"User Interface received the command = {message}")
            self.start_command = message
            if message == "set_up":
                # Check to see if the screen is turned on
                logging.info("UI publishing ready")
                self.publish_UI_status("ready")
            elif message == "start":
                logging.info("UI publishing that it is running")
                self.publish_UI_status("running")
            elif message == "end":
                # put the screen in stand-by or go to home page
                self.publish_UI_status("completed")
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload. Using default retry parameters.")

    def _process_silence_detected(self, client, userdata, message):
        duration = message.payload.decode()
        self.logger.info(f"Silence detected: {duration}")
        self.socketio.emit('silence_detected', {'duration': duration})

    def _on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"Message received on '{self.conversation_history_topic}, payload: {payload}")
            if self.message_callback:
                self.message_callback(payload)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON payload: {e}")

    def _process_camera_active(self, client, userdata, message):
        camera_active = message.payload.decode() == '1'
        self.logger.info(f"Camera active: {camera_active}")
        if self.socketio:
            self.logger.info("Emitting cam_status event to clients")
            self.dispatcher.dispatch_event("update_connectoin_status", {'key': 'cam', 'status': camera_active})

    def _process_audio_active(self, client, userdata, message):
        audio_active = json.loads(message.payload.decode("utf-8")) == '1'
        self.logger.info(f"Microphone active: {audio_active}")
        self.inputs['audioActive'] = audio_active
        if self.socketio:
            self.logger.info("Emitting mic_status event to clients")
            self.dispatcher.dispatch_event("update_connectoin_status", {'key': 'mic', 'status': audio_active})

    def _process_error_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"################################### RECIVED ERROR MESSAGE: {payload}")
            self.logger.info(f"Error message received on '{self.error_message_topic}, payload: {payload}")
            self.socketio.emit('error_message', payload)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON payload: {e}")

    def _update_service_state(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            state_name = payload.get("state_name", "")
            state = payload.get("state_value", "")
            self.logger.info(f"User interface received state update for {state_name}: {state}")
            self.dispatcher.dispatch_event("update_service_state", payload)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for updating service state. Using default retry parameters.")

    def all_states_updated(self):
        self.service_status = "set_up"        
    
    def _process_behaviour_status_update(self, client, userdata, message):
        # try:
        # payload = json.loads(message.payload.decode("utf-8"))
        message = message.payload.decode("utf-8")
        self.logger.info(f"Behaviour status update received: {message}")
        self.socketio.emit("loading_status", {'message': message})
        # except json.JSONDecodeError as e:
        #     self.logger.error(f"Error decoding JSON payload: {e}")
    
    def _process_robot_connection_status(self, client, userdata, message):
        status = json.loads(message.payload.decode("utf-8")).get("status", "") == "connected"
        self.logger.info(f"Robot connection status in UI: {status}")
        self.dispatcher.dispatch_event("update_connectoin_status", {'key': 'robot', 'status': status})

    def _process_network_connection_status(self, client, userdata, message):
        status = json.loads(message.payload.decode("utf-8")).get("status", "") == "connected"
        self.logger.info(f"Network connection status in UI: {status}")
        self.dispatcher.dispatch_event("update_connectoin_status", {'key': 'wifi', 'status': status})

    def _process_network_connection_speed(self, client, userdata, message):
        download_speed = json.loads(message.payload.decode("utf-8")).get("download", 0)
        upload_speed = json.loads(message.payload.decode("utf-8")).get("upload", 0)
        self.logger.info(f"Network connection speed in UI: Download = {download_speed}Mbps, Upload = {upload_speed}Mbps")
        self.dispatcher.dispatch_event("update_connectoin_status", {'key': 'wifi_download_speed', 'status': download_speed})
        self.dispatcher.dispatch_event("update_connectoin_status", {'key': 'wifi_upload_speed', 'status': upload_speed})

    def _process_study_history(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"Study history received: {payload}")
            time.sleep(1)
            self.socketio.emit('study_history', payload)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON payload: {e}")

    def publish_service_error(self, error_message):
        self.publish(self.service_error_topic, error_message)

    def publish_reconnect_request(self, sender):
        payload = {
            "sender": sender,
            "service_name": "user_interface",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.reconnect_request_topic, json.dumps(payload))

    def start_check_in(self):
        if self.check_in_status != True:
            self.logger.info("Sending check-in start command")
            self.publish(self.check_in_controls_topic, "1")

    def configuration_controller(self, command):
        if command == "start":
            self.logger.info("Sending start configuring command")
            self.publish(self.configuration_controls_topic, "1")
        elif command == "end":
            self.logger.info("Sending end configuring command")
            self.publish(self.configuration_controls_topic, "0")
    
    def change_colour(self, selected_colour):
        self.logger.info(f"Sending colour change command: {selected_colour}")
        # self.publish(self.robot_colour_topic, selected_colour)
        self.publish(self.update_persistent_data_topic, json.dumps({"service_name": "user_interface", "state_name": "robot_colour", "state_value": selected_colour}))
    
    def change_volume(self, volume):
        self.logger.info(f"Sending volume change command: {volume}")
        self.publish(self.robot_volume_topic, volume)
        self.publish(self.update_persistent_data_topic, json.dumps({"service_name": "user_interface", "state_name": "robot_volume", "state_value": volume}))

    def change_brightness(self, brightness):
        self.logger.info(f"brightness value is being updated to: {brightness}")
        self.publish(self.update_persistent_data_topic, json.dumps({"service_name": "user_interface", "state_name": "brightness", "state_value": brightness}))

    def publish_UI_status(self, status, message="", details=None):
        self.logger.info(f"Publishing UI status: {status}")
        payload = {
            "service_name": "user_interface",
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.user_interface_status_topic, json.dumps(payload))

        self.service_status = status

    def request_study_history(self):
        self.logger.info("Requesting study history")
        payload = {
            "cmd": "request_history"
        }
        self.publish(self.service_control_cmd, json.dumps(payload))

    def wake_up_screen(self):
        # self.logger.info("Waking up screen")
        self.publish(self.wake_up_screen_topic, json.dumps({"cmd": "wake_up"}))

    def save_check_in(self, check_in_data):
        self.publish(self.save_check_in_topic, json.dumps(check_in_data))
        self.logger.info(f"Check-in data sent to the database service, Payload: {check_in_data}")

    def set_reminder_time(self, hours = 0, minutes = 0, ampm = "AM"):
        self.logger.info(f"Setting reminder time to {hours}:{minutes} {ampm}")
        states = [
            ["reminder_time_hr", hours],
            ["reminder_time_min", minutes],
            ["reminder_time_ampm", ampm]
        ]

        for state in states:
            payload = {
                "service_name": "reminder",
                "state_name": state[0],
                "state_value": state[1]
            }
            self.logger.info(f"Sending reminder time update: {payload}")
            self.publish(self.update_persistent_data, json.dumps(payload))

    def get_system_status(self):
        return self.system_status
