from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime
import uuid
from typing import Optional, Any
from .other import FileUpload

User = Any # Using this to avoid Pylance errors

# Vaccine model containing dates and serializers
class VaccineDates(SQLModel):
    date_received: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Vaccine Table model used for table creation
class Vaccine(VaccineDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    provider: str
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="vaccines")
    
    certificate: Optional["FileUpload"] = Relationship(back_populates="vaccine", cascade_delete=True)

# Vaccine response model
class VaccineResponse(VaccineDates):
    id: uuid.UUID
    name: str
    provider: str
    certificate: bool | None = None

# Vaccine create model
class VaccineCreate(VaccineDates):
    name: str
    provider: str

# Vaccine update model
class VaccineUpdate(SQLModel):
    name: str | None = None
    provider: str | None = None
    date_received: date | None = None
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")