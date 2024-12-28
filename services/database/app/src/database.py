from contextlib import contextmanager
from sqlmodel import create_engine, Session, SQLModel
# from .persistent_data_db_schema import ServiceState
# from .study_data_db_schema import StudyMeta, CheckIn, Reminder

# Study data database connection
study_data_file_name = "services/database/app/database/hri_study.db"
study_data_url = f"sqlite:///{study_data_file_name}"
study_data_engine = create_engine(study_data_url)


# Persistent data database connection
persistent_data_file_name = "services/database/app/database/persistent.db"
persistent_data_url = f"sqlite:///{persistent_data_file_name}"
persistent_data_engine = create_engine(persistent_data_url)


def init_study_db():
    """
    Initializes the study data database with only study-related tables.
    """
    SQLModel.metadata.create_all(
        study_data_engine,
        tables=[
            SQLModel.metadata.tables["studymeta"],
            SQLModel.metadata.tables["checkinmeta"],
            SQLModel.metadata.tables["checkin"],
        ],
    )


def init_persistent_db():
    """
    Initializes the persistent data database with only persistent tables.
    """
    SQLModel.metadata.create_all(
        persistent_data_engine,
        tables=[
            SQLModel.metadata.tables["servicestate"],
        ],
    )


@contextmanager
def get_study_data_session():
    session = Session(study_data_engine)
    try:
        yield session
    finally:
        session.close()


@contextmanager
def get_persistent_data_session():
    session = Session(persistent_data_engine)
    try:
        yield session
    finally:
        session.close()
