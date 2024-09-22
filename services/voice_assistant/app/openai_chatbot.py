import openai

OPENAI_API_KEY= 

class OpenAIChatbot:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]

    def chat(self, user_message):
        self.messages.append({"role": "user", "content": user_message})
        # self.mqtt_client.publish_message('voice_assistant/user_request', user_message)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        bot_message = response['choices'][0]['message']['content']
        self.messages.append({"role": "assistant", "content": bot_message})
        return bot_message




