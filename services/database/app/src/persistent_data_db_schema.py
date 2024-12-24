from sqlmodel import Field, SQLModel, Relationship
from typing import List, Optional
from sqlalchemy import MetaData

class UserProfile(SQLModel, table=True):
    """
    Stores persistent user profile data.
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

    # Relationship with ServiceState
    service_states: List["ServiceState"] = Relationship(back_populates="user")


class ServiceState(SQLModel, table=True):
    """
    Stores the state of the services.
    """
    id: int = Field(default=None, primary_key=True)
    service_name: str
    state_name: str
    state_value: str

    # Foreign Key
    user_id: int = Field(default=None, foreign_key="userprofile.id")

    # Relationship with UserProfile
    user: Optional[UserProfile] = Relationship(back_populates="service_states")