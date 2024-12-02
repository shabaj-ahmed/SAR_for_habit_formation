from src.communication_interface import CommunicationInterface
from custom_logging.logging_config import setup_logger
import time
import threading
import traceback
import sys
from dotenv import load_dotenv
from pathlib import Path
import os

import anki_vector
from anki_vector import util
from anki_vector import annotate
from anki_vector.util import degrees

import logging

# Relative path to the .env file in the config directory
# Move up one level and into config
dotenv_path = Path('../../configurations/.env')

# Load the .env file
load_dotenv(dotenv_path=dotenv_path)

# import json
import io
import anki_vector
# from PIL import Image
# import paho.mqtt.client as mqtt

class VectorRobotController:
    def __init__(self):
        self.robot_serial = str(os.getenv("SDK_CONFIGURATION"))
        
        """Connects to the Vector robot."""
        self.robot = anki_vector.Robot(self.robot_serial)
        self.robot.connect()
        self.is_streaming = False
        self.stop_video_stream() # Ensure video stream is stopped

    def disconnect_robot(self):
        """Disconnects from the Vector robot."""
        if self.robot:
            self.robot.disconnect()

    def engage_user(self):
        self.robot.behavior.drive_off_charger()
        self.robot.behavior.find_faces()
        # self.robot.behavior.turn_towards_face()

    def disengage_user(self):
        self.robot.behavior.drive_on_charger()

    def say_text(self, text):
        self.robot.behavior.say_text(text)

    def list_animations(self):
        """Returns a list of all available animations on the robot."""
        return self.robot.anim.anim_list

    def play_animation(self, animation_name):
        """Plays a specified animation by name."""
        if animation_name in self.robot.anim.anim_list:
            self.robot.anim.play_animation(animation_name)
        else:
            raise ValueError(f"Animation '{animation_name}' not found.")

    def toggle_autonomous_behavior(self, enable=True):
        self.robot.behavior.enable_all_reactions(enable)

    def set_eye_colour(self, hue, saturation):
        self.robot.behavior.set_head_angle(degrees(45.0))
        self.robot.behavior.set_lift_height(0.0)
        self.robot.behavior.set_eye_color(hue, saturation)
    
    def set_volume(self, volume):
        self.robot.audio.set_master_volume(volume)

    def capture_camera_frame(self):
        """Captures a single image frame from the robot's camera."""
        if self.robot.camera.latest_image:
            return self.robot.camera.latest_image.raw_image
        else:
            raise RuntimeError("Camera feed not available.")

    def return_to_charger(self):
        self.robot.behavior.drive_on_charger()

    def drive(self, forward_speed=50, turn_speed=0):
        """
        Drives the robot with specified forward and turning speeds.
        Positive forward_speed moves forward; negative moves backward.
        turn_speed specifies turning velocity (left or right).
        """
        self.robot.motors.set_wheel_motors(forward_speed, forward_speed + turn_speed)

    def start_video_stream(self):
        self.is_streaming = True
        self.robot.camera.init_camera_feed()

    def stop_video_stream(self):
        self.is_streaming = False
        self.robot.camera.close_camera_feed()

def publish_heartbeat():
    while True:
        # Publish voice assistant heartbeat
        logger.info("voice assistant heartbeat")
        time.sleep(30)  # Publish heartbeat every 30 seconds

if __name__ == '__main__':
    try:
        setup_logger()

        logger = logging.getLogger("Main")

        controller = VectorRobotController()
        
        communication_interface = CommunicationInterface(
            broker_address=str(os.getenv("MQTT_BROKER_ADDRESS")),
            port=int(os.getenv("MQTT_BROKER_PORT")),
            robot_controller=controller
        )

        heart_beat_thread = threading.Thread(target=publish_heartbeat, daemon=True)
        heart_beat_thread.start()
        video_thread = threading.Thread(target=communication_interface.video_stream)
        video_thread.start()

        while True:
            pass

    except KeyboardInterrupt as e:
        # Stop video streaming
        controller.stop_video_stream()
        heart_beat_thread.join()
        video_thread.join()
    except anki_vector.exceptions.VectorConnectionException as e:
        sys.exit("A connection error occurred: %s" % e)
    finally:
        controller.disconnect_robot()

