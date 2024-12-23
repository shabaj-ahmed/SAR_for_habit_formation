from sqlmodel import Field, SQLModel

class ServiceState(SQLModel, table=True):
    """
    This class is used to store the state of the services.
    """
    id: int = Field(default=None, primary_key=True)
    service_name: str
    state_name: str
    status: str
    timestamp: str
