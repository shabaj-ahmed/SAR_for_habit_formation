import anki_vector
from anki_vector import audio
from anki_vector.util import degrees
import logging
import os
import time

MAX_RETRIES = 5
RETRY_DELAY = 4

class VectorRobotController:
    def __init__(self, dispatcher=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.dispatcher = dispatcher
        self._register_event_handlers()

        self.robot_serial = str(os.getenv("SDK_CONFIGURATION"))
        self.robot_enabled = str(os.getenv("ROBOT_ENABLED")) == 'True'
        self.logger.info(f"Robot enabled: {self.robot_enabled}")
        self.connected = False
        self.connect()
        
    def connect(self):
        """Connects to the Vector robot."""
        max_retries = MAX_RETRIES
        if self.robot_enabled:
            for attempt in range(max_retries):
                try:
                    self.robot = anki_vector.Robot(self.robot_serial)
                    self.robot.connect()
                    self.connected = True
                    self.logger.info("Connected successfully!")
                    break
                except anki_vector.exceptions.VectorTimeoutException as e:
                    # self.disconnect_robot()
                    self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        self.logger.info("Retrying...")
                    else:
                        self.connected = False
                        raise e
                time.sleep(RETRY_DELAY)

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
    
    def _register_event_handlers(self):
        """Register event handlers for robot actions."""
        if self.dispatcher:
            self.dispatcher.register_event("control_command", self.handle_control_command)
            self.dispatcher.register_event("volume_command", self.set_volume)
            self.dispatcher.register_event("tts_command", self.handle_tts_command)
            self.dispatcher.register_event("eye_colour_command", self.handle_eye_colour_command)

    def handle_control_command(self, command):
        '''
        handels the control commands received from the state machine.

        Args:
            command (str): The control command to handle.
        '''
        self.logger.info(f"Handling control command: {command}")
        if command == "set_up":
            # self.drive_off_charger()
            pass
        elif command == "start":
            # self.handle_tts_command("Starting check-in")
            pass
        elif command == "end":
            # self.disengage_user()
            pass
        elif command == "drive off charger":
            self.logger.debug("Processing drive off charger request")
            self.drive_off_charger()
        elif command == "return home":
            self.logger.debug("Processing drive off charger request")
            self.drive_on_charger()
    
    def run_if_robot_is_enabled(func):
        def wrapper(self, *args, **kwargs):
            if self.robot_enabled:
                return func(self, *args, **kwargs)
            return None  # Or raise another custom exception if necessary
        return wrapper
    
    @run_if_robot_is_enabled
    @reconnect_on_fail
    def drive_off_charger(self):
        self.robot.behavior.drive_off_charger()

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def drive_on_charger(self):
        self.robot.behavior.drive_on_charger()

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
    def handle_tts_command(self, text):
        self.logger.info(f"In handel tts command func, text to be said is: {text}")
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
    def handle_eye_colour_command(self, colour):
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
        '''
        Set the robot's volume level.

        Args:
            volume (str): The volume level to set. One of "quiet", "medium_low", "default", "medium_high", "loud".
        '''
        RobotVolumeLevel = {
            "quiet": audio.RobotVolumeLevel.LOW,
            "medium_low": audio.RobotVolumeLevel.MEDIUM_LOW,
            "default": audio.RobotVolumeLevel.MEDIUM,
            "medium_high": audio.RobotVolumeLevel.MEDIUM_HIGH,
            "loud": audio.RobotVolumeLevel.HIGH,
        }
        
        self.robot.audio.set_master_volume(RobotVolumeLevel[volume])

        self.handle_tts_command(f"Volume has been set to {volume}")

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