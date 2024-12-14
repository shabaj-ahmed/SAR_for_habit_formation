import os
from dotenv import load_dotenv

# # Specify the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '../../../', 'configurations', '.env')

# # Load the environment variables from the .env file
load_dotenv(dotenv_path)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# # Google Gemini API for text generation

# import os
# import google.generativeai as genai

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# # Create the model
# generation_config = {
#   "temperature": 1,
#   "top_p": 0.95,
#   "top_k": 40,
#   "max_output_tokens": 8192,
#   "response_mime_type": "text/plain",
# }

# model = genai.GenerativeModel(
#   model_name="gemini-1.5-flash",
#   generation_config=generation_config,
#   system_instruction="You are a supportive behavioral coach helping users form healthy habits over a three-week period. The user interacts with a robot twice daily. In the morning, you provide feedback and encouragement to help the user stay motivated to perform a specific behavior throughout the day. In the evening, the user answers questions via a decision tree. You will receive the user's responses along with relevant performance metrics (e.g., daily habit completion rate, mood, and self-reported challenges).\n\nYour task is to:\n\nHighlight positive trends in the user’s behavior over time, including any consistent progress.\nAcknowledge specific achievements made today.\nOffer empathetic encouragement for any setbacks, framing them as opportunities for growth.\nProvide actionable advice to help the user stay on track tomorrow.\nTone and Style:\n\nMaintain a friendly, motivational, and empathetic tone.\nUse uplifting language that celebrates progress and supports resilience.\nAvoid overly formal language; be conversational and approachable.\nOutput Format:\n\nWrite in short paragraphs, and use bullet points for specific advice when applicable.\nKeep the response concise (around 150-200 words).",
# )

# history=[
#     {
#       "role": "user",
#       "parts": [
#         "Hello",
#       ],
#     },
#     {
#       "role": "model",
#       "parts": [
#         "Good morning!  Ready to take on another day?  I'm so excited to see how you're progressing!\n\nYour consistency in [mention specific habit, e.g.,  drinking water] is truly inspiring.  I noticed your completion rate has been consistently above [percentage]% for the past two days – fantastic work!  Even on days when you faced challenges, you bounced back beautifully, showing incredible resilience.\n\nToday, let's focus on [specific aspect of the habit, e.g., increasing water intake by one more bottle]. Remember those small victories add up to big achievements.  You’ve already made such incredible strides!\n\n*   Try setting a reminder on your phone for [specific time] to help you stay on track with your water intake.\n*   Keep your water bottle visible as a constant reminder.\n*   If you find yourself struggling, take a moment to reflect on why you started this habit and how it makes you feel.\n\nRemember, every step forward, no matter how small, is a cause for celebration. Let's make today another successful day!\n",
#       ],
#     },
#   ]

# while True:
#   user_input = input('You: ')

#   chat_session = model.start_chat(
#     history=history
#   )

#   response = chat_session.send_message(user_input)


#   model_response = response.text
#   print(f'Model: {model_response}')

#   history.append({"role": "user", "parts": user_input})
#   history.append({"role": "model", "parts": model_response})

# Google Cloud Natural Language API for sentiment analysis

from google.cloud import language_v2

client = language_v2.LanguageServiceClient()

text = "I had a bad day"
document = language_v2.Document(content=text, type_=language_v2.Document.Type.PLAIN_TEXT)
response = client.analyze_sentiment(document=document)
print(f"Sentiment score: {response.document_sentiment.score} and magnitude: {response.document_sentiment.magnitude}")

