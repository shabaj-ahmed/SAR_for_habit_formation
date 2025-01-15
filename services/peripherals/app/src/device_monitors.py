import speedtest
import subprocess

class NetworkMonitor:
    def __init__(self, event_dispatcher):
        self.servers = []
        self.threads = None
        self.speed_test = speedtest.Speedtest()
        self.dispatcher = event_dispatcher
    
    def get_servers(self):
        self.speed_test.get_servers(self.servers)
    
    def get_best_server(self):
        self.speed_test.get_best_server()
    
    def download(self):
        self.speed_test.download(threads=self.threads)
    
    def upload(self):
        self.speed_test.upload(threads=self.threads)
    
    def run_speed_test(self):
        self.get_servers()
        self.get_best_server()
        self.download()
        self.upload()
    
    def get_results(self):
        return self.speed_test.results.dict()
    
    def check_internet_speed(self):
        self.run_speed_test()
        results = self.get_results()
        if results:
            print(f"Download = {results['download']/1000000}Mbps and upload = {results['upload']/1000000}Mbps")
            self.dispatcher.dispatch_event("send_network_speed", results)
    
    def check_internet_connection(self):
        ps = subprocess.Popen(['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
            if 'TP-Link_A58E' in str(output):
                print("Connected to the TP-Link_A58E network")
                self.dispatcher.dispatch_event("send_network_status", "connected")
            else:
                print(f"Could not find the TP-Link_A5BE network in the output: {str(output)}")
        except subprocess.CalledProcessError:
            # grep did not match any lines
            print("No wireless networks connected")

import time

class ScreenMonitor:
    def __init__(self, event_dispatcher):
        self.dispatcher = event_dispatcher
        self.brightness = 50
        self.screen_dim_value = 15 # default to medium brightness if value not yet recived
        self.is_sleep_timer_enabled = False
        self.is_screen_awake = True
        self.countdown = time.time()

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
        # print(f"sleep timer has been configured to: {configuration}")
        self.is_sleep_timer_enabled = configuration
        self._wake_up_screen()

    def _set_screen_brightness(self, brightness):
        self.brightness = brightness

    def _wake_up_screen(self):
        self.countdown = time.time()
        if not self.is_screen_awake:
            self.wake_up()
    
    def put_to_sleep(self):
        self.screen_dim_value = int(self.brightness) if self.screen_dim_value is None else self.screen_dim_value

        # set new brightness
        self.screen_dim_value = self.screen_dim_value - 1

        # make sure the new brightness is not less than 0
        if self.screen_dim_value <= 1:
            self.screen_dim_value = 0
        elif self.screen_dim_value <= 0:
            return
        
        try:
            subprocess.run(
                f'echo {self.screen_dim_value} | sudo tee /sys/class/backlight/4-0045/brightness',
                shell=True,
                check=True
            )
            pass
            # Return a success response
        except subprocess.CalledProcessError as e:
            # Return an error response if the command fails
            return f"send_service_error: {e}"
        
        time.sleep(0.04)

        # print(f"Brightness successfully dimmed")
    
    def wake_up(self):
        # print("Waking up screen")
        self.dispatcher.dispatch_event("send_screen_status", "awake")
        for brightness in range(0, self.brightness):            
            try:
                subprocess.run(
                    f'echo {brightness} | sudo tee /sys/class/backlight/4-0045/brightness',
                    shell=True,
                    check=True
                )
                pass
            except subprocess.CalledProcessError as e:
                # Return an error response if the command fails
                return f"send_service_error: {e}"
            
            time.sleep(0.04)
        self.screen_dim_value = self.brightness
        # print(f"Brightness successfully lit")
            
    def check_for_screen_timeout(self):
        if self.is_sleep_timer_enabled and self.screen_dim_value > 0:
            print("########################### Screen saver started ############################")
            if time.time() - self.countdown > 10:
                self.put_to_sleep()
                self.is_screen_awake = False
    
    def wake_up_screen(self):
        if not self.is_screen_awake:
            print("########################### Screen saver restarted ############################")
            self.wake_up()
            self.is_screen_awake = True
            self._wake_up_screen()