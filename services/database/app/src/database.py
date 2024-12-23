from contextlib import contextmanager
from sqlmodel import create_engine, SQLModel, Session

# Database connection
user_profile_file_name = "services/database/app/database/hri_study.db"
user_profile_url = f"sqlite:///{user_profile_file_name}"
user_profile_engine = create_engine(user_profile_url)

# Initialise user profile database
def init_db():
    SQLModel.metadata.create_all(user_profile_engine)

# Session helper
@contextmanager
def get_user_profile_session():
    session = Session(user_profile_engine)
    try:
        yield session
    finally:
        session.close()

# Service state database connection
service_state_file_name = "services/database/app/database/service_state.db"
service_state_url = f"sqlite:///{service_state_file_name}"
service_state_engine = create_engine(service_state_url)

# Initialise ServiceState database
def init_service_state_db():
    SQLModel.metadata.create_all(service_state_engine)

# Session helper
def get_service_state_session():
    session = Session(user_profile_engine)
    try:
        yield session
    finally:
        session.close()