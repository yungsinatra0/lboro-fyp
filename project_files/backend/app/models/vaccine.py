from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime
import uuid
from typing import Optional, TYPE_CHECKING
from .other import FileUpload

if TYPE_CHECKING:
    from .user import User  # Avoid circular import issues

# Vaccine model for date and serializers
class VaccineDates(SQLModel):
    date_received: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Vaccine model for database
class Vaccine(VaccineDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    provider: str
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="vaccines")
    
    certificate: Optional["FileUpload"] = Relationship(back_populates="vaccine", cascade_delete=True)

# Vaccine response model, used for API responses
class VaccineResponse(VaccineDates):
    id: uuid.UUID
    name: str
    provider: str
    certificate: bool | None = None

# Vaccine create model, used for API requests to create a new vaccine
class VaccineCreate(VaccineDates):
    name: str
    provider: str

# Vaccine update model, used for API requests to update an existing vaccine
class VaccineUpdate(SQLModel):
    name: str | None = None
    provider: str | None = None
    date_received: date | None = None
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")