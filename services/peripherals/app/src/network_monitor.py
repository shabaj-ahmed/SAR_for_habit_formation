import speedtest
import subprocess
import os

class NetworkMonitor:
    def __init__(self, event_dispatcher):
        self.servers = []
        self.threads = None
        self.speed_test = speedtest.Speedtest()
        self.dispatcher = event_dispatcher
        self.network_name = str(os.getenv("NETWORK_NAME"))
    
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
        try:
            ps = subprocess.Popen(['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
            if self.network_name in str(output):
                print(f"Connected to the {self.network_name} network")
                self.dispatcher.dispatch_event("send_network_status", "connected")
            else:
                self.dispatcher.dispatch_event("send_network_status", "disconnected")
                print(f"Could not find the {self.network_name} network in the output: {str(output)}")
            pass
        except subprocess.CalledProcessError:
            self.dispatcher.dispatch_event("send_network_status", "disconnected")
            # grep did not match any lines
            print("No wireless networks connected")
