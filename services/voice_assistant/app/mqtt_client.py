import paho.mqtt.client as mqtt
import json


class MQTTClient:
    def __init__(self, broker_address, port):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(broker_address, port, keepalive=60)
        self.mqtt_client.loop_start()

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

        self.mqtt_client.subscribe("user/check_in")
        self.mqtt_client.message_callback_add(
            "user/check_in", self.process_check_in)

        self.mqtt_client.subscribe("robot/reminder")
        self.mqtt_client.message_callback_add(
            "robot/reminder", self.process_reminder_status
        )

        self.mqtt_client.subscribe("robot/check_in_status")
        self.mqtt_client.message_callback_add(
            "robot/check_in_status", self.process_check_in_status
        )

    def publish_fsm_state(self, state):
        self.mqtt_client.publish("fsm/state", state)
    
    def publish_check_in_status(self, status):
        self.mqtt_client.publish("user/check_in", "0")
        self.mqtt_client.publish("robot/check_in_status", status)
    
    def publish_message(self, sender, content, message_type="response"):
        message = {
            "sender": sender,
            "type": message_type,
            "content": content
        }
        json_message = json.dumps(message)
        print(f"Publishing message: {json_message}")
        self.mqtt_client.publish("conversation/history", json_message)

    def process_check_in(self, client, userdata, message):
        print("Processing check in")
        print("Check in message received")
        if message.payload.decode() == '1':
            self.userEvents['check_in'] = True
        else:
            self.userEvents['check_in'] = False
            self.userEvents['configurations'] = False

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
    
    def get_user_event(self):
        return self.userEvents
    
    def get_behaviour_completion_status(self):
        return self.behaviourCompletionStatus

    def disconnect(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
