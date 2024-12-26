from sqlmodel import Session, select
from .study_data_db_schema import StudyMeta, CheckIn, Reminder
from datetime import datetime

class StudyDatabaseManager:
    def __init__(self, session: Session, dispatcher=None):
        """
        Initializes the StudyDatabaseManager with a session.
        """
        self.session = session
        self.dispatcher = dispatcher
        self._register_event_handlers()

    def _register_event_handlers(self):
        """Register event handlers for robot actions."""
        if self.dispatcher:
            self.dispatcher.register_event("save_check_in", self.save_check_in)
            self.dispatcher.register_event("upsert_reminder", self.upsert_reminder)

    def get_user_responses(self):
        return self.session.exec(select(CheckIn)).all()

    def save_check_in(self, responses):
        print("Saving check-in data")
        # Get today's date
        today_date = str(datetime.now().date())

        # Check if a StudyMeta entry exists for today
        statement = select(StudyMeta).where(StudyMeta.date == today_date)
        study_meta = self.session.exec(statement).one_or_none()

        # If no StudyMeta entry exists, create one
        if not study_meta:
            study_meta = StudyMeta(
                number_of_interactions_in_a_day=0,  # Initial values
                total_duration_of_interaction="01:00:00",
                checkin_time="",
                checkin_duration="",
                date=today_date
            )
            self.session.add(study_meta)
            self.session.commit()  # Commit to generate an ID for the new StudyMeta
            self.session.refresh(study_meta)

        print(f"responses received: {responses}")
        # Add CheckIn responses and associate them with StudyMeta
        for response in responses:
            new_response = CheckIn(
                question=response["question"],
                response=response["response"],
                study_meta_id=study_meta.id  # Link to the correct StudyMeta entry
            )
            self.session.add(new_response)

        # Update StudyMeta fields (e.g., number of interactions)
        study_meta.number_of_interactions_in_a_day += len(responses)
        self.session.commit()



    def upsert_reminder(self, reminder_id: int, reminder_time: str, reminder_message: str):
        reminder = self.session.get(Reminder, reminder_id)
        if reminder:
            reminder.reminder_time = reminder_time
            reminder.reminder_message = reminder_message
        else:
            reminder = Reminder(
                id=reminder_id, reminder_time=reminder_time, reminder_message=reminder_message
            )
            self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)
        return reminder

    def delete_user_responses(self, response_id: int = None, date: str = None):
        responses = self.session.exec(
            select(CheckIn).where(CheckIn.timestamp == date)
        ).all()
        for response in responses:
            self.session.delete(response)
        self.session.commit()
