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

        self.inputs = {
            'switch_state': False,
            'error': False,
            'audioActive': False,
            'cameraActive': False,
            'wifiActive': False,
        }
        self.check_in_status = False

        # Set up the message callbacks
        self.message_callback = None
        self.socketio = None

        # Subscribe to topics
        self.subscribe("check_in_status", self._process_check_in_status)
        self.subscribe("conversation/history", self._on_message)
        self.subscribe("robot/cameraActive", self._process_camera_active)
        self.subscribe("audio_active", self._process_audio_active)
        self.subscribe("robot/error", self._process_error_message)

    def _process_check_in_status(self, client, userdata, message):
        payload = json.loads(message.payload.decode("utf-8"))
        message = payload.get("message", "")
        if message == "started" or message == "running":
            self.socketio.emit('mic_status', {'active': True})
            self.socketio.emit('cam_status', {'active': True})
            self.check_in_status = True
        if message == 'completed' or message == 'end':
            self.socketio.emit('mic_status', {'active': False})
            self.socketio.emit('cam_status', {'active': False})
            self.socketio.emit('check_in_complete')
            self.check_in_status = False
            self.logger.info("Ending check-in")

    def _on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"Message received on 'conversation/history, payload: {payload}")
            if self.message_callback:
                self.message_callback(payload)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON payload: {e}")

    def _process_camera_active(self, client, userdata, message):
        camera_active = message.payload.decode() == '1'
        self.logger.info(f"Camera active: {camera_active}")
        if self.socketio:
            self.logger.info("Emitting cam_status event to clients")
            self.socketio.emit('cam_status', {'active': camera_active})

    def _process_audio_active(self, client, userdata, message):
        audio_active = message.payload.decode() == '1'
        self.logger.info(f"Microphone active: {audio_active}")
        self.inputs['audioActive'] = audio_active
        if self.socketio:
            self.logger.info("Emitting mic_status event to clients")
            self.socketio.emit('mic_status', {'active': audio_active})

    def _process_error_message(self, client, userdata, message):
        error_message = message.payload.decode()

    def start_check_in(self):
        if self.check_in_status != True:
            self.logger.info("Sending check-in start command")
            self.publish("start_check_in", "1")

    def publish_UI_status(self, status, message="", details=None):
        payload = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish("UI_status", json.dumps(payload))
