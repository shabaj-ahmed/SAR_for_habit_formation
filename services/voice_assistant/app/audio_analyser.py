import speech_recognition as sr
from twilio.rest import Client
import re


class AudioAnalysis:
    WAKE_WORD = "hey max"
    EMERGENCY_WORD = "help"
    CALL = "call tom"

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.client = Client(account_sid, auth_token)

    def listen_and_recognize(self, source):
        try:
            audio = self.recognizer.listen(source)
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError as e:
            print(
                f"Could not request results from Google Speech Recognition service; {e}")
            return ""

    # def listen_for_wake_word(self):
    #     with self.mic as source:
    #         self.recognizer.adjust_for_ambient_noise(source, duration=1)
    #         self.recognizer.energy_threshold = 4000 # Adjusting the threshold to ambient noise
    #         print('Listening for wake word...')
    #         text = self.listen_and_recognize(source)

    #     try:
    #         heard = text.lower() == self.WAKE_WORD
    #     except AttributeError:
    #         heard = False

    #     return heard

    def listen(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.energy_threshold = 4000
            text = self.listen_and_recognize(source)

        try:
            heard = text.lower()
        except AttributeError:
            heard = ''
        print('heard: ', heard)
        if re.search(r'\bhelp\b', heard):
            return 'emergency'
        elif re.search(r'\bhey max\b', heard):
            print('Waking up')
            return 'waking up'
        elif re.search(r'\bcall tom\b', heard):
            message = self.client.messages \
                .create(
                    body="Robotarium hackathon is trying to reach you.",
                    from_='+447380307618',
                    to='+447522697324'
                )

            print(message.sid)
            return 'call tom'

        return None
