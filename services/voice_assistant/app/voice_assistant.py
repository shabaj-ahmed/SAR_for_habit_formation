import subprocess
# Assuming speech_recognition.py is in the same directory
from audio_analyser import AudioAnalysis
# Assuming openai_chatbot.py is in the same directory
from openai_chatbot import OpenAIChatbot
# to speech conversion
import pyttsx3
from gtts import gTTS
import os


class VoiceAssistant:
    def __init__(self):  # , mqtt_client):
        self.speech_recognition = AudioAnalysis()
        self.chatbot = OpenAIChatbot()
        self.tts = pyttsx3.init()
        self.tts.setProperty('voice', 'english+f1')
        # self.mqtt_client = mqtt_client

    def speak(self, text, lang='en'):
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save("temp.mp3")
        if not os.path.exists("temp.mp3"):
            print("Error: MP3 file not created!")
            return
        os.system("mpg321 temp.mp3 -quiet")
        os.remove("temp.mp3")

        # self.mqtt_client.publish_message("voice_assistant/speak", text)
        # print('saying: ', text)
        # self.tts.say(text)
        # self.tts.runAndWait()

    def chat_with_bot(self, message):
        try:
            chat_message = self.chatbot.chat(message)
            self.speak(chat_message)
            print(f"Bot: {chat_message}")
        except Exception as e:
            print(f"Error occurred: {e}")

    def run(self):
        self.speak("Hello")
        while True:
            heard = self.speech_recognition.listen()
            if heard == 'waking up':
                with self.speech_recognition.mic as source:  # Use mic from speech_recognition
                    self.speech_recognition.recognizer.adjust_for_ambient_noise(
                        source)  # Use recognizer from speech_recognition
                    text = self.speech_recognition.listen_and_recognize(source)
                if text.lower() == "quit":
                    break
                if text:
                    confirmation = input(
                        "Press [Enter] to confirm the speech, or type 'cancel' to cancel: ").strip().lower()
                    if confirmation == '':
                        print("Processing your request please wait...")
                        self.chat_with_bot(text)
                    elif confirmation == 'cancel':  # ASCII for backspace
                        print("Cancelled. Please speak again.")
                    else:
                        print("Invalid input. Please speak again.")
            elif heard == 'emergency':
                print(f"Emergency detected! \n")
                self.speak("Do you need help?")
            elif heard == 'call tom':
                print(f"Calling Tom \n")
                self.speak("Calling Tom")
