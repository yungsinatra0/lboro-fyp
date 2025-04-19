from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime
from typing import TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .user import User  # Avoid circular import issues

# Medication model for date and serializers
class MedicationDates(SQLModel):
    date_prescribed: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_prescribed')
    def serialize_date_prescribed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")

# Medication model for database
class Medication(MedicationDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    dosage: str
    frequency: str
    time_of_day: str | None = None
    duration_days: int | None = None
    notes: str | None = None
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="medications")
    
    route_id : uuid.UUID = Field(foreign_key="medicationroute.id")
    route: "MedicationRoute" = Relationship(back_populates="medications")
    
    form_id : uuid.UUID = Field(foreign_key="medicationform.id")
    form: "MedicationForm" = Relationship(back_populates="medications")

# Medication response model, used for API responses
class MedicationResponse(MedicationDates):
    id: uuid.UUID
    name: str
    dosage: str
    frequency: str
    time_of_day: str | None = None
    duration_days: int | None = None 
    route: str
    form: str
    notes: str | None = None

# Medication create model, used for API requests to create a new medication
class MedicationCreate(MedicationDates):
    name: str
    dosage: str
    frequency: str
    time_of_day: str | None = None
    duration_days: int | None = None
    route: str
    form: str
    notes: str | None = None
    
# Medication update model, used for API requests to update an existing medication
class MedicationUpdate(SQLModel):
    name: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    time_of_day: str | None = None
    date_prescribed: date | None = None
    duration_days: int | None = None
    route: str | None = None
    form: str | None = None
    notes: str | None = None
    
    @field_serializer('date_prescribed')
    def serialize_date_prescribed(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

# Medication Route model for database
class MedicationRoute(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medications: list[Medication] = Relationship(back_populates="route")
    
# Medication Route response model, used for API responses
class MedicationRouteResponse(SQLModel):
    id: uuid.UUID
    name: str
    
# Medication Form model for database
class MedicationForm(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medications: list[Medication] = Relationship(back_populates="form")
    
# Medication Form response model, used for API responses
class MedicationFormResponse(SQLModel):
    id: uuid.UUID
    name: str