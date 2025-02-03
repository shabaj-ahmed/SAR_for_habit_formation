import subprocess
import time
import os

class ScreenMonitor:
    def __init__(self, event_dispatcher):
        self.dispatcher = event_dispatcher
        self.brightness = 50
        self.screen_dim_value = 15 # default to medium brightness if value not yet recived
        self.is_sleep_timer_enabled = False
        self.is_screen_awake = True
        self.countdown = time.time()
        self.brightness_file = str(os.getenv("BRIGHTNESS_FILE"))
        self.brightness_interval = 1 if int(os.getenv("BRIGHTNESS_VALUE") == 255 else 4

        self.dispatcher.register_event("configure_sleep_timer", self._configure_sleep_timer)
        self.dispatcher.register_event("update_screen_brightness", self._set_screen_brightness)
        self.dispatcher.register_event("wake_up_screen", self._wake_up_screen)
        self.dispatcher.register_event("update_state_variable", self._update_service_state)

    def _update_service_state(self, payload):
        state_name = payload.get("state_name", "")
        state_value = payload.get("state_value", [])
        if state_name == "brightness":
            self.brightness = int(state_value)
            self.screen_dim_value = int(state_value)

    def _configure_sleep_timer(self, payload):
        configuration = payload.get("control", False)
        print(f"sleep timer has been configured to: {configuration}")
        self.is_sleep_timer_enabled = configuration
        self._wake_up_screen()

    def _set_screen_brightness(self, brightness):
        self.brightness = brightness

    def _wake_up_screen(self):
        self.countdown = time.time()
        if not self.is_screen_awake:
            # print("self.is_screen_awake: ", self.is_screen_awake)
            print("########################### Screen saver restarted ############################")
            self.wake_up()
    
    def put_to_sleep(self):
        self.screen_dim_value = int(self.brightness) if self.screen_dim_value is None else self.screen_dim_value

        # set new brightness
        self.screen_dim_value = self.screen_dim_value - self.brightness_interval

        # make sure the new brightness is not less than 0
        if self.screen_dim_value <= 1:
            self.screen_dim_value = 0
        elif self.screen_dim_value <= 0:
            return
        
        try:
            subprocess.run(
                f'echo {self.screen_dim_value} | sudo tee {self.brightness_file}',
                shell=True,
                check=True
            )
            pass
        except subprocess.CalledProcessError as e:
            # Return an error response if the command fails
            return f"send_service_error: {e}"

        # print(f"Brightness successfully dimmed")
    
    def wake_up(self):
        # print("Waking up screen")
        self.dispatcher.dispatch_event("send_screen_status", "awake")
        for brightness in range(self.screen_dim_value, self.brightness, self.brightness_interval):            
            try:
                subprocess.run(
                    f'echo {brightness} | sudo tee {self.brightness_file}',
                    shell=True,
                    check=True
                )
                pass
            except subprocess.CalledProcessError as e:
                # Return an error response if the command fails
                return f"send_service_error: {e}"
            
        self.screen_dim_value = self.brightness
        self.is_screen_awake = True
        # print(f"Brightness successfully lit")
            
    def check_for_screen_timeout(self):
        if self.is_sleep_timer_enabled and self.screen_dim_value > 0:
            # print(f"is sleep timer enabled: {self.is_sleep_timer_enabled} and screen dim value: {self.screen_dim_value} is screen awake: {self.is_screen_awake}")
            if time.time() - self.countdown > 10:
                print("########################### Screen saver started ############################")
                self.put_to_sleep()
                self.is_screen_awake = False
    
    def wake_up_screen(self):
        if not self.is_screen_awake:
            print("########################### Screen saver restarted ############################")
            self.wake_up()
            self.countdown = time.time()
