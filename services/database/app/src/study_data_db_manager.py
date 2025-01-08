from sqlmodel import Session, select
from .study_data_db_schema import StudyMeta, CheckInMeta, CheckIn
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
            self.dispatcher.register_event("create_new_reminder", self.create_new_reminder)
            self.dispatcher.register_event("request_history", self.retrieve_history)
    
    def save_check_in(self, responses):
        print("Saving check-in data")

        today_date = datetime.now().date().strftime("%Y-%m-%d")

        # Check if a StudyMeta entry exists for today
        statement = select(StudyMeta).where(StudyMeta.date == today_date)
        study_meta = self.session.exec(statement).one_or_none()

        # If no StudyMeta entry exists, create one
        if not study_meta:
            study_meta = StudyMeta(
                number_of_interactions_in_a_day=0,  # Initial values
                total_duration_of_interaction="00:00",
                date=today_date,
                reminder_message="",
            )
            self.session.add(study_meta)
            self.session.commit()  # Commit to generate an ID for the new StudyMeta
            self.session.refresh(study_meta)

        # Check if a CheckInMeta entry already exists for today's StudyMeta
        checkin_meta = (
            self.session.exec(
                select(CheckInMeta)
                .where(CheckInMeta.study_meta_id == study_meta.id)
            ).one_or_none()
        )

        if not checkin_meta:
            # If no CheckInMeta exists, create one
            checkin_meta = CheckInMeta(
                checkin_time=today_date,
                checkin_duration="00:00",  # Placeholder duration
                study_meta_id=study_meta.id,
            )
            self.session.add(checkin_meta)
            self.session.commit()  # Commit to generate an ID for the new CheckInMeta
            self.session.refresh(checkin_meta)
        
        print(f"responses received: {responses}")
        # Add CheckIn responses and associate them with StudyMeta
        for response in responses:
            new_checkin = CheckIn(
                question=response["question"],
                response=response["response"],
                study_meta_id=checkin_meta.id  # Link to the correct StudyMeta entry
            )
            checkin_meta.checkins.append(new_checkin)

        self.session.commit()

        # Update StudyMeta fields (e.g., number of interactions)
        study_meta.number_of_interactions_in_a_day += 1
        self.session.commit()

    def create_new_reminder(self, reminder_message: str):
        print("Creating new reminder")
        today_date = datetime.now().date().strftime("%Y-%m-%d")

        # Check if a StudyMeta entry exists for today
        statement = select(StudyMeta).where(StudyMeta.date == today_date)
        study_meta = self.session.exec(statement).one_or_none()

        # If no StudyMeta entry exists, create one
        if not study_meta:
            study_meta = StudyMeta(
                number_of_interactions_in_a_day=0,  # Initial values
                total_duration_of_interaction="",
                date=today_date,
                reminder_message = "",
                number_of_network_failures=0,
                number_of_robot_crashes=0
            )
        
        study_meta.reminder_message = reminder_message
        
        self.session.add(study_meta)
        self.session.commit()  # Commit to generate an ID for the new StudyMeta
        self.session.refresh(study_meta)

    def retrieve_history(self):
        print("Retrieving history")
        statement = select(StudyMeta)
        study_meta_list = self.session.exec(statement).all()
        if not study_meta_list:
            return None
        
        serialised_data = []
        
        for row in study_meta_list:
            serialised_data.append(
                {
                    "date": row.date,
                }
            )
            
        print(f"Retrieved history: {serialised_data}")
        self.dispatcher.dispatch_event("send_history", serialised_data)