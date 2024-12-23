from src.database import init_db, get_user_profile_session, init_service_state_db
from src.communication_interface import CommunicationInterface
from src.event_dispatcher import EventDispatcher
from src.database_manager import DatabaseManager
from src.user_profile_db_schema import UserProfile
from src.system_state_db_profile import ServiceState

from sqlmodel import select
import logging
import time
import threading

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)

from configurations.initial_configurations import StudyConfigs
from shared_libraries.logging_config import setup_logger

def initialise_user_profile_database(session, db_manager):
    # Load the initial configurations
    configs = StudyConfigs()

    # Check if the user profile already exists
    existing_user = session.exec(select(UserProfile).where(UserProfile.id == 1)).first()
    
    if existing_user:
        print("User profile already exists. No action taken.")
    else:
        print("No user profile found. Initializing database with default configuration.")

        # Prepare data for the new UserProfile
        reminder_time = configs.get_reminder_time()
        new_user_profile = UserProfile(
            id=1,  # Assuming single-user database
            study_duration=configs.get_study_duration(),
            reminder_time_hr=str(reminder_time["hours"]),
            reminder_time_min=str(reminder_time["minutes"]),
            reminder_time_ampm=reminder_time["ampm"],
            implementation_intention=configs.get_implementation_intention(),
            robot_colour="default",  # Default values, can be modified
            robot_volume="medium",
            screen_brightness="medium",
            robot_voice="default"
        )

        # Add the new user profile to the database
        session.add(new_user_profile)
        session.commit()
        print("User profile initialised successfully.")

def publish_heartbeat():
    while True:
        # Publish robot controller heartbeat
        logger.info("Robot controller heartbeat")
        time.sleep(30)  # Publish heartbeat every 30 seconds

if __name__ == "__main__":
    try:
        setup_logger()

        logger = logging.getLogger("Main")

        dispatcher = EventDispatcher()

        communication_interface = CommunicationInterface(
            broker_address=str(os.getenv("MQTT_BROKER_ADDRESS")),
            port=int(os.getenv("MQTT_BROKER_PORT")),
            event_dispatcher=dispatcher
        )

        communication_interface.publish_database_status("Awake")

        heart_beat_thread = threading.Thread(target=publish_heartbeat, daemon=True)
        heart_beat_thread.start()

        # Initialise the databases
        init_db()
        init_service_state_db()

        with get_user_profile_session() as session:
            db_manager = DatabaseManager(session, dispatcher)
            initialise_user_profile_database(session, db_manager)

        # Keep the main thread alive
        while True:
            time.sleep(0.4)
    except KeyboardInterrupt as e:
        heart_beat_thread.join()
        communication_interface.disconnect()