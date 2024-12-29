from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional

class StudyMeta(SQLModel, table=True):
    """
    Stores study metadata for each day.
    """
    id: int = Field(default=None, primary_key=True)
    number_of_interactions_in_a_day: int
    total_duration_of_interaction: str  # Format: HH:MM
    date: str  # Format: YYYY-MM-DD
    reminder_message: str

    # Relationship with CheckInMeta
    checkin_meta: List["CheckInMeta"] = Relationship(back_populates="study_meta")


class CheckInMeta(SQLModel, table=True):
    """
    Stores metadata for each check-in session.
    """
    id: int = Field(default=None, primary_key=True)
    checkin_time: str  # Format: HH:MM
    checkin_duration: str  # Format: HH:MM

    # Foreign Key linking to StudyMeta
    study_meta_id: int = Field(default=None, foreign_key="studymeta.id")
    study_meta: Optional[StudyMeta] = Relationship(back_populates="checkin_meta")

    # Relationship with CheckIn
    checkins: List["CheckIn"] = Relationship(back_populates="checkin_meta")


class CheckIn(SQLModel, table=True):
    """
    Stores individual questions and responses during the check-in process.
    """
    id: int = Field(default=None, primary_key=True)
    question: str
    response: str

    # Foreign Key linking to CheckInMeta
    checkin_meta_id: int = Field(default=None, foreign_key="checkinmeta.id")
    checkin_meta: Optional[CheckInMeta] = Relationship(back_populates="checkins")
