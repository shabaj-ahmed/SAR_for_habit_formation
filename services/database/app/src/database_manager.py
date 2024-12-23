from sqlmodel import Session, select
from .user_profile_db_schema import UserProfile, UserResponse, Reminder, ObjectiveData
from datetime import datetime

class DatabaseManager:
    def __init__(self, session: Session, dispatcher=None):
        """
        Initialises the DatabaseManager with a session.
        :param session: An active SQLModel session object.
        """
        self.session = session
        self.dispatcher = dispatcher
        self._register_event_handlers()

    def _register_event_handlers(self):
        """Register event handlers for robot actions."""
        if self.dispatcher:
            self.dispatcher.register_event("update_user_profile", self.update_user_profile_field)
            self.dispatcher.register_event("batch_update_user_responses", self.batch_update_user_responses)
            self.dispatcher.register_event("upsert_reminder", self.upsert_reminder)
            self.dispatcher.register_event("add_objective_data", self.add_objective_data)

    # Create if one does not exist
    def create_user_profile(session: Session, profile: UserProfile):
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile

    # Read
    def get_user_profile(session: Session, user_id: int):
        return session.get(UserProfile, user_id)

    def get_user_responses(session: Session):
        return session.exec(select(UserResponse)).all()
    
    # I might need to create some shared libraries with enums of something to store all these string values for retriving data
    # Get any field required from the user profile
    def get_user_profile_field(session: Session, user_id: int, field: str):
        user_profile = session.get(UserProfile, user_id)
        if not user_profile:
            return None
        if hasattr(user_profile, field):
            return getattr(user_profile, field)
        else:
            raise AttributeError(f"{field} is not a valid attribute of UserProfile")

    # Update
    # UserProfile Operations
    def update_user_profile_field(self, user_id: int, field: str, value):
        user_profile = self.session.get(UserProfile, user_id)
        if not user_profile:
            return None
        if hasattr(user_profile, field):
            setattr(user_profile, field, value)
            self.session.commit()
            self.session.refresh(user_profile)
            return user_profile
        else:
            raise AttributeError(f"{field} is not a valid attribute of UserProfile")

    # Record all questions and responses given during the checkin process
    def batch_update_user_responses(self, responses: list[dict]):
        for response_data in responses:
            response = self.session.exec(
                select(UserResponse).where(UserResponse.id == response_data.get("id"))
            ).one_or_none()
            if response:
                # Update existing response
                response.question = response_data.get("question", response.question)
                response.response = response_data.get("response", response.response)
                response.timestamp = response_data.get("timestamp", response.timestamp)
            else:
                # Insert new response
                new_response = UserResponse(
                    question=response_data["question"],
                    response=response_data["response"],
                    timestamp=response_data["timestamp"],
                )
                self.session.add(new_response)
        self.session.commit()

    # When the robot sends a reminder record it in the database
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

    # Record backend objective data
    def add_objective_data(self, data_id: int, interactions: int, duration: str, timestamp: str):
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if data for today already exists
        existing_entry = self.session.exec(
            select(ObjectiveData).where(ObjectiveData.timestamp == today)
        ).one_or_none()

        if existing_entry:
            # Update existing entry
            existing_entry.number_of_interactions_in_a_day = interactions
            existing_entry.total_duration_of_interaction = duration
            existing_entry.timestamp = timestamp
        else:
            # Create a new entry
            new_entry = ObjectiveData(
                id=data_id,
                number_of_interactions_in_a_day=interactions,
                total_duration_of_interaction=duration,
                timestamp=timestamp,
            )
            self.session.add(new_entry)

        self.session.commit()
        self.session.refresh(new_entry if not existing_entry else existing_entry)
        return True

    # Delete
    # Delete history for a specific date
    def delete_user_responses(session: Session, response_id: int = None, date: str = None):
        responses = session.exec(
            select(UserResponse).where(UserResponse.timestamp == date)
        ).all()
        for response in responses:
            session.delete(response)
        session.commit()