import datetime
import time
import logging

'''
Publish the questions to be asked and request reponses from the user
'''

class CheckInScenario:
    def __init__(self, communication_interface):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.communication_interface = communication_interface
        self.step = 0
        self.complete = False

    def start(self):
        self.step = 1
        self.complete = False
        self.waiting_for_response = False
        self.current_question = None
        self.delay_start_time = None
        self.next_question = None
        self.logger.info("Check-in scenario started")
        pass
    
    def update(self):
        self.logger.info(f"Updating orchestrator, currently on step = {self.step}")
        # If we've completed the scenario, do nothing.
        if self.complete:
            return
        
        # Step 1: Set up
        if self.step == 1: 
            if self._drive_off_charger():
                 self.step = 2
        
        # Step 1: Send greeting
        if self.step == 2: 
            if self._greet_user():
                 self.step = 3
                
        # Step 2: Weekday-specific questions
        # if self.step == 3:
        #     if self.waiting_for_response == False:
        #         # check if the user has responded
        #         try:
        #             response = self.communication_interface.get_user_response() #TODO: Delete the response once it has been processed
        #         except Exception as e:
        #             self.logger.error(f"Error asking weekday questions: {e}")
        #         # If the response is invalid, ask the same question again
        #         if response == "":
        #             # Ask the same question again
        #             pass
        #         if response is not None:
        #             self.waiting_for_response = False
        #             self.next_question = self.get_current_day_questions(previous_question=self.current_question, previous_response=response)
        #             if self.next_question is None:
        #                 self.step = 4
        #                 self.current_question = None
        #                 return
        #             self.communication_interface.publish_robot_speech(
        #                 message_type = "question",
        #                 content = self.next_question["question"]
        #             )
        #     else:
        #         # Not currently waiting for a response means we must have just asked a new question
        #         # or finished. If no question was asked yet, ask the first one:
        #         if self.current_question is None:
        #             self.get_current_day_questions()
        
        # elif self.step == 3:
        #     # Step 3: Experience sampling questions
        #     self.step = 4
        #     # Step 3: Experience sampling questions
        #     try:
        #         self._ask_experience_questions()
        #     except Exception as e:
        #         self.logger.error(f"Error asking experience questions: {e}")
        #     return
        
        # # Step 4: Summarise the conversation
        
        # # Step 5: Wish participants farewell
        # if self.step == 4:
        #     self._farewell_user()
        #     self.step = 5
        #     return
        
        # Step 5: Mark as complete
        elif self.step == 4:
            self.complete = True
            self.logger.info("Check-In Scenario Complete")
            self.step = 0
            # Possibly also send completion signals if needed

            return
        
        # Step 6: Save the conversation to a database or file
        
    # Helper methods for each step
    def _drive_off_charger(self):
        # Get robot to drive off the charger and wait for it to complete...
        if self.waiting_for_response == False:
            self.communication_interface.publish_robot_behaviour_command("drive off charger")
            self.waiting_for_response = True
        
        if self.communication_interface.get_robot_behaviour_completion_status("drive off charger") == "complete":
            self.waiting_for_response = False
            self.logger.info("No longer wating, moving to step 2 to greet user")
            return True
        
        return False
    
    def _greet_user(self):
        if self.waiting_for_response == False:
            self.logger.info("Requesting robot to speak")
            self.communication_interface.publish_robot_speech(
                message_type="greeting",
                content="Hello! Welcome to your daily check-in."
            )
            self.waiting_for_response = True
        
        if self.communication_interface.get_robot_behaviour_completion_status("greeting") == "complete":
            self.logger.info("Greetings complete")
            self.waiting_for_response = False
            return True
        
        return False

    # Function to determine the day and adjust the questions accordingly
    def get_current_day_questions(self, question = "", response = ""):
        """
        Determine the initial question based on the current day of the week.

        Returns:
            dict: A dictionary containing the question and expected response format.
        """
        self.logger.info(f"In get_current_day_questions: question = {question}, response = {response}")

        QUESTION_MAP = {
            "Monday": "What specific goals do you have for this week?",
            "Tuesday": "What would you like to reflect on this week?",
            "Wednesday": "What can you improve next week?",
            "Thursday": "What strategies worked well for you?",
            "Friday": "What is your main goal for today?",
            "Saturday": "What have you done to stay on track with your behaviour change goals?",
            "Sunday": "What strategies helped you this week?",
        }

        # Get the current day of the week
        current_day = datetime.datetime.now().strftime('%A')
        self.logger.info(f"Current day: {current_day}")

        if question == "":
            # Assign different initial questions based on the day
            self.logger.info(f"Initial question: {QUESTION_MAP.get(current_day)}")
            question = QUESTION_MAP.get(
                current_day,
                "What specific goals do you have for this week?"
                )
            self.logger.info(f"Initial question: {question}")
        else:
            if question == "What specific goals do you have for this week?": # Monday
                question = "What strategies will you use to achieve these goals?"
            elif question == "What would you like to reflect on this week?": # Tuesday
                question = "What did you learn from your reflections?"
            elif question == "What can you improve next week?": # Wednesday
                question = "What specific actions will you take to improve?"
            elif question == "What strategies worked well for you?": # Thursday
                question = "How can you apply these strategies in the future?"
            elif question == "What is your main goal for today?": # Friday
                question = "What strategies will you use to achieve this goal?"
            elif question == "What have you done to stay on track with your behaviour change goals?": # Saturday
                question = "What will you do differently next week?"
            elif question == "What strategies helped you this week?": # Sunday
                question = "How can you build on these strategies for next week?"
            else:
                self.logger.info(f"No more questions for the week. Returning None.")
                return None
        self.logger.info(f"Returning question: {question}")

        return {"question": question, "expected_format": "open-ended"}

    def experience_sampling_questions(self, question = "", response = ""):
        self.logger.info(f"In experience_sampling_questions: question = {question}, response = {response}")
        if question == "":
            return {"question": "How would you rate your progress on a scale of 1 to 10?", "expected_format": "short"}
        elif question == "How would you rate your progress on a scale of 1 to 10?":
            try:
                if response is None or response == "" or response < 1 or response > 10:
                    # Handle the case where no valid number was found
                    return {"question": "Please provide a valid number between 1 and 10.", "expected_format": "short"}
                elif response < 5:
                    return {"question": "What obstacles kept you from meeting your goals?", "expected_format": "open-ended"}
                elif 5 <= response <= 7:
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
        elif question == "What can you improve next week?":
            return {"question": "What specific actions will you take to improve?", "expected_format": "open-ended"}
        elif question == "Great! What strategies worked well for you?":
            return {"question": "How can you apply these strategies in the future?", "expected_format": "open-ended"}
        else:
            self.logger.info(f"No more questions for experience sampling. Returning None.")
            return None
    
    def _farewell_user(self):
        self.logger.info("Sending farewell.")
        self.communication_interface.publish_robot_speech(
            message_type="farewell",
            content="Thank you for checking in. Have a great day!"
        )
        self.communication_interface.publish_speech_recognition_status("completed")
        self.communication_interface.end_check_in()
        self.logger.info("Voice assistant service completed successfully.")

    # def save_response(question, response, summary=""):
        # Save the response to a database or file

    def is_complete(self):
            return self.complete