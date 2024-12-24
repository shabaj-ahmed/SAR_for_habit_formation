from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from sqlalchemy import MetaData


class StudyMeta(SQLModel, table=True):
    """
    Stores study metadata for each day.
    """
    id: int = Field(default=None, primary_key=True)
    number_of_interactions_in_a_day: int
    total_duration_of_interaction: str
    checkin_time: str
    checkin_duration: str
    timestamp: str

    # Foreign Key
    user_id: int = Field(default=None, foreign_key="userprofile.id")

    # Relationship with CheckIn
    checkins: List["CheckIn"] = Relationship(back_populates="study_meta")


class CheckIn(SQLModel, table=True):
    """
    Stores user responses for the check-in process.
    """
    id: int = Field(default=None, primary_key=True)
    question: str
    response: str

    # Foreign Key
    study_meta_id: int = Field(default=None, foreign_key="studymeta.id")
    study_meta: Optional[StudyMeta] = Relationship(back_populates="checkins")


class Reminder(SQLModel, table=True ):
    """
    Stores reminder data.
    """
    id: int = Field(default=None, primary_key=True)
    reminder_time: str
    reminder_message: str

    # Foreign Key
    user_id: int = Field(default=None, foreign_key="userprofile.id")
