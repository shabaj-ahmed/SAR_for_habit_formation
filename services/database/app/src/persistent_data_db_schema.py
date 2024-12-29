from sqlmodel import Field, SQLModel

class ServiceState(SQLModel, table=True):
    """
    Stores the state of the services.
    """
    id: int = Field(default=None, primary_key=True)
    service_name: str
    state_name: str
    state_value: str