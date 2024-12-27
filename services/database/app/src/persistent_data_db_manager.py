from sqlmodel import Session, select
from .persistent_data_db_schema import ServiceState
from collections import defaultdict
import datetime

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
            self.dispatcher.register_event("update_service_states", self.update_specific_service_states_field)
            self.dispatcher.register_event("service_control_command", self._process_control_command)

    def _process_control_command(self, command):
        """
        Retrieves all service states. Clusters service states by `service_name`.
        """
        print(f"Processing control command: {command}")
        if command == "update_system_state":
            # Step 1: Go through each row of the ServiceStates and get the data
            states = self.session.exec(select(ServiceState)).all()
            clustered_states = defaultdict(list)
            for state in states:
                print(f"Processing state: {state}")
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

    # Read
    def get_all_service_states_fields(self):
        return self.session.get(select(ServiceState)).all()
    
    # I might need to create some shared libraries with enums of something to store all these string values for retriving data
    # Get any field required from the user profile
    def get_specific_service_states(self, state_name: str):
        statement = select(ServiceState).where(ServiceState.state_name == state_name)
        service_states = self.session.exec(statement).one_or_none()
        if not service_states:
            return None
        if hasattr(service_states, state_name):
            return getattr(service_states, "state_value")
        else:
            raise AttributeError(f"{state_name} is not a valid attribute of UserProfile")

    def get_specific_service_state(self, service_name: str):
        """
        Retrieves the state of a specific service.
        """
        return self.session.exec(
            select(ServiceState).where(ServiceState.service_name == service_name)
        ).one_or_none()
    
    # Update
    # UserProfile Operations
    def update_specific_service_states_field(self, payload):
        state_name = payload.get("state_name", "")
        value = payload.get("state_value", "")

        statement = select(ServiceState).where(ServiceState.state_name == state_name)
        service_states = self.session.exec(statement).all()

        print(f"All service states to be updated: {service_states}")

        updated_services = []
        for service_state in service_states:
            setattr(service_state, "state_value", value)  # Update the field in the object
            updated_services.append(service_state)

        self.session.commit()

        for service_state in updated_services:
            self.session.refresh(service_state)
            update_state = {
                "service_name": service_state.service_name,
                "state_name": service_state.state_name,
                "state_value": service_state.state_value
            }
            self.dispatcher.dispatch_event("publish_service_state", update_state)

    def update_service_state(self, service_name: str, state_name: str, state_value):
        """
        Updates or inserts a service state.
        """
        service_state = self.session.exec(
            select(ServiceState).where(ServiceState.service_name == service_name and ServiceState.state_name == state_name)
        ).one_or_none()

        if service_state:
            service_state.state_value = state_value
        else:
            service_state = ServiceState(
                service_name=service_name,
                state_name=state_name,
                state_value=state_value,
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
