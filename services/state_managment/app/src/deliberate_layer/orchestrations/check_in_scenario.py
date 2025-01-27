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
        self.ask_questions = CheckInQuestions()

    def start(self):
        self.logger.info("In orchestrator, starting check-in scenario.")
        self.step = 1
        self.complete = False
        self.waiting_for_response = False
        self.backchanneling_timer = None
        self.current_question = None
        self.next_question = None
        self.response = None
        self.ask_questions.set_start_of_study(self.communication_interface.get_first_day())
        self.communication_interface.configure_sleep_timer("Off")
        pass
    
    def update(self):
        # self.logger.info(f"Updating orchestrator, currently on step = {self.step}")
        # If we've completed the scenario, do nothing.
        if self.complete:
            return
        
        # Step 1: Set up
        elif self.step == 1: 
            if self._drive_off_charger():
                 self.step = 2

        # Step 2: Greet the user
        elif self.step == 2:
            if self._greet_user():
                self.step = 3
        
        # # Step 3: Look up
        elif self.step == 3:
            self.communication_interface.publish_robot_behaviour_command("look_up")
            time.sleep(0.4)
            self.step = 4
                
        # # Step 4: Ask questions
        elif self.step == 4:
            if not self.waiting_for_response:
                if self.current_question is not None:
                    self.logger.info("Current question exists, checking for response.")
                    # Check if the user has responded
                    self.response = self.communication_interface.get_user_response()
                    self.logger.debug(f"In check in scenario and response received: {self.response}")
                    response_text = self.response["response_text"]
                    if not response_text.strip():
                        # Ask the same question again
                        self.logger.info("Invalid response received, asking the same question again.")
                    else:
                        # Generate a animation based on sentiment
                        if self.current_question["expected_format"] == "short":
                            self.logger.info(f"publishing sentiment for week day response: {self.response['sentiment']}")
                            self.communication_interface.publish_robot_behaviour_command("sentiment", self.response["sentiment"])
                        self.next_question = self.ask_questions.get_question(question=self.current_question['question'], response=response_text)
                        if self.next_question is None:
                            self.step = 5
                            self.current_question = None
                            return
                        else:
                            self.current_question = self.next_question
                else:
                    self.logger.info("No current question, getting the first question for the day.")
                    # No question was asked yet, ask the first one
                    self.next_question = self.ask_questions.get_question()
                    self.current_question = self.next_question
                
                # Request the robot to ask the question
                self.communication_interface.publish_robot_speech(
                    message_type="question",
                    content=self.current_question['question']
                )
                self.waiting_for_response = True
                self.backchanneling_timer = time.time()
            elif self.communication_interface.get_robot_behaviour_completion_status("user response") == "complete" or self.communication_interface.get_robot_behaviour_completion_status("user response") == "failed":
                self.communication_interface.acknowledge_robot_behaviour_completion_status("user response")
                self.logger.info("User response acknowledged")
                self.waiting_for_response = False
            elif self.communication_interface.get_robot_behaviour_completion_status("question") == "complete":
                # Once the robot has asked the question, acknowledge the completion and wait for the user response
                self.communication_interface.acknowledge_robot_behaviour_completion_status("question")
                self.communication_interface.publish_collect_response(self.current_question["expected_format"])
                self.waiting_for_response = True
            elif self.waiting_for_response and time.time() - self.backchanneling_timer > 10:
                # Send a back channeling request
                self.communication_interface.publish_robot_behaviour_command("backchannel")
                self.backchanneling_timer = time.time()
                            
        # Step 5: Wish participants farewell
        elif self.step == 5:
            self._farewell_user()
            self.step = 6
            return
        
        # Step 5: Mark as complete
        elif self.step == 6:
            self.logger.info("Check-In Scenario Complete")
            self.step = 0
            self.communication_interface.configure_sleep_timer("On")
            self.complete = True
            self.communication_interface.end_check_in()
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
            self.communication_interface.acknowledge_robot_behaviour_completion_status("drive off charger")
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
            self.communication_interface.acknowledge_robot_behaviour_completion_status("greeting")
            self.logger.info("Greetings complete")
            self.waiting_for_response = False
            return True
        
        return False

    def _farewell_user(self):
        self.logger.info("Sending farewell.")
        self.communication_interface.publish_robot_speech(
            message_type="farewell",
            content="Thank you for checking in. Have a great day!"
        )
        self.communication_interface.publish_robot_behaviour_command("farewell")
        self.communication_interface.set_behaviour_running_status("check_in", "standby")
        self.logger.info("Voice assistant service completed successfully.")
    
    def is_complete(self):            
            return self.complete
    
    def error(self):
        self.logger.error("An error occurred while processing the check-in scenario.")
        return
    
    def resume(self):
        self.logger.info("Resuming the check-in scenario.")
        # Restart the current step in the scenario
        self.waiting_for_response = False
        self.current_question = None
        self.next_question = None
        self.response = None
        return
    
class CheckInQuestions:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.first_day = False

    def set_start_of_study(self, start_of_study):
        self.first_day = start_of_study
    
    def get_question(self,  question = "", response = ""):
        current_day = datetime.datetime.now().strftime('%A')
        if self.first_day:
            return self.start_of_study_questions(question, response)
        elif current_day == "Monday":
            return self.mondays_question(question, response)
        elif current_day == "Tuesday":
            return self.tuesdays_question(question, response)
        elif current_day == "Wednesday":
            return self.wednesdays_question(question, response)
        elif current_day == "Thursday":
            return self.thursdays_question(question, response)
        elif current_day == "Friday":
            return self.fridays_question(question, response)
        elif current_day == "Saturday":
            return self.saturdays_question(question, response)
        elif current_day == "Sunday":
            return self.sundays_question(question, response)
        
    def start_of_study_questions(self, question = "", response = ""):
        self.logger.info(f"In start_of_study_questions: question = {question}, response = {response}")
        if question == "":
            return {"question": "Did you exercise today?", "expected_format": "closed-ended"}
        elif question == "Did you exercise today?":
            return {"question": "How are you feeling about starting your behaviour change journey?", "expected_format": "open-ended"}
        elif question == "How are you feeling about starting your behaviour change journey?":
            return {"question": "Have you tried to change your behaviour before?", "expected_format": "closed-ended"}
        elif question == "Have you tried to change your behaviour before?":
            if "yes" in response.lower():
                return {"question": "WWhat has worked well for you?", "expected_format": "open-ended"}
            else:
                return {"question": "What obstacles have prevented you from changing your behaviour?", "expected_format": "open-ended"}
        elif question == "What has worked well for you?" or question == "What obstacles have prevented you from changing your behaviour?":
            return {"question": "On a scale of 1 to 10, with 1 being not at all important and 10 being very important, how important is it for you to exercise more?", "expected_format": "short"}
        elif question == "On a scale of 1 to 10, with 1 being not at all important and 10 being very important, how important is it for you to exercise more?" or question == "Please provide a valid number between 1 and 10.":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10.", "expected_format": "short"}
            else:
                return {"question": "Why is increasing your activity level important to you?", "expected_format": "open-ended"}
        elif question == "Why is increasing your activity level important to you?":
            return {"question": "What is one thing you can do to make it easier to succeed in your behaviour change?", "expected_format": "open-ended"}
        self.logger.info(f"No more questions for experience sampling. Returning None.")
        return None
    
    def mondays_question(self, question = "", response = ""):
        self.logger.info(f"In mondays_question: question = {question}, response = {response}")
        if question == "":
            return {"question": "Did you exercise today?", "expected_format": "closed-ended"}
        elif question == "Did you exercise today?":
            return {"question": "What does a typical day of physical activity look like for you?", "expected_format": "open-ended"}
        elif question == "What does a typical day of physical activity look like for you?":
            return {"question": "On a scale of 1 to 10, with 1 being low and 10 being high, how confident are you about staying active this week?", "expected_format": "short"}
        elif question == "On a scale of 1 to 10, with 1 being low and 10 being high, how confident are you about staying active this week?" or question == "Please provide a valid number between 1 and 10.":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                # Handle the case where no valid number was found
                return {"question": "Please provide a valid number between 1 and 10.", "expected_format": "short"}
            elif int(response) < 5:
                return {"question": "What obstacles kept you from meeting your goals?", "expected_format": "open-ended"}
            elif 5 <= int(response) <= 7:
                return {"question": "What would help you feel even more confident?", "expected_format": "open-ended"}
            else:
                return {"question": "That is excellent! What strategies worked well for you?", "expected_format": "open-ended"}
        elif question == "What obstacles kept you from meeting your goals?" or question == "What would help you feel even more confident?" or question == "That is excellent! What strategies worked well for you?":
            return {"question": "What is your main focus for staying active this week?", "expected_format": "open-ended"}
        elif question == "What is your main focus for staying active this week?":
            return {"question": "What would make you feel successful this week?", "expected_format": "open-ended"}
        self.logger.info(f"No more questions for experience sampling. Returning None.")
        return None
        
    def tuesdays_question(self, question = "", response = ""):
        self.logger.info(f"In tuesdays_question: question = {question}, response = {response}")
        if question == "":
            return {"question": "Did you exercise today?", "expected_format": "closed-ended"}
        elif question == "Did you exercise today?":
            return {"question": "What is something you enjoy about being active?", "expected_format": "open-ended"}
        elif question == "What is something you enjoy about being active?":
            return {"question": "Was it challenging to be active today?", "expected_format": "closed-ended"}
        elif question == "Was it challenging to be active today?":
            if "No" in response.lower():
                return {"question": "That is great! Is there anything you can do to keep it this way?", "expected_format": "open-ended"}
            else:
                return {"question": "What is one thing you can do to make it easier to be active?", "expected_format": "open-ended"}
        elif question == "That is great! Is there anything you can do to keep it this way?" or question == "What is one thing you can do to make it easier to be active?":
            return {"question": "What is keeping you motivated to stay active today?", "expected_format": "open-ended"}
        elif question == "What is keeping you motivated to stay active today?":
            return {"question": "What is one thing you look forward to achieving before our next check-in?", "expected_format": "open-ended"}
        self.logger.info(f"No more questions for experience sampling. Returning None.")
        return None
        
    def wednesdays_question(self, question = "", response = ""):
        self.logger.info(f"In wednesdays_question: question = {question}, response = {response}")
        if question == "":
            return {"question": "How have you found this journey so far?", "expected_format": "open-ended"}
        elif question == "How have you found this journey so far?":
            return {"question": "Have you been active today?", "expected_format": "closed-ended"}
        elif question == "Have you been active today?":
            return {"question": "If you could make one small change this week to move closer to your goal, what would it be?", "expected_format": "open-ended"}
        elif question == "If you could make one small change this week to move closer to your goal, what would it be?":
            return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you find yourself exercising automatically, without having to think about it?", "expected_format": "short"}
        elif question == "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you find yourself exercising automatically, without having to think about it?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                # Handle the case where no valid number was found
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you find yourself exercising automatically, without having to think about it?", "expected_format": "short"}
            else:
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you start exercising before you realize you're doing it?", "expected_format": "short"}
        elif question == "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you start exercising before you realize you're doing it?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you start exercising before you realize you're doing it?", "expected_format": "short"}
            else:
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Would you find it difficult to go a day without exercising?", "expected_format": "short"}
        if question == "On a scale of 1 to 10, with 1 being never and 10 being all the time. Would you find it difficult to go a day without exercising?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Would you find it difficult to go a day without exercising?", "expected_format": "short"}
        self.logger.info(f"No more questions for experience sampling. Returning None.")
        return None
        
    def thursdays_question(self, question = "", response = ""):
        self.logger.info(f"In thursdays_question: question = {question}, response = {response}")
        if question == "":
            return {"question": "Did you exercise today?", "expected_format": "closed-ended"}
        elif question == "Did you exercise today?":
            return {"question": "What strategies have you used so far to stay consistent with your activity so far?", "expected_format": "open-ended"}
        elif question == "What strategies have you used so far to stay consistent with your activity so far?":
            return {"question": "How can you apply these strategies in the future?", "expected_format": "open-ended"}
        elif question == "How can you apply these strategies in the future?":
            return {"question": "What does it mean to you to succeed in your behaviour change goal?", "expected_format": "open-ended"}
        elif question == "What does it mean to you to succeed in your behaviour change goal?":
            return {"question": "Are there any things you can do to increase the likelihood of succeeding in your behaviour change goal?", "expected_format": "open-ended"}
        elif question == "Are there any things you can do to increase the likelihood of succeeding in your behaviour change goal?":
            return {"question": "What is one thing you are looking forward to doing differently next week?", "expected_format": "open-ended"}
        self.logger.info(f"No more questions for experience sampling. Returning None.")
        return None
        
    def fridays_question(self, question = "", response = ""):
        self.logger.info(f"In fridays_question: question = {question}, response = {response}")
        if question == "":
            return {"question": "Did you exercise today?", "expected_format": "closed-ended"}
        elif question == "Did you exercise today?":
            return {"question": "What is been the most rewarding part of staying active this week?", "expected_format": "open-ended"}
        elif question == "What is been the most rewarding part of staying active this week?":
            return {"question": "On a scale of 1 to 10, with 1 being not at all important and 10 being very important, how important is it for you to exercise more?", "expected_format": "short"}
        elif question == "On a scale of 1 to 10, with 1 being not at all important and 10 being very important, how important is it for you to exercise more?" or question == "Please provide a valid number between 1 and 10.":
            if response is None or response == "" or int(response) < 0 or int(response) > 10:
                # Handle the case where no valid number was found
                return {"question": "Please provide a valid number between 1 and 10.", "expected_format": "short"}
            elif int(response) < 5:
                return {"question": "What obstacles have prevented you from performing the behaviour?", "expected_format": "open-ended"}
            elif 5 <= int(response) <= 8:
                return {"question": "What would help you feel even more confident?", "expected_format": "open-ended"}
            else:
                return {"question": "That is excellent! What is your plan to stay on track?", "expected_format": "open-ended"}
        elif question == "What obstacles have prevented you from performing the behaviour?" or question == "What would help you feel even more confident?" or question == "That is excellent! What is your plan to stay on track?":
            return {"question": "What has been the biggest challenge for you?", "expected_format": "open-ended"}
        elif question == "What has been the biggest challenge for you?":
            return {"question": "How have you overcome challenges this week?", "expected_format": "open-ended"}
        elif question == "How have you overcome challenges this week?":
            return {"question": "What is one piece of advice you would give someone else trying to be more active?", "expected_format": "open-ended"}
        self.logger.info(f"No more questions for experience sampling. Returning None.")
        return None
        
    def saturdays_question(self, question = "", response = ""):
        self.logger.info(f"In saturdays_question: question = {question}, response = {response}")
        if question == "":
            return {"question": "Did you exercise today?", "expected_format": "closed-ended"}
        elif question == "Did you exercise today?":
            return {"question": "What is one thing you have learned about yourself this week?", "expected_format": "open-ended"}
        elif question == "What is one thing you have learned about yourself this week?":
            return {"question": "What is one thing you would like to focus on next week to improve your routine?", "expected_format": "open-ended"}
        elif question == "What is one thing you would like to focus on next week to improve your routine?":
            return {"question": "What is one small step you could take to make next week even better?", "expected_format": "open-ended"}
        elif question == "What is one small step you could take to make next week even better?":
            return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you find yourself exercising automatically, without having to think about it?", "expected_format": "short"}
        elif question == "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you find yourself exercising automatically, without having to think about it?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you find yourself exercising automatically, without having to think about it?", "expected_format": "short"}
            else:
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you start exercising before you realize you're doing it?", "expected_format": "short"}
        elif question == "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you start exercising before you realize you're doing it?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Do you start exercising before you realize you're doing it?", "expected_format": "short"}
            else:
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Would you find it difficult to go a day without exercising?", "expected_format": "short"}
        if question == "On a scale of 1 to 10, with 1 being never and 10 being all the time. Would you find it difficult to go a day without exercising?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. Would you find it difficult to go a day without exercising?", "expected_format": "short"}
        self.logger.info(f"No more questions for experience sampling. Returning None.")
        return None
        
    def sundays_question(self, question = "", response = ""):
        self.logger.info(f"In sundays_question: question = {question}, response = {response}")
        if question == "":
            return {"question": "Did you exercise today?", "expected_format": "closed-ended"}
        elif question == "Did you exercise today?":
            return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. How would you rate your progress on a scale of 1 to 10?", "expected_format": "short"}
        elif question == "On a scale of 1 to 10, with 1 being never and 10 being all the time. How would you rate your progress on a scale of 1 to 10?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                # Handle the case where no valid number was found
                return {"question": "On a scale of 1 to 10, with 1 being never and 10 being all the time. How would you rate your progress on a scale of 1 to 10?", "expected_format": "short"}
            elif int(response) < 5:
                return {"question": "What obstacles kept you from meeting your goals?", "expected_format": "open-ended"}
            elif 5 <= int(response) <= 7:
                return {"question": "What can you improve next week?", "expected_format": "open-ended"}
            else:
                return {"question": "Great! What strategies worked well for you?", "expected_format": "open-ended"}
        elif question == "What obstacles kept you from meeting your goals?" or question == "What can you improve next week?" or question == "Great! What strategies worked well for you?":
            return {"question": "Keeping in mind your activity level over the past week, on a scale between 1 and 10, with 1 being never and 10 being always. Over the past week, how often did you feel like you wanted to exercise?", "expected_format": "short"}
        # intensity
        if question == "Keeping in mind your activity level over the past week, on a scale between 1 and 10, with 1 being never and 10 being always. Over the past week, how often did you feel like you wanted to exercise?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you feel like you wanted to exercise?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you feel like you wanted to exercise?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did you feel like you needed to exercise?", "expected_format": "short"}
        elif question == "On a scale between 1 and 10, over the past week, how often did you feel like you needed to exercise?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you feel like you needed to exercise?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you feel like you needed to exercise?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did you have a strong urge to exercise?", "expected_format": "short"}
        elif question == "On a scale between 1 and 10, over the past week, how often did you have a strong urge to exercise?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you have a strong urge to exercise?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you have a strong urge to exercise?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did you imagine how good it would be to exercise?", "expected_format": "short"}
        # Incentives imagery
        elif question == "On a scale between 1 and 10, over the past week, how often did you imagine how good it would be to exercise?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine how good it would be to exercise?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine how good it would be to exercise?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did you imagine how much better you would feel after exercising?", "expected_format": "short"}
        elif question == "On a scale between 1 and 10, over the past week, how often did you imagine how much better you would feel after exercising?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine how much better you would feel after exercising?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine how much better you would feel after exercising?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did you imagine how much worse you would feel if you didn not exercise?", "expected_format": "short"}
        # Self-efficacy
        elif question == "On a scale between 1 and 10, over the past week, how often did you imagine how much worse you would feel if you didn not exercise?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine how much worse you would feel if you didn not exercise?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine how much worse you would feel if you didn not exercise?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did you imagine yourself exercising?", "expected_format": "short"}
        elif question == "On a scale between 1 and 10, over the past week, how often did you imagine yourself exercising?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine yourself exercising?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine yourself exercising?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did you imagine how you would exercise?", "expected_format": "short"}
        elif question == "On a scale between 1 and 10, over the past week, how often did you imagine how you would exercise?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine how you would exercise?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine how you would exercise?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did you imagine succeeding at exercising?", "expected_format": "short"}
        elif question == "On a scale between 1 and 10, over the past week, how often did you imagine succeeding at exercising?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine succeeding at exercising?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you imagine succeeding at exercising?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did you picture times you did picture doing something like this in the past?", "expected_format": "short"}
        elif question == "On a scale between 1 and 10, over the past week, how often did you picture times you did picture doing something like this in the past?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did you picture times you did picture doing something like this in the past?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did you picture times you did picture doing something like this in the past?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did thoughts of exercising come to mind?", "expected_format": "short"}
        # Availability
        elif question == "On a scale between 1 and 10, over the past week, how often did thoughts of exercising come to mind?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did thoughts of exercising come to mind?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did thoughts of exercising come to mind?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did other things remind you of exercising?", "expected_format": "short"}
        elif question == "On a scale between 1 and 10, over the past week, how often did other things remind you of exercising?" or question == "Please provide a valid number between 1 and 10. Over the past week, how often did other things remind you of exercising?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. Over the past week, how often did other things remind you of exercising?", "expected_format": "short"}
            else:
                return {"question": "On a scale between 1 and 10, over the past week, how often did thoughts about exercising grab your attention?", "expected_format": "short"}
        elif question == "On a scale between 1 and 10, over the past week, how often did thoughts about exercising grab your attention?" or question == "Please provide a valid number between 1 and 10. 3. Over the past week, how often did thoughts about exercising grab your attention?":
            if response is None or response == "" or int(response) < 1 or int(response) > 10:
                return {"question": "Please provide a valid number between 1 and 10. 3. Over the past week, how often did thoughts about exercising grab your attention?", "expected_format": "short"}
            else:
                return {"question": "Thank you for answering those questions. Is there anything you are excited to achieve by the end of next week?", "expected_format": "open-ended"}
        self.logger.info(f"No more questions for experience sampling. Returning None.")
        return None