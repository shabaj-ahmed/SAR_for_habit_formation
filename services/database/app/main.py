from src.communication_interface import CommunicationInterface
from src.event_dispatcher import EventDispatcher
from src.study_data_db_manager import StudyDatabaseManager
from src.persistent_data_db_manager import PersistentDataManager
from src.persistent_data_db_schema import UserProfile, ServiceState
from src.database import init_persistent_db, get_study_data_session, init_study_db, get_persistent_data_session

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

def initialise_persistent_database(session):
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
        print("User profile initialised successfully.")

        service_states = [
            ServiceState(service_name="robot_controller", state_name="status", state_value="running", user_id=1),
            ServiceState(service_name="user_interface", state_name="status", state_value="running", user_id=1),
            ServiceState(service_name="speech_recognition", state_name="status", state_value="running", user_id=1),
            ServiceState(service_name="reminder", state_name="status", state_value="running", user_id=1),
        ]
        
        session.add_all(service_states)
        print("Service states added to the database.")
        session.commit()
        print("ServiceState database initialized with default values.")
        

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
        
        # Initialise the databases
        init_study_db()
        init_persistent_db()

        with get_persistent_data_session() as persistent_data_session:
            PersistentDataManager(persistent_data_session, dispatcher)
            initialise_persistent_database(persistent_data_session)
        with get_study_data_session() as study_data_session:
            StudyDatabaseManager(study_data_session, dispatcher)

        communication_interface = CommunicationInterface(
            broker_address=str(os.getenv("MQTT_BROKER_ADDRESS")),
            port=1883,
            event_dispatcher=dispatcher
        )

        communication_interface.publish_database_status("Awake")

        heart_beat_thread = threading.Thread(target=publish_heartbeat, daemon=True)
        heart_beat_thread.start()
        print("Database service started.")

        # Keep the main thread alive
        while True:
            time.sleep(0.4)
    except KeyboardInterrupt as e:
        heart_beat_thread.join()
        communication_interface.disconnect()
