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

from services.shared_libraries.mqtt_client_base import MQTTClientBase

class CommunicationInterface(MQTTClientBase):
    def __init__(self, broker_address, port, robot_controller):
        super().__init__(broker_address, port)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.robot_controller = robot_controller
        self.start_command = False
        self.is_streaming = False

        # Topics and configuration
        self.robot_status = "robot_status"
        self.check_in_status_topic = "robot/check_in_status"
        self.robot_volume = "robot_volume"
        self.robot_colour = "robot_colour"
        self.tts_topic = "conversation/history"
        self.animation_topic = "robot/animation"
        self.behavior_topic = "robot/behavior"
        self.activate_camera_topic = "robot/activate_camera"
        self.video_topic = "robot/video_feed"

        # Subscribe to necessary topics
        self.subscribe(self.check_in_status_topic, self._handle_start_command)
        self.subscribe(self.robot_volume, self._handle_volume_command)
        self.subscribe(self.robot_colour, self._handle_colour_command)
        self.subscribe(self.tts_topic, self._handle_tts_command)
        self.subscribe(self.animation_topic, self._handle_animation_command)
        self.subscribe(self.behavior_topic, self._handle_behavior_command)
        self.subscribe(self.activate_camera_topic, self._process_camera_active)
    
    def _handle_start_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            message = payload.get("message", "")
            self.logger.info(f"message = {message}")
            if message == "start" or message == "running":
                self.robot_controller.drive
                # Wake up the robot
                pass
            elif message == "completed" or message == "end":
                # request to go to charger
                pass
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload. Using default retry parameters.")
    
    def _handle_volume_command(self, client, userdata, message):
        try:
            volume = message.payload.decode("utf-8")
            self.logger.info(f"Volume command received: {volume}")
            if volume:
                self.robot_controller.set_volume(volume)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for volume command.")
    
    def _handle_colour_command(self, client, userdata, message):
        selected_colour = message.payload.decode()
        try:
            self.logger.info(f"Colour received: {selected_colour}")
            if selected_colour:
                self.robot_controller.set_eye_colour(selected_colour)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for colour command.")
    
    def _handle_tts_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            sender = payload.get("sender", "")
            text = payload.get("content", "")
            self.logger.info(f"environment variable {text}")
            if sender == "robot":
                self.robot_controller.say_text(text)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for TTS command.")
    
    def _handle_animation_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            animation_name = payload.get("animation", "")
            self.logger.info(f"Animation command received: {animation_name}")
            if animation_name:
                self.robot_controller.play_animation(animation_name)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for animation command.")
    
    def _handle_behavior_command(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            action = payload.get("action", "")
            self.logger.info(f"Behavior command received: {action}")

            if action == "move_forward":
                self.robot_controller.drive(forward_speed=100)
                time.sleep(2)
                self.robot_controller.drive(forward_speed=0)
            elif action == "go_home":
                self.robot_controller.return_to_charger()
            elif action == "toggle_autonomous":
                enable = payload.get("enable", True)
                self.robot_controller.toggle_autonomous_behavior(enable)
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON payload for behavior command.")

    def _process_camera_active(self, client, userdata, message):
        camera_active = message.payload.decode() == '1'
        self.logger.info(f"Camera active: {camera_active}")
        if self.socketio:
            self.logger.info("start displaying camera feed")
            self.robot_controller.start_video_stream()
        else:
            self.robot_controller.stop_video_stream()
    
    def video_stream(self):
        self.logger.info(f"Video stream status = {self.robot_controller.is_streaming}")
        while True:
            if self.robot_controller.is_streaming:
                try:
                    img = self.robot_controller.capture_camera_frame()
                    img_io = io.BytesIO()
                    img.save(img_io, format="JPEG")
                    img_data = img_io.getvalue()
                    self.publish(self.video_topic, img_data)
                    time.sleep(0.2)  # Frame rate of 5 frames per second
                except Exception as e:
                    self.logger.error(f"Error in video streaming: {e}")
                    break
    
    def publish_robot_status(self, status, message="", details=None):
        payload = {
            "status": status,
            "message": message,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.publish(self.robot_status, json.dumps(payload))