import json
import sys
import os
import time

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, project_root)
print(f"project_root: {project_root}")

from shared_libraries.mqtt_client_base import MQTTClientBase
import logging


class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port):
        # Initialize QObject explicitly (no arguments are required for QObject)
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.on_message = self.on_message
        self.message_callback = None
        self.socketio = None
        
        self.inputs = {
            'switch_state': False,
            'error': False,
            'audioActive': False,
            'cameraActive': False,
            'wifiActive': False,
        }
        self.subscribe_to_topics()

    def subscribe_to_topics(self):
        self.subscribe("robot/switch_state", self._process_switch_state)

        self.subscribe("robot/error", self._process_error_message)

        self.subscribe("robot/audioActive", self._process_audio_active)

        self.subscribe("robot/cameraActive", self._process_camera_active)
        
        self.subscribe("conversation/history", self._on_message)

    # Use QMetaObject.invokeMethod to ensure signal emission in the main thread
    def _process_switch_state(self, client, userdata, message):
        switch_state = message.payload.decode()

    def _process_error_message(self, client, userdata, message):
        error_message = message.payload.decode()

    def _process_audio_active(self, client, userdata, message):
        audio_active = message.payload.decode() == '1'
        self.logger.info(f"Microphone active: {audio_active}")
        if self.socketio:
            self.logger.info("Emitting mic_status event to clients")
            self.socketio.emit('mic_status', {'active': audio_active})

    def _process_camera_active(self, client, userdata, message):
        camera_active = message.payload.decode() == '1'
        self.logger.info(f"Camera active: {camera_active}")
        if self.socketio:
            self.logger.info("Emitting cam_status event to clients")
            self.socketio.emit('cam_status', {'active': camera_active})


    def _on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"Message received on 'conversation/history, payload: {payload}")
            if self.message_callback:
                self.message_callback(payload)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON payload: {e}")

    # These methods will be called safely from the main thread
    def emit_switch_state_signal(self, switch_state):
        pass

    def emit_error_signal(self, error_message):
        pass

    def emit_audio_signal(self, audio_active):
        pass

    def emit_camera_signal(self, camera_active):
        pass

    def get_inputs(self):
        return self.inputs

    def start_check_in(self):
        self.publish("user/check_in", "1")

    def publish_status(self, status, message="", details=None):
        payload = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish("UI_status", json.dumps(payload))
