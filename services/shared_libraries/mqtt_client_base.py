import paho.mqtt.client as mqtt


class MQTTClientBase:
    def __init__(self, broker_address, port, client_id=None):
        self.mqtt_client = mqtt.Client(client_id=client_id)

        try:
            self.mqtt_client.connect(broker_address, port, keepalive=60)
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.loop_start()
            self.mqtt_client.on_disconnect = self.on_disconnect
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")

        # Default state, can be extended in child classes
        self.state = {}

    def on_connect(self, client, userdata, flags, rc):
        try:
            if rc == 0:
                print("Connected to broker")
            else:
                print(f"Failed to connect to broker, return code {rc}")
        except Exception as e:
            print(f"Exception in on_connect: {e}")

    def on_message(self, client, userdata, message):
        """Default on_message handler."""
        print(
            f"Received message '{message.payload.decode()}' on topic '{message.topic}'"
        )

    def subscribe(self, topic, callback=None):
        """Subscribe to a topic and optionally add a callback."""
        self.mqtt_client.subscribe(topic)
        if callback:
            self.mqtt_client.message_callback_add(topic, callback)

    def publish(self, topic, message):
        """Publish a message to a topic."""
        self.mqtt_client.publish(topic, message)

    def disconnect(self):
        """Disconnect the MQTT client."""
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
    
    def on_disconnect(self, client, userdata, rc):
        print(f"Disconnected with return code {rc}")
        if rc != 0:
            print("Unexpected disconnection. Attempting to reconnect...")
            try:
                client.reconnect()
            except Exception as e:
                print(f"Reconnection failed: {e}")

