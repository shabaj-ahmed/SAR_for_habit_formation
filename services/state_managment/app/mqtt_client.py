import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, broker_address, port):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(broker_address, port, keepalive=60)
        self.mqtt_client.loop_start()

        self.inputs = {
            'switch_state': None,
            'check_in': None,
            'error': None
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

        self.mqtt_client.subscribe("robot/check_in")
        self.mqtt_client.message_callback_add(
            "robot/check_in", self.process_check_in)

        self.mqtt_client.subscribe("robot/error")
        self.mqtt_client.message_callback_add(
            "robot/error", self.process_error_message)

    def process_switch_state(self, client, userdata, message):
        print("Processing switch state")
        self.inputs['switch_state'] = message.payload.decode()

    def process_check_in(self, client, userdata, message):
        print("Processing check in")
        print("Check in message received")
        if message.payload.decode() == '1':
            self.inputs['check_in'] = True
        else:
            self.inputs['check_in'] = False

    def process_error_message(self, client, userdata, message):
        print("Processing error message")
        self.inputs['error'] = message.payload.decode()

    def get_inputs(self):
        return self.inputs

    def disconnect(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
