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

class SpeedToText:
    def __init__(self):
        # Load API keys from environment variables
        self.speech_key = os.getenv('SPEECH_KEY')
        self.service_region = os.getenv('SPEECH_REGION')
        self.communication_interface = None

        # Set up the Azure STT configurations once, to avoid reconnecting each time
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key, region=self.service_region)
        
        self.audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

        # Keep a reusable SpeechRecognizer for short responses
        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, audio_config=self.audio_config
        )
    
    def recognise_response(self, response_type):
        if response_type == "short":
            return self.recognise_short_response()
        elif response_type == "open-ended":
            return self.speech_recognise_continuous_async_from_microphone()
        else:
            print("Invalid response type. Please specify either 'short' or 'open-ended'.")
            return None
    
    def recognise_short_response(self):
        print("Speak into your microphone.")
        speech_recognition_result = self.speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"Recognised: {speech_recognition_result.text}")
            return speech_recognition_result.text.strip()
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print(f"No speech could be recognised: {speech_recognition_result.no_match_details}")
            return None
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return None
        
    def speech_recognise_continuous_async_from_microphone(self):
        """performs continuous speech recognition asynchronously with input from microphone"""
        speech_recogniser = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, audio_config=self.audio_config)

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
            self.communication_interface.silance_detected()


        def recognised_cb(evt: speechsdk.SpeechRecognitionEventArgs):
            # print('recogniseD: {}'.format(evt))
            all_results.append(evt.result.text)
            nonlocal silence_start_time
            # Reset silence start time when recognising speech
            silence_start_time = time.time()
            self.communication_interface.silance_detected()


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
        self.communication_interface.silance_detected()

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
