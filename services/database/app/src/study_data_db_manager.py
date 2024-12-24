from sqlmodel import Session, select
from .study_data_db_schema import CheckIn, Reminder

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
            self.dispatcher.register_event("batch_update_user_responses", self.batch_update_user_responses)
            self.dispatcher.register_event("upsert_reminder", self.upsert_reminder)

    def get_user_responses(self):
        return self.session.exec(select(CheckIn)).all()

    def batch_update_user_responses(self, responses: list[dict]):
        for response_data in responses:
            response = self.session.exec(
                select(CheckIn).where(CheckIn.id == response_data.get("id"))
            ).one_or_none()
            if response:
                response.question = response_data.get("question", response.question)
                response.response = response_data.get("response", response.response)
            else:
                new_response = CheckIn(
                    question=response_data["question"],
                    response=response_data["response"],
                )
                self.session.add(new_response)
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
