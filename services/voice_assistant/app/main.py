# # from mqtt_client import MQTTClient
# from voice_assistant import VoiceAssistant
# import os

# # # Get the broker address from environment variables
# # broker_address = os.environ.get('BROKER_ADDRESS')


# # mqtt_client = MQTTClient(broker_address=broker_address, port=1883)
# # # mqtt_client.subscribe_to_topic("voice_assistant/instructions", on_message)


# voice_assistant = VoiceAssistant()
# voice_assistant.run()

import os
import azure.cognitiveservices.speech as speechsdk

speech_key = "b5bcea72d7bf4fe9b2c041e3e7c53dba"
service_region = "uksouth"


def recognize_from_microphone():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(
            speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(
                cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")


recognize_from_microphone()
