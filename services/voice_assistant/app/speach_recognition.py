from datetime import time
from dotenv import load_dotenv
from pathlib import Path
import os
import azure.cognitiveservices.speech as speechsdk
import time

# Relative path to the .env file in the config directory
# Move up one level and into config
dotenv_path = Path('../../configurations/.env')

# Load the .env file
load_dotenv(dotenv_path=dotenv_path)

# Load API keys from environment variables
speech_key = os.getenv('SPEECH_KEY')
service_region = os.getenv('SPEECH_REGION')


def recognise_short_response():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region)
    # speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recogniser = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recogniser.recognise_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognised: {speech_recognition_result.text}")
        return speech_recognition_result.text.strip()
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print(
            f"No speech could be recognised: {speech_recognition_result.no_match_details}")
        return None
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
        return None


def speech_recognise_continuous_async_from_microphone():
    """performs continuous speech recognition asynchronously with input from microphone"""
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region)

    # Set end silence timeout (e.g., 2 seconds of silence)
    # speech_config.set_property_by_name("SPEECH_SILENCE_TIMEOUT_MS", "2000")

    # The default language is "en-us".
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recogniser = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config)

    first_response_received = False
    done = False
    all_results = []
    silence_start_time = None
    initial_silence_timeout = 10
    within_response_timeout = 3

    def recognising_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        # print('RECOGNISING: {}'.format(evt))
        # all_results.append(evt.result.text)
        nonlocal silence_start_time
        # Reset silence start time when recognising speech
        nonlocal first_response_received
        first_response_received = True
        silence_start_time = time.time()

    def recognised_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        # print('recogniseD: {}'.format(evt))
        all_results.append(evt.result.text)
        nonlocal silence_start_time
        # Reset silence start time when recognising speech
        silence_start_time = time.time()

    def stop_cb(evt: speechsdk.SessionEventArgs):
        """callback that signals to stop continuous recognition"""
        # print('CLOSING on {}'.format(evt))

    # Connect callbacks to the events fired by the speech recogniser
    speech_recogniser.recognizing.connect(recognising_cb)
    speech_recogniser.recognized.connect(recognised_cb)
    speech_recogniser.session_stopped.connect(stop_cb)
    speech_recogniser.canceled.connect(stop_cb)

    # Perform recognition. `start_continuous_recognition_async asynchronously initiates continuous recognition operation,
    # Other tasks can be performed on this thread while recognition starts...
    # wait on result_future.get() to know when initialization is done.
    # Call stop_continuous_recognition_async() to stop recognition.
    speech_recogniser.start_continuous_recognition()

    # Initialize silence tracking
    silence_start_time = time.time()

    while not done:
        current_time = time.time()

        if not first_response_received:
            # Check for initial silence timeout
            if current_time - silence_start_time > initial_silence_timeout:
                print(
                    f"Initial silence timeout reached. No speech detected in the past {initial_silence_timeout} seconds.")
                break
        else:
            # Check for end silence timeout
            if current_time - silence_start_time > within_response_timeout:
                print(
                    f"End silence timeout of {within_response_timeout} seconds reached. Stopping recognition.")
                break

    speech_recogniser.stop_continuous_recognition()

    return ' '.join(all_results)


def recognise_response(response_type):
    if response_type == "short":
        return recognise_short_response()
    elif response_type == "open-ended":
        return speech_recognise_continuous_async_from_microphone()
    else:
        print("Invalid response type. Please specify either 'short' or 'open-ended'.")
        return None
