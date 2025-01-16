import anki_vector
from anki_vector import audio
from anki_vector.util import degrees
import logging
import os
import random

import threading
import time
import logging
from functools import wraps

TIMEOUT_WARNING = 5  # Seconds to issue a warning
RETRY_DELAY = 3

class VectorRobotController:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.communication_interface = None

        self.robot_serial = str(os.getenv("SDK_CONFIGURATION"))
        self.robot_enabled = str(os.getenv("ROBOT_ENABLED")) == 'True'
        self.logger.info(f"Robot enabled: {self.robot_enabled}")
        self.connected = False
        self.robot_awake = True
        self.prevent_robot_timeout = True
        self.error = None
        self.max_retries = 1
        self.timeout = 8
        self.robot_states = {}

    def reconnect_on_fail(func):
        '''
            Run robot control function. If the function hangs, force a reconnect.
        '''
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            attempt_counter = 0

            while attempt_counter < self.max_retries:
                thread = None
                result = None
                func_executed = threading.Event()  # Flag to track if `func()` completed
                exception_raised = None
                
                def issue_warning():
                    self.logger.warning(f"{func.__name__} is taking too long. Please wait or check the robot.")
                
                warning_timer = threading.Timer(TIMEOUT_WARNING, issue_warning)
                warning_timer.start()

                def run_function():
                    nonlocal result, exception_raised
                    try:
                        result = func(self, *args, **kwargs)
                        func_executed.set()  # Mark function as completed
                    except Exception as e:
                        self.logger.error(f"Exception in {func.__name__}: {e}")
                        exception_raised = e

                thread = threading.Thread(target=run_function, daemon=True)
                thread.start()

                # Wait for the function to complete or timeout
                self.logger.info(f"Waiting for {func.__name__} to complete or timeout...")
                thread.join(self.timeout)
                
                if func_executed.is_set():
                    # Function completed successfully
                    self.logger.info("function executed sucessfully")
                    warning_timer.cancel()
                    return result
                else:
                    self.logger.warning(f"{func.__name__} did not complete in time ({self.timeout} timeout).")
                    # if self.connected:
                    #     self.connected = False
                    #     try:
                    #         self.communication_interface.publish_service_error({"message": "Connection to robot lost.\nAttempting to reconnect", "response": "reconnect"})
                    #         self.disconnect_robot()
                    #     except Exception as e:
                    #         self.logger.debug(f"Attempted to disconnect but recived an error: {e}")
                    #         retries += 1
                    #         # If there is an error during disconnect assume the robot is not connected
                    
                    self.logger.info(f"Attempt {attempt_counter} of {self.max_retries}")
                    self.logger.warning(f"{func.__name__} took too long. Forcing a reconnect...")
                    
                    try:
                        self.logger.warning(f"{func.__name__} is being directly invoked to avoid recursion.")
                        self._direct_connect()  # Direct method for `connect` logic
                        if func.__name__ == "connect":
                            return True  # If _direct_connect() succeeds and connect is the parent function then connection to robot is successful so no retry necessary
                    except Exception as e: 
                        self.logger.error(f"The followng error occurred in robot controller: {e}")
                        attempt_counter += 1
                        time.sleep(RETRY_DELAY)
            
            self.communication_interface.publish_error_message({
                "error_message": "Connection to robot lost.\nEnsure the robot and router are turned on.", 
                "response": "reconnect",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })  
            self.communication_interface.publish_robot_connection_status("disconnected")
            # Exhausted retries
            self.logger.error(f"Failed to execute {func.__name__} after {self.max_retries} retries.")
            return False

        return wrapper
    
    def run_if_robot_is_enabled(func):
        def wrapper(self, *args, **kwargs):
            if self.robot_enabled:
                return func(self, *args, **kwargs)
            else:
                self.connected = True
            return True  # Or raise another custom exception if necessary
        return wrapper
    
    @run_if_robot_is_enabled
    @reconnect_on_fail
    def connect(self):
        """Wrapper for connection logic."""
        self.timeout = 15
        self.max_retries = 10
        self._direct_connect()
    
    def _direct_connect(self):
        """Direct connection logic without decorator."""
        self.robot = anki_vector.Robot(self.robot_serial)
        self.robot.connect()
        self.connected = True
        self.logger.info("Connected successfully!")
        self.communication_interface.publish_robot_connection_status("connected")

        # Ensure the customisations are applied
        for state_name, state_value in self.robot_states:
            self.update_service_state({"state_name": state_name, "state_value": state_value})

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def check_connection(self):
        battery_state = self.robot.get_battery_state()
        if not self.connected:
            self.logger.info(f"Failed to connect to the robot after multiple attempts. Ended with error {self.error}")
            self.robot_awake = True
            self.communication_interface.publish_robot_connection_status("disconnected")
            return False
        self.communication_interface.publish_robot_connection_status("connected")
        self.logger.info("Battery checked and robot is, Connected successfully!")
        print("Robot is on charger platform: {0}".format(battery_state.is_on_charger_platform))
        if self.prevent_robot_timeout:
            # If a robot has recently received a command, then prevent it from going to sleep
            self.prevent_robot_timeout = False
            return True
        if battery_state.is_on_charger_platform and self.robot_awake:
            # If the robot is connected and on the docking station, then put it to sleep.
            self.robot.anim.play_animation("anim_chargerdocking_severergetout_01")
            # self.robot.behavior.set_head_angle(degrees(-20.0))
            self.robot_awake = False
        return True
            
    def disconnect_robot(self):
        """Disconnects from the Vector robot."""
        if self.robot:
            self.robot.disconnect()
        
    def handle_control_command(self, command):
        '''
        handels the control commands received from the state machine.

        Args:
            command (str): The control command to handle.
        '''
        self.prevent_robot_timeout = True
        self.logger.info(f"Handling control command: {command}")
        if self.connected:
            status = "complete"
            try:
                if command == "set_up":
                    # self.drive_off_charger()
                    pass
                elif command == "start":
                    # self.handle_tts_command("Starting check-in")
                    pass
                elif command == "end":
                    pass
                elif command == "look_up":
                    self.look_up()
                    self.logger.info("Look up command has been fulfilled..")
                elif command == "follow_face":
                    self.follow_face()
                    self.logger.debug("Follow face command has been fulfilled..")
                elif command == "drive off charger":
                    self.logger.debug("Processing drive off charger request")
                    self.drive_off_charger()
                    self.logger.info("Drive off charger request has been fulfilled..")
                elif command == "return_home":
                    self.logger.debug("Processing return home request")
                    self.drive_on_charger()
                elif command == "backchannel":
                    self.logger.debug("generating a back channel request...")
                    self.generate_backchannel_animation()
                elif command == "reminder":
                    self.logger.debug("generate reminder animation")
                    self.generate_reminder_animation()
                elif command == "wake_up":
                    self.look_up()
            except Exception as e:
                self.logger.error(f"Error processing control command: {e}")
                status = "failed"
                return RuntimeError(f"Failed to execute control command")
        else:
            status = "failed"
        
        # Send acknowledgement to the state machine that the command has been processed
        response = {
                    "behaviour_name": command,
                    "status": status, # "complete" or "failed"
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
        self.communication_interface.update_behaviour_status(response)
    
    @run_if_robot_is_enabled
    @reconnect_on_fail
    def drive_off_charger(self):
        self.robot.behavior.drive_off_charger()
        return True

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def drive_on_charger(self):
        self.robot.behavior.drive_on_charger()
        return True

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def follow_face(self):
        # This takes too long to find a face and ends up blocking the rest of the code so it has been disabled...
        # self.robot.behavior.find_faces()
        pass
        return True

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def enable_free_play(self, enable=True):
        if enable:
            self.robot.conn.release_control()
        else:
            self.robot.conn.request_control()
        return True

    def handle_tts_command(self, payload):
        status = "complete"
        try: 
            self.logger.info(f"In handel tts command func, text from {payload['sender']} is: {payload['content']}")
            self._tts(payload["content"])
            # Add delay to allow the robot to finish speaking before sending completion status
            delay = len(payload["content"].split()) / 8 # This is an arbitrary delay, it allows time for the robot to complete speaking before sending the completion status
            if payload.get("message_type", "") == "greeting":
                self.generate_greetings_animation()
            elif payload.get("message_type", "") == "farewell":
                self.generate_farewell_animation()
            self.logger.info(f"Delaying for {delay} seconds")
            time.sleep(int(delay))
        except Exception as e:
            self.logger.error(f"Error processing TTS command {e}")
            status = "failed"
            return RuntimeError(f"Failed to execute TTS command after {self.max_retries} retries")
            
        response = {
                    "behaviour_name": payload["message_type"],
                    "status": status, # "complete" or "failed"
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
        self.communication_interface.update_behaviour_status(response)

        return True

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def _tts(self, text):
        self.robot.behavior.say_text(text)
        return True

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
        self.logger.info(f"Setting eye colour to {colour}")
        self.logger.info("Getting robot to look up.")
        self.look_up()
        self.robot.behavior.set_lift_height(0.0)
        self.logger.info("Lifted the robot's lift.")
        self.robot.behavior.set_eye_color(hue=selected_colour[0], saturation=selected_colour[1])
        self.logger.info("Eye colour set successfully.")
        return True
    
    @run_if_robot_is_enabled
    @reconnect_on_fail
    def look_up(self):
        self.robot_awake = True
        self.robot.anim.play_animation("anim_generic_look_up_idle_01")
        self.robot.behavior.set_head_angle(degrees(45.0))
        return True

    def update_service_state(self, payload):
        self.prevent_robot_timeout = True
        state_name = payload.get("state_name", "")
        state = payload.get("state_value", "")
        self.logger.info(f"Robot controller received state update for {state_name}: {state}")
        self.robot_states[state_name] = state
        if self.connected:
            if state_name == "robot_colour":
                self.handle_eye_colour_command(state)
            elif state_name == "robot_volume":
                self.set_volume(state, silent=True)
            elif state_name == "robot_voice":
                self.logger.info(f"Voice command received: {state}")
            elif state_name == "free_play":
                self.logger.info(f"Free play mode {'enabled' if state == 'enable' else 'disabled'}")
                self.enable_free_play(state=="enable")

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def set_volume(self, volume, silent=False):
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

        if not silent:
            self._tts(f"Volume has been set to {volume}")

        return True

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
    def generate_backchannel_animation(self):
        backchannel_animations = ["anim_explorer_idle_02_head_angle_40", "anim_explorer_idle_01_head_angle_40", "anim_eyecontact_right_thought_01_head_angle_40", "anim_eyecontact_right_contact_01_head_angle_40", "anim_eyecontact_left_contact_01_head_angle_40", "anim_eyecontact_getout_01_head_angle_40", "anim_eyecontact_center_thought_01_head_angle_40", "anim_freeplay_reacttoface_sayname_02_head_angle_40", "anim_gazing_lookatsurfaces_getin_left_01_head_angle_40", "anim_generic_look_up_01", "anim_generic_look_up_idle_01", "anim_keepalive_blink_01", "anim_lookinplaceforfaces_keepalive_long_02_head_angle_40", "anim_movement_lookinplaceforfaces_medium_head_angle_40", "anim_movement_lookinplaceforfaces_short_head_angle_40", "anim_movement_reacttoface_01_head_angle_40", "anim_reacttoface_unidentified_02_head_angle_40", "anim_reacttoface_unidentified_03_head_angle_40", "anim_referencing_curious_01_head_angle_40", "anim_referencing_smile_01_head_angle_40", "anim_referencing_squint_01_head_angle_40", "anim_rtmotion_lookup_01"]
        index = random.randint(0,len(backchannel_animations)-1)
        self.robot.anim.play_animation(backchannel_animations[index])

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def generate_greetings_animation(self):
        greetings_animation = ["anim_greeting_goodmorning_01", "anim_greeting_goodmorning_02", "anim_greeting_hello_01", "anim_greeting_hello_02", "anim_handdetection_reaction_02", "anim_greeting_imhome_01", "anim_handdetection_reaction_01", "anim_handdetection_reaction_02", "anim_howold_getout_01", "anim_knowledgegraph_success_01", "anim_meetvictor_sayname02_02", "anim_meetvictor_sayname02_04", "anim_movement_comehere_greeting_01", "anim_movement_comehere_greeting_02", "anim_petting_bliss_getout_02", "anim_qa_motors_lift_down_500ms_01"]
        index = random.randint(0,len(greetings_animation)-1)
        self.robot.anim.play_animation(greetings_animation[index])

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def generate_farewell_animation(self):
        farewell_animation = ["anim_greeting_goodbye_02", "anim_greeting_goodnight_01", "anim_greeting_goodnight_02"]
        index = random.randint(0,len(farewell_animation)-1)
        self.robot.anim.play_animation(farewell_animation[index])

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def generate_reminder_animation(self):
        print("In generate_reminder_annimation, requesting a reminder animation")
        reminder_animations = ["anim_timer_beep_01", "anim_timer_beep_02", "anim_timersup_getin_01"]
        index = random.randint(0,len(reminder_animations))
        if index == len(reminder_animations):
            # If the index is the same as the length of the list then skip the animation, this adds a little randomness to the process
            return
        self.robot.anim.play_animation(reminder_animations[index])

    @run_if_robot_is_enabled
    @reconnect_on_fail
    def generate_feedback_animation(self, sentiment = None):
        self.logger.info(f"In generate_feedback_animation(), generating sentiment with {sentiment} which is of type: {type(sentiment)}")
        happy =  ['anim_blackjack_victorbust_01', 'anim_blackjack_victorbjackwin_01', 'anim_blackjack_victorwin_01', 'anim_dancebeat_getout_01', 'anim_eyecontact_giggle_01', 'anim_eyecontact_giggle_01_head_angle_20', 'anim_eyecontact_giggle_01_head_angle_40', 'anim_eyecontact_smile_01_head_angle_40', 'anim_eyecontact_squint_01_head_angle_40', 'anim_eyepose_bliss', 'anim_eyepose_happy', 'anim_eyepose_joy', 'anim_feedback_goodrobot_02', 'anim_freeplay_reacttoface_identified_01', 'anim_freeplay_reacttoface_identified_02', 'anim_freeplay_reacttoface_sayname_01', 'anim_freeplay_reacttoface_sayname_01_head_angle_20', 'anim_freeplay_reacttoface_sayname_01_head_angle_40', 'anim_freeplay_reacttoface_sayname_03', 'anim_onboarding_reacttoface_happy_01', 'anim_onboarding_reacttoface_happy_01_head_angle_40', 'anim_pounce_success_04', 'anim_eyecolorreact_switch_02', 'anim_volume_stage_05']
        sad = ['anim_blackjack_quit_01', 'anim_chargerdocking_pickup_01', 'anim_chargerdocking_requestgetout_01', 'anim_chargerdocking_rightturn_all', 'anim_chargerdocking_severergetout_02', 'anim_communication_cantdothat_01', 'anim_cubeconnection_connectionfailure_01', 'anim_dancebeat_getout_02', 'anim_driving_upset_loop_02', 'anim_driving_upset_start_01', 'anim_explorer_planning_idle_01', 'anim_eyepose_scared', 'anim_feedback_meanwords_02', 'anim_meetvictor_alreadyknowbob_01', 'anim_onboarding_lookdown_lookaround_loop_01', 'anim_blackjack_swipe_01', 'anim_codelab_getin_01', 'anim_communication_cantdothat_02', 'anim_communication_cantdothat_03', 'anim_communication_pickup_cantdothat_01', 'anim_explorer_planning_getin_02', 'anim_fistbump_fail_01', 'anim_wakeword_groggyeyes_getin_01', 'anim_cubedocking_fail_01', 'anim_cubespinner_anticgamefail_01', 'anim_cubespinner_rtcubemoved_01', 'anim_dancebeat_cantdothat_01', 'anim_driving_upset_loop_01', 'anim_explorer_lookaround_01', 'anim_eyepose_scrutinizing', 'anim_reacttoblock_frustrated_01', 'anim_rtshake_lv1rtonground_01', 'anim_explorer_huh_01_head_angle_40', 'anim_eyepose_startled', 'anim_freeplay_reacttoface_identified_03', 'anim_chargerdocking_leftturn_all', 'anim_explorer_scan_short_02']
        neutral = ['anim_chargerdocking_request1_01', 'anim_chargerdocking_requestwait_01', 'anim_cubedocking_drive_getout_01', 'anim_dancebeat_headliftbody_right_small_01', 'anim_explorer_huh_far_01', 'anim_explorer_planning_getout_02', 'anim_eyecontact_center_thought_01_head_angle_20', 'anim_dancebeat_getin_01', 'anim_dancebeat_headliftbody_back_01', 'anim_dancebeat_headliftbody_left_med_01', 'anim_dancebeat_headliftbody_left_small_01', 'anim_dancebeat_headliftbody_right_large_01', 'anim_dancebeat_headliftbody_right_med_01', 'anim_eyecontact_center_contact_01', 'anim_eyecontact_center_contact_01_head_angle_-20', 'anim_eyecontact_center_contact_01_head_angle_20', 'anim_eyecontact_center_contact_01_head_angle_40', 'anim_dancebeat_headlift_01', 'anim_eyecolorreact_getin_01', 'anim_gazing_lookatvector_reaction_01_head_angle_40']
        celebration = ["anim_holiday_hny_fireworks_01", "anim_holiday_hyn_confetti_01", "anim_keepaway_wingame_01", "anim_keepaway_wingame_02"]
        selected_animation = None
        if sentiment >= 6 or sentiment < 9:
            happy_ahmimantion_index = random.randint(0,len(happy)-1)
            selected_animation = happy[happy_ahmimantion_index]
        elif sentiment < 4:
            sad_animation_index = random.randint(0,len(sad)-1)
            selected_animation = sad[sad_animation_index]
        elif sentiment > 9:
            celebration_animation_index = random.randint(0,len(celebration)-1)
            selected_animation = celebration[celebration_animation_index]
        else:
            neutral_animation_index = random.randint(0,len(neutral)-1)
            selected_animation = neutral[neutral_animation_index]
        self.logger.info(f"The following animation has been selected: {selected_animation}")
        self.robot.anim.play_animation(selected_animation)
    
    def set_time_out(self, command):
        self.max_retries = 1
        if command == "enable_timeout":
            self.timeout = 8
        elif command == "disable_timeout":
            self.timeout = 90 # Usually the robot will throw an error well before this time

        self.logger.info(f"Timeout set to {self.timeout} seconds and max_retries set to {self.max_retries}")

    