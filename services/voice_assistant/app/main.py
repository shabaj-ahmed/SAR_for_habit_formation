# from mqtt_client import MQTTClient
from voice_assistant import VoiceAssistant
import os

# # Get the broker address from environment variables
# broker_address = os.environ.get('BROKER_ADDRESS')


# mqtt_client = MQTTClient(broker_address=broker_address, port=1883)
# # mqtt_client.subscribe_to_topic("voice_assistant/instructions", on_message)


voice_assistant = VoiceAssistant()
voice_assistant.run()
