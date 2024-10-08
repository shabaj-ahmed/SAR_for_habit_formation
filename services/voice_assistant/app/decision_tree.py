
import speach_recognition as sr
import datetime
import re

# def save_response(question, response, summary=""):
# Save the response to a database or file

# Function to determine the next question based on the current response

# Function to determine the next question based on the current response


def extract_number_from(response):
    # Use regex to find the first occurrence of a number (integer)
    match = re.search(r'\d+', response)
    if match:
        return int(match.group())
    else:
        return None


def determine_next_question(question, response, current_day):

    # Example branching based on initial question
    if question == "How would you rate your progress on a scale of 1 to 10?":
        try:
            rating = extract_number_from(response)
            if rating < 5:
                return {"question": "What obstacles kept you from meeting your goals?", "expected_format": "open-ended"}
            elif 5 <= rating <= 7:
                return {"question": "What can you improve next week?", "expected_format": "open-ended"}
            else:
                return {"question": "Great! What strategies worked well for you?", "expected_format": "open-ended"}
        except ValueError:
            return {"question": "Please provide a valid number between 1 and 10.", "expected_format": "short"}

    # Branching based on responses for obstacles
    if question == "What obstacles kept you from meeting your goals?":
        if "time" in response.lower():
            return {"question": "Would allocating more time next week help?", "expected_format": "open-ended"}
        elif "motivation" in response.lower():
            return {"question": "What could help you stay motivated?", "expected_format": "open-ended"}
        else:
            return {"question": "What can you change to improve your progress?", "expected_format": "open-ended"}

    if question == "What is your main goal for today?":
        return {"question": "What strategies will you use to achieve this goal?", "expected_format": "open-ended"}

    # Different question sets based on the day (e.g., Monday, Tuesday)
    if current_day == "Saturday" and question == "What can you improve next week?":
        return {"question": "What specific goals do you have for this week?", "expected_format": "open-ended"}
    elif current_day == "Sunday" and question == "What strategies worked well for you?":
        return {"question": "What would you like to reflect on this week?", "expected_format": "open-ended"}
    elif current_day == "Monday" and question == "What strategies worked well for you?":
        return {"question": "What would you like to reflect on this week?", "expected_format": "open-ended"}
    elif current_day == "Tuseday" and question == "What strategies worked well for you?":
        return {"question": "What would you like to reflect on this week?", "expected_format": "open-ended"}
    elif current_day == "Wednesday" and question == "What strategies worked well for you?":
        return {"question": "What would you like to reflect on this week?", "expected_format": "open-ended"}
    elif current_day == "Thursday" and question == "What strategies worked well for you?":
        return {"question": "What would you like to reflect on this week?", "expected_format": "open-ended"}
    elif current_day == "Friday" and question == "What strategies worked well for you?":
        return {"question": "What would you like to reflect on this week?", "expected_format": "open-ended"}

    return None

# Function to ask questions and continue based on responses


def ask_question(question, expected_format="short", current_day="Monday"):
    while question:

        # Publish the question to the speech microservice and get the response
        response = sr.recognise_response(expected_format)

        # Determine the next question based on the current response
        next_question = determine_next_question(
            question, response, current_day)

        # If there is no next question, break the loop
        if next_question is None:
            # print("All questions answered.")
            break

        # Move to the next question
        question = next_question["question"]
        expected_format = next_question["expected_format"]


# Function to determine the day and adjust the questions accordingly
def get_current_day_questions():
    # Get the current day of the week
    current_day = datetime.datetime.now().strftime('%A')

    # Assign different initial questions based on the day
    if current_day == "Saturday":
        initial_question = {
            "question": "How would you rate your progress on a scale of 1 to 10?", "expected_format": "short"}
    elif current_day == "Sunday":
        initial_question = {
            "question": "What strategies helped you this week?", "expected_format": "open-ended"}
    elif current_day == "Monday":
        initial_question = {
            "question": "How would you rate your progress on a scale of 1 to 10?", "expected_format": "short"}
    elif current_day == "Tuseday":
        initial_question = {
            "question": "What strategies helped you this week?", "expected_format": "open-ended"}
    elif current_day == "Wednesday":
        initial_question = {
            "question": "How would you rate your progress on a scale of 1 to 10?", "expected_format": "short"}
    elif current_day == "Thursday":
        initial_question = {
            "question": "What strategies helped you this week?", "expected_format": "open-ended"}
    elif current_day == "Friday":
        initial_question = {
            "question": "How would you rate your progress on a scale of 1 to 10?", "expected_format": "short"}
    else:
        initial_question = {
            "question": "What is your main goal for today?", "expected_format": "open-ended"}

    return initial_question, current_day

# Start the check-in process


def check_in():
    # Get the current day and determine the initial question based on that
    initial_question, current_day = get_current_day_questions()

    # Start asking questions in a loop based on the day
    ask_question(initial_question["question"],
                 initial_question["expected_format"], current_day)


if __name__ == "__main__":
    # Start check-in process
    check_in()
