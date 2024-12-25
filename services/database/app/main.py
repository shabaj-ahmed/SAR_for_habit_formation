from src.communication_interface import CommunicationInterface
from src.event_dispatcher import EventDispatcher
from src.study_data_db_manager import StudyDatabaseManager
from src.persistent_data_db_manager import PersistentDataManager
from src.persistent_data_db_schema import ServiceState
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

    # Check if the database already exists
    existing_service_states = session.exec(select(ServiceState)).all()

    if existing_service_states:
        print("User profile already exists. No action taken.")
    else:
        print("No user profile found. Initializing database with default configuration.")

        # Prepare data for the new UserProfile
        reminder_time = configs.get_reminder_time()

        service_states = [
            ServiceState(service_name="reminder", state_name="user_name", state_value=str(configs.get_user_name())),
            ServiceState(service_name="reminder", state_name="study_duration", state_value=str(configs.get_study_duration())),
            ServiceState(service_name="reminder", state_name="reminder_time_hr", state_value=str(reminder_time["hours"])),
            ServiceState(service_name="reminder", state_name="reminder_time_min", state_value=str(reminder_time["minutes"])),
            ServiceState(service_name="reminder", state_name="reminder_time_ampm", state_value=reminder_time["ampm"]),
            ServiceState(service_name="reminder", state_name="implementation_intention", state_value=configs.get_implementation_intention()),

            ServiceState(service_name="robot_controller", state_name="robot_colour", state_value="green"),
            ServiceState(service_name="robot_controller", state_name="robot_volume", state_value="medium"),
            ServiceState(service_name="robot_controller", state_name="robot_voice", state_value="default"),

            ServiceState(service_name="user_interface", state_name="screen_brightness", state_value="medium"),
            ServiceState(service_name="user_interface", state_name="sleep_timer", state_value=configs.get_sleep_timer()),

            ServiceState(service_name="speech_recognition", state_name="user_name", state_value=str(configs.get_user_name())),

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
