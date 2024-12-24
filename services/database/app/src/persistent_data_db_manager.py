from sqlmodel import Session, select
from .persistent_data_db_schema import UserProfile, ServiceState
from collections import defaultdict

class PersistentDataManager:
    def __init__(self, session: Session, dispatcher=None):
        """
        Initialises the ServiceStateManager with a session.
        :param session: An active SQLModel session object.
        """
        self.session = session
        self.dispatcher = dispatcher

        self._register_event_handlers()

    def _register_event_handlers(self):
        """Register event handlers for robot actions."""
        if self.dispatcher:
            self.dispatcher.register_event("update_user_profile", self.update_user_profile_field)
            self.dispatcher.register_event("service_control_command", self._process_control_command)

    def _process_control_command(self, command):
        """
        Retrieves all service states. Clusters service states by `service_name`.
        """
        if command == "update_system_state":
            # Step 1: Go through each row of the ServiceStates and get the data
            states = self.session.exec(select(ServiceState)).all()
            clustered_states = defaultdict(list)
            for state in states:
                clustered_states[state.service_name].append(
                    {
                        "service_name": state.service_name,
                        "state_name": state.state_name,
                        "state_value": state.state_value,
                    }
                )
            # Ensure a default return value
            if not clustered_states:
                print("No service states found.")
                return {}
            
            # Step 2: Publish the clustered states
            self.dispatcher.dispatch_event("publish_service_state", clustered_states)

    # Create if one does not exist
    def create_user_profile(session: Session, profile: UserProfile):
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile

    # Read
    def get_user_profile(session: Session, user_id: int):
        return session.get(UserProfile, user_id)
    
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


    def get_service_state(self, service_name: str):
        """
        Retrieves the state of a specific service.
        """
        return self.session.exec(
            select(ServiceState).where(ServiceState.service_name == service_name)
        ).one_or_none()
    
    #Update
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

    def update_service_state(self, service_name: str, state_name: str, status: str, timestamp: str):
        """
        Updates or inserts a service state.
        """
        service_state = self.session.exec(
            select(ServiceState).where(ServiceState.service_name == service_name)
        ).one_or_none()

        if service_state:
            service_state.state_name = state_name
            service_state.status = status
            service_state.timestamp = timestamp
        else:
            service_state = ServiceState(
                service_name=service_name,
                state_name=state_name,
                status=status,
                timestamp=timestamp,
            )
            self.session.add(service_state)

        self.session.commit()
        self.session.refresh(service_state)
        return service_state

    def delete_service_state(self, service_name: str):
        """
        Deletes the state of a specific service.
        """
        service_state = self.session.exec(
            select(ServiceState).where(ServiceState.service_name == service_name)
        ).one_or_none()
        if service_state:
            self.session.delete(service_state)
            self.session.commit()
