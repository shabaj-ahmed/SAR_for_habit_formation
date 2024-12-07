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
dotenv_path = Path('../../../configurations/.env')

# Load the .env file
load_dotenv(dotenv_path=dotenv_path)

# import json
import io
import anki_vector
# from PIL import Image
# import paho.mqtt.client as mqtt

MAX_RETRIES = 3
RETRY_DELAY = 1

class VectorRobotController:
    def __init__(self):
        self.robot_serial = str(os.getenv("SDK_CONFIGURATION"))
        self.robot_enabled = str(os.getenv("ROBOT_ENABLED")) == 'True'
        print(f"Robot enabled: {self.robot_enabled}")
        self.connected = False
        self.connect()
        
    def connect(self):
        """Connects to the Vector robot."""
        try:
            if self.robot_enabled:
                self.robot = anki_vector.Robot(self.robot_serial)
                self.robot.connect()
                self.connected = True
        except anki_vector.exceptions.VectorConnectionException as e:
            self.connected = False
            raise e

    def disconnect_robot(self):
        """Disconnects from the Vector robot."""
        if self.robot:
            self.robot.disconnect()

    # TODO: reconnect to robot if the function has no response withing a given time limit...
    def reconnect_on_fail(func):
        '''
        Decorator to reconnect to the robot if the connection is lost.
        '''
        def wrapper(self, *args, **kwargs):
            retries = 0
            while retries < MAX_RETRIES:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    self.connected = False
                    self.connect()
                    if self.connected:
                        retries += 1
                        time.sleep(RETRY_DELAY)
                        continue  # exit the loop
                    else:
                        # If unable to reconnect, raise the exception
                        raise e
            return None  # Or raise another custom exception if necessary
        return wrapper
    
    def run_if_robot_is_enabled(func):
        def wrapper(self, *args, **kwargs):
            if self.robot_enabled:
                return func(self, *args, **kwargs)
            return None  # Or raise another custom exception if necessary
        return wrapper
    
    @run_if_robot_is_enabled
    @reconnect_on_fail
    def drive_off_charger(self):
        # self.robot.connection.request_control()
        self.robot.behavior.drive_off_charger()

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def find_face(self):
        # Ask user where are they
        self.robot.behavior.say_text("where are you")
        self.robot.behavior.find_faces()
        # Let the user know you see them
        # self.robot.behavior.turn_towards_face()

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def disengage_user(self):
        self.robot.behavior.drive_on_charger()

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def say_text(self, text):
        self.robot.behavior.say_text(text)

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def list_animations(self):
        """Returns a list of all available animations on the robot."""
        return self.robot.anim.anim_list

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def play_animation(self, animation_name):
        """Plays a specified animation by name."""
        # self.robot.conn.request_control()
        # print(self.robot.conn.requires_behavior_control) # Will print True
        # self.robot.anim.play_animation_trigger('GreetAfterLongTime')
        # self.robot.conn.release_control()
        if animation_name in self.robot.anim.anim_list:
            self.robot.anim.play_animation(animation_name)
        else:
            raise ValueError(f"Animation '{animation_name}' not found.")

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def toggle_autonomous_behavior(self, enable=True):
        self.robot.behavior.enable_all_reactions(enable)

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def set_eye_colour(self, colour):
        colours = {
            "orange": (0.05, 0.95),
            "yellow": (0.11, 1.00),
            "lime": (0.21, 1.00),
            "sapphire": (0.57, 1.00),
            "purple": (0.83, 0.76),
            "green": (0.25, 1.00),
            "red": (0.00, 1.00),    
        }

        selected_colour = colours.get(colour, colours["orange"])

        self.robot.behavior.set_head_angle(degrees(45.0))
        self.robot.behavior.set_lift_height(0.0)
        
        self.robot.behavior.set_eye_color(hue=selected_colour[0], saturation=selected_colour[1])

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def set_volume(self, volume):
        RobotVolumeLevel = {
            "quiet": 0,
            "medium_low": 1,
            "default": 2,
            "medium_high": 3,
            "loud": 4,
        }
        
        self.robot.audio.set_master_volume(RobotVolumeLevel[volume])

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def capture_camera_frame(self):
        """Captures a single image frame from the robot's camera."""
        if self.robot.camera.latest_image:
            return self.robot.camera.latest_image.raw_image
        else:
            raise RuntimeError("Camera feed not available.")        

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def drive(self, forward_speed=50, turn_speed=0):
        """
        Drives the robot with specified forward and turning speeds.
        Positive forward_speed moves forward; negative moves backward.
        turn_speed specifies turning velocity (left or right).
        """
        self.robot.motors.set_wheel_motors(forward_speed, forward_speed + turn_speed)

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def start_video_stream(self):
        self.is_streaming = True
        self.robot.camera.init_camera_feed()

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def stop_video_stream(self):
        self.is_streaming = False
        self.robot.camera.close_camera_feed()

def publish_heartbeat():
    while True:
        # Publish robot controller heartbeat
        logger.info("Robot controller heartbeat")
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

        communication_interface.publish_robot_status("Awake")

        heart_beat_thread = threading.Thread(target=publish_heartbeat, daemon=True)
        heart_beat_thread.start()
        # video_thread = threading.Thread(target=communication_interface.video_stream)
        # video_thread.start()

        while True:
            pass

    except KeyboardInterrupt as e:
        # Stop video streaming
        # controller.stop_video_stream()
        heart_beat_thread.join()
        # video_thread.join()
    except anki_vector.exceptions.VectorConnectionException as e:
        sys.exit("A connection error occurred: %s" % e)
        controller.disconnect_robot()
