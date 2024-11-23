from speech_to_text_recognition import SpeedToText
import json
import datetime
import re
import time


class DecisionTree:
    def __init__(self):
        self.sr = SpeedToText()
        self.communication_interface = None

    def check_in(self):
        if not self.communication_interface:
            print("Communication interface is not set!")
            return
        print("Communication interface is set and ready to use.")

        # Get the current day and determine the initial question based on that
        initial_question = self.get_current_day_questions()

        # Start asking questions in a loop based on the day
        self.ask_question(
            initial_question["question"],
            initial_question["expected_format"]
        )


    # Function to determine the day and adjust the questions accordingly
    def get_current_day_questions(self):
        """
        Determine the initial question based on the current day of the week.

        Returns:
            dict: A dictionary containing the question and expected response format.
        """

        QUESTION_MAP = {
            "Monday": "What specific goals do you have for this week?",
            "Tuesday": "What would you like to reflect on this week?",
            "Wednesday": "What can you improve next week?",
            "Thursday": "What strategies worked well for you?",
            "Friday": "What is your main goal for today?",
            "Saturday": "What have you done to stay on track with your behavior change goals?",
            "Sunday": "What strategies helped you this week?",
        }

        # Get the current day of the week
        current_day = datetime.datetime.now().strftime('%A')

        # Assign different initial questions based on the day
        question = QUESTION_MAP.get(
            current_day,
            "How would you rate your progress on a scale of 1 to 10?"
        )
        return {"question": question, "expected_format": "open-ended"}

    def extract_number_from(self, response):
        if not isinstance(response, str):
            print(f"Invalid response type: {type(response)}. Expected string.")
            return None
        # Use regex to find the first occurrence of a number (integer)
        match = re.search(r'\d+', response)
        if match:
            return int(match.group())
        else:
            return None

    def determine_next_question(self, question, response, expected_format):
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
            if question == "How would you rate your progress on a scale of 1 to 10?":
                try:
                    rating = self.extract_number_from(response)
                    if rating is None:
                        # Handle the case where no valid number was found
                        return {"question": "Please provide a valid number between 1 and 10.", "expected_format": "short"}
                    elif rating < 5:
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
            elif question == "How would you rate your progress on a scale of 1 to 10?":
                return None
            else:
                return {"question": "How would you rate your progress on a scale of 1 to 10?", "expected_format": "short"}

    def ask_question(self, question = "", expected_format = "open-ended"):
        while question:
            self.communication_interface.publish_message(
                sender = "Robot",
                message_type = "question",
                content = question
            )
            time.sleep(2)

            response = self._get_response(expected_format)

            self.communication_interface.publish_message(
                sender = "User",
                message_type = "Response",
                content = response
            )

            # Determine the next question based on the current response
            next_question = self.determine_next_question(
                question,
                response,
                expected_format
            )        

            # If there is no next question, break the loop
            if next_question is None:
                break

            # Move to the next question
            question = next_question["question"]
            expected_format = next_question["expected_format"]
    
    def _get_response(self, expected_format):
        response = self.sr.recognise_response(expected_format)
        if not isinstance(response, str) or not response.strip():
            self.communication_interface.publish_status(
                "error", "No valid response received."
            )
            return ""
        return response

    # def save_response(question, response, summary=""):
        # Save the response to a database or file
