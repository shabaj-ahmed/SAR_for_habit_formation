import speedtest
import subprocess

class NetworkMonitor:
    def __init__(self, event_dispatcher):
        self.servers = []
        self.threads = None
        self.speed_test = speedtest.Speedtest()
        self.dispatcher = event_dispatcher
        self._register_event_handlers()

    def _register_event_handlers(self):
        if self.dispatcher:
            self.dispatcher.register_event("check_network_status", self.check_internet_connection)
            self.dispatcher.register_event("check_network_speed", self.check_internet_speed)
    
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
        self.dispatcher.dispatch_event("send_network_speed", results)
    
    def check_internet_connection(self):
        ps = subprocess.Popen(['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
            if 'TP-Link_A5BE' in str(output):
                print("Connected to the TP-Link_A5BE network")
                self.dispatcher.dispatch_event("send_network_status", "connected")
            print(f"Could not find the TP-Link_A5BE network in the output: {str(output)}")
        except subprocess.CalledProcessError:
            # grep did not match any lines
            print("No wireless networks connected")