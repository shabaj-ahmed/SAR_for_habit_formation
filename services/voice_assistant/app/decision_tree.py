
from speech_to_text_recognition import SpeedToText
import datetime
import re
import time


class DecisionTree:
    def __init__(self, mqtt_client):
        self.sr = SpeedToText()
        self.mqtt_client = mqtt_client

    def check_in(self):
        # Get the current day and determine the initial question based on that
        initial_question = self.get_current_day_questions()

        # Start asking questions in a loop based on the day
        self.ask_question(
            initial_question["question"],
            initial_question["expected_format"]
        )
    
    # Function to determine the day and adjust the questions accordingly
    def get_current_day_questions(self):
        # Get the current day of the week
        current_day = datetime.datetime.now().strftime('%A')

        # Assign different initial questions based on the day
        if current_day == "Monday":
            initial_question = {
                "question": "What specific goals do you have for this week?", "expected_format": "open-ended"}
        elif current_day == "Tuseday":
            initial_question = {
                "question": "What would you like to reflect on this week?", "expected_format": "open-ended"}
        elif current_day == "Wednesday":
            initial_question = {
                "question": "What can you improve next week?", "expected_format": "open-ended"}
        elif current_day == "Thursday":
            initial_question = {
                "question": "What strategies worked well for you?", "expected_format": "open-ended"}
        elif current_day == "Friday":
            initial_question = {
                "question": "What is your main goal for today?", "expected_format": "open-ended"}
        elif current_day == "Saturday":
            initial_question = {
                "question": "What have you done to stay on track with you behaviour change goals", "expected_format": "open-ended"}
        elif current_day == "Sunday":
            initial_question = {
                "question": "What strategies helped you this week?", "expected_format": "open-ended"}
        else:
            initial_question = {
                "question": "How would you rate your progress on a scale of 1 to 10?", "expected_format": "open-ended"}

        return initial_question
    
    def extract_number_from(self, response):
        # Use regex to find the first occurrence of a number (integer)
        match = re.search(r'\d+', response)
        if match:
            return int(match.group())
        else:
            return None
        
    def determine_next_question(self, question, response):
        if question == "What specific goals do you have for this week?": # Monday
            return {"question": "What strategies will you use to achieve these goals?", "expected_format": "open-ended"}
        elif question == "What would you like to reflect on this week?": # Tuesday
            return {"question": "What did you learn from your reflections?", "expected_format": "open-ended"}
        elif question == "What can you improve next week?": # Wednesday
            return {"question": "What specific actions will you take to improve?", "expected_format": "open-ended"}
        elif question == "What strategies worked well for you?": # Thursday
            return {"question": "How can you apply these strategies in the future?", "expected_format": "open-ended"}
        elif question == "What is your main goal for today?": # Friday
            return {"question": "What strategies will you use to achieve this goal?", "expected_format": "open-ended"}
        elif question == "What have you done to stay on track with you behaviour change goals": # Saturday
            return {"question": "What will you do differently next week?", "expected_format": "open-ended"}
        elif question == "What strategies helped you this week?": # Sunday
            return {"question": "How can you build on these strategies for next week?", "expected_format": "open-ended"}
        else:
            question == "How would you rate your progress on a scale of 1 to 10?"

        if question == "How would you rate your progress on a scale of 1 to 10?":
            try:
                rating = self.extract_number_from(response)
                if rating < 5:
                    return {"question": "What obstacles kept you from meeting your goals?", "expected_format": "open-ended"}
                elif 5 <= rating <= 7:
                    return {"question": "What can you improve next week?", "expected_format": "open-ended"}
                else:
                    return {"question": "Great! What strategies worked well for you?", "expected_format": "open-ended"}
            except ValueError:
                return {"question": "Please provide a valid number between 1 and 10.", "expected_format": "short"}

        # Branching based on responses for obstacles
        elif question == "What obstacles kept you from meeting your goals?":
            if "time" in response.lower():
                return {"question": "Would allocating more time next week help?", "expected_format": "open-ended"}
            elif "motivation" in response.lower():
                return {"question": "What could help you stay motivated?", "expected_format": "open-ended"}
            else:
                return {"question": "What can you change to improve your progress?", "expected_format": "open-ended"}

        return None
    
    def ask_question(self, question = "", expected_format = "open-ended"):
        print("In ask_question function in DecisionTree class")
        while question:
            print(f"Question: {question}")
            self.mqtt_client.publish_message(
                sender="Robot",
                message_type="question",
                content=question
            )
            time.sleep(1)

            # Publish the question to the speech microservice and get the response
            response = self.sr.recognise_response(expected_format)

            print(f"recognition response: {response}, with expected format: {expected_format}")

            # Determine the next question based on the current response
            next_question = self.determine_next_question(
                question,
                response
            )        

            # If there is no next question, break the loop
            if next_question is None:
                print("All questions answered.")
                break

            # Move to the next question
            question = next_question["question"]
            expected_format = next_question["expected_format"]
    
    # def save_response(question, response, summary=""):
        # Save the response to a database or file