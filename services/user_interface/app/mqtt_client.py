import paho.mqtt.client as mqtt
import threading


class MQTTClient:
    def __init__(self, broker_address, port):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(broker_address, port, keepalive=60)
        threading.Thread(target=self.mqtt_client.loop_forever).start()

        self.inputs = {
            'switch_state': None,
            'wake_word': None,
            'error': None,
            'audioActive': None,
            'cameraActive': None,
            'wifiActive': None,
        }
        self.subscribe_to_topics()

    def subscribe_to_topics(self):
        self.mqtt_client.subscribe("robot/switch_state")
        self.mqtt_client.message_callback_add(
            "robot/switch_state", self.process_switch_state)

        self.mqtt_client.subscribe("robot/wake_word")
        self.mqtt_client.message_callback_add(
            "robot/wake_word", self.process_wake_word)

        self.mqtt_client.subscribe("robot/error")
        self.mqtt_client.message_callback_add(
            "robot/error", self.process_error_message)

    def process_switch_state(self, message):
        self.inputs['switch_state'] = message.payload.decode()

    def process_wake_word(self, message):
        self.inputs['wake_word'] = message.payload.decode()

    def process_error_message(self, message):
        self.inputs['error'] = message.payload.decode()

    def get_inputs(self):
        return self.inputs

    def disconnect(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
