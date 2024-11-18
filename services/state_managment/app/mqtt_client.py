import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, broker_address, port):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(broker_address, port, keepalive=60)
        self.mqtt_client.loop_start()

        self.criticalEvents = {
            'switch_state': False,
            'reminder': False,
            'error': False
        }
        self.userEvents = {
            'check_in': False,
            'configurations': False
        }
        self.behaviourCompletionStatus = {
            'reminder': False,
            'check_in': False,
            'configurations': False
        }

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
            self.subscribe_to_topics()
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, message):
        print(
            f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

    def subscribe_to_topics(self):
        print("Subscribing to topics...")
        self.mqtt_client.subscribe("robot/switch_state")
        self.mqtt_client.message_callback_add(
            "robot/switch_state", self.process_switch_state)
        
        self.mqtt_client.subscribe("robot/error")
        self.mqtt_client.message_callback_add(
            "robot/error", self.process_error_message)

        self.mqtt_client.subscribe("user/check_in")
        self.mqtt_client.message_callback_add(
            "user/check_in", self.process_check_in)
        
        self.mqtt_client.subscribe("user/configurations")
        self.mqtt_client.message_callback_add(
            "user/configurations", self.process_configurations
        )

        self.mqtt_client.subscribe("robot/reminder")
        self.mqtt_client.message_callback_add(
            "robot/reminder", self.process_reminder_status
        )

        self.mqtt_client.subscribe("robot/check_in_status")
        self.mqtt_client.message_callback_add(
            "robot/check_in_status", self.process_check_in_status
        )
    
    def publish_fsm_state(self, state):
        self.mqtt_client.publish(f"fsm/state", state)

    def process_switch_state(self, client, userdata, message):
        print("Processing switch state")
        self.criticalEvents['switch_state'] = message.payload.decode()

    def process_error_message(self, client, userdata, message):
        print("Processing error message")
        self.criticalEvents['error'] = message.payload.decode()

    def process_check_in(self, client, userdata, message):
        print("Processing check in")
        print("Check in message received")
        if message.payload.decode() == '1':
            self.userEvents['check_in'] = True
        else:
            self.userEvents['check_in'] = False
            self.userEvents['configurations'] = False

    def process_configurations(self, client, userdata, message):
        print("Processing configurations")
        print("Configurations message received")
        if message.payload.decode() == '1':
            self.userEvents['configurations'] = True
        else:
            self.userEvents['configurations'] = False
            self.userEvents['check_in'] = False

    def process_reminder_status(self, client, userdata, message):
        print("Processing reminder status")
        print("Reminder message received")
        if message.payload.decode() == 'running':
            self.behaviourCompletionStatus['reminder'] = True
        elif message.payload.decode() == 'completed':
            self.behaviourCompletionStatus['reminder'] = False
            self.userEvents['configurations'] = False
            self.userEvents['check_in'] = False
    
    def process_check_in_status(self, client, userdata, message):
        print("Processing check in status")
        print("Check in message received")
        if message.payload.decode() == 'running':
            self.behaviourCompletionStatus['check_in'] = True
        elif message.payload.decode() == 'completed':
            self.behaviourCompletionStatus['check_in'] = False
            self.userEvents['configurations'] = False
            self.userEvents['check_in'] = False

    def get_critical_events(self):
        return self.criticalEvents
    
    def get_user_event(self):
        return self.userEvents
    
    def get_behaviour_completion_status(self):
        return self.behaviourCompletionStatus

    def disconnect(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
