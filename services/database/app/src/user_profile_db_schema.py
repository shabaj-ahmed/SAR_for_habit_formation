from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

class UserProfile(SQLModel, table=True):
    """
    This class is used to store user profile data.
    """
    id: int = Field(default=None, primary_key=True)
    study_duration: int
    reminder_time_hr: str
    reminder_time_min: str
    reminder_time_ampm: str
    implementation_intention: str
    robot_colour: str
    robot_volume: str
    screen_brightness: str
    robot_voice: str

    # Relationships
    checkins: List["CheckinMeta"] = Relationship(back_populates="user")
    responses: List["UserResponse"] = Relationship(back_populates="user")
    reminders: List["Reminder"] = Relationship(back_populates="user")
    objective_data: List["ObjectiveData"] = Relationship(back_populates="user")


class CheckinMeta(SQLModel, table=True):
    """
    This class is used to store the metadata of the check-in process.
    """
    id: int = Field(default=None, primary_key=True)
    checkin_time: str
    checkin_duration: str
    timestamp: str

    # Foreign Key
    user_id: int = Field(default=None, foreign_key="userprofile.id")

    # Relationship
    user: Optional[UserProfile] = Relationship(back_populates="checkins")


class UserResponse(SQLModel, table=True):
    """
    This class is used to store user responses to the questions asked during the check-in process.
    """
    id: int = Field(default=None, primary_key=True)
    question: str
    response: str
    timestamp: str

    # Foreign Key
    user_id: int = Field(default=None, foreign_key="userprofile.id")

    # Relationship
    user: Optional[UserProfile] = Relationship(back_populates="responses")


class Reminder(SQLModel, table=True):
    """
    This class is used to store if a reminder has been sent to the user or not.
    """
    id: int = Field(default=None, primary_key=True)
    reminder_time: str
    reminder_message: str

    # Foreign Key
    user_id: int = Field(default=None, foreign_key="userprofile.id")

    # Relationship
    user: Optional[UserProfile] = Relationship(back_populates="reminders")


class ObjectiveData(SQLModel, table=True):
    """
    This class is used to store daily interaction data with the system.
    """
    id: int = Field(default=None, primary_key=True)
    number_of_interactions_in_a_day: int
    total_duration_of_interaction: str
    timestamp: str

    # Foreign Key
    user_id: int = Field(default=None, foreign_key="userprofile.id")

    # Relationship
    user: Optional[UserProfile] = Relationship(back_populates="objective_data")
