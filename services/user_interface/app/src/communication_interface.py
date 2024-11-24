import json
import sys
import os

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from shared_libraries.mqtt_client_base import MQTTClientBase

from PyQt6.QtCore import pyqtSignal, QObject
import logging


class CommunicationInterface(QObject):
    switch_state_signal = pyqtSignal(str)
    wake_word_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    audio_signal = pyqtSignal(bool)
    camera_signal = pyqtSignal(bool)
    message_signal = pyqtSignal(dict)

    def __init__(self, broker_address, port):
        # Initialize QObject explicitly (no arguments are required for QObject)
        QObject.__init__(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.mqtt_client = MQTTClientBase(broker_address, port)

        self.inputs = {
            'switch_state': False,
            'error': False,
            'audioActive': False,
            'cameraActive': False,
            'wifiActive': False,
        }
        self.subscribe_to_topics()

    def subscribe_to_topics(self):
        self.mqtt_client.subscribe("robot/switch_state", self._process_switch_state)

        self.mqtt_client.subscribe("robot/error", self._process_error_message)

        self.mqtt_client.subscribe("robot/audioActive", self._process_audio_active)

        self.mqtt_client.subscribe("robot/cameraActive", self._process_camera_active)
        
        self.mqtt_client.subscribe("conversation/history", self._on_message)

    # Use QMetaObject.invokeMethod to ensure signal emission in the main thread
    def _process_switch_state(self, client, userdata, message):
        switch_state = message.payload.decode()
        self.switch_state_signal.emit(switch_state)

    def _process_error_message(self, client, userdata, message):
        error_message = message.payload.decode()
        self.error_signal.emit(error_message)

    def _process_audio_active(self, client, userdata, message):
        audio_active = message.payload.decode() == '1'
        self.audio_signal.emit(audio_active)

    def _process_camera_active(self, client, userdata, message):
        camera_active = message.payload.decode() == '1'
        self.camera_signal.emit(camera_active)

    def _on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            self.logger.info(f"Message received on 'conversation/history, payload: {payload}")
            self.message_signal.emit(payload)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON payload: {e}")

    # These methods will be called safely from the main thread
    def emit_switch_state_signal(self, switch_state):
        self.switch_state_signal.emit(switch_state)

    def emit_error_signal(self, error_message):
        self.error_signal.emit(error_message)

    def emit_audio_signal(self, audio_active):
        self.audio_signal.emit(audio_active)

    def emit_camera_signal(self, camera_active):
        self.camera_signal.emit(camera_active)

    def get_inputs(self):
        return self.inputs

    def start_check_in(self):
        self.mqtt_client.publish("user/check_in", "1")