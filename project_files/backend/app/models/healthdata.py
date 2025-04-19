from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # Avoid circular import issues

# Health data model for date and serializers
class HealthDataDates(SQLModel):
    date_recorded: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_recorded')
    def serialize_date_recorded(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Health data model for database
class HealthData(HealthDataDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    value: float | None = None
    value_systolic: float | None = None
    value_diastolic: float | None = None
    notes: str | None = None
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="healthdata")
    
    type_id : uuid.UUID = Field(foreign_key="healthdatatype.id")
    type: "HealthDataType" = Relationship(back_populates="healthdata") 
    
# Health data response model, used for API responses
class HealthDataResponse(HealthDataDates):
    id: uuid.UUID
    name: str
    unit: str
    value: float | None = None
    value_systolic: float | None = None
    value_diastolic: float | None = None
    notes: str | None = None
    normal_range: str | None = None
    trend: str | None = None     
    
# Health data create models, used for API requests to create new health data entries. Different models for different types of health data - simple is all that have single values and blood pressure is a compound type with two values.
class SimpleHealthDataCreate(HealthDataDates):
    name: str
    value: float
    notes: str | None = None
    
class BloodPressureCreate(HealthDataDates):
    name: str
    value_systolic: float
    value_diastolic: float
    notes: str | None = None
    
# Health data update model, used for API requests to update an existing health data entry
class HealthDataUpdate(SQLModel):
    name: str | None = None
    value: float | None = None
    value_systolic: float | None = None
    value_diastolic: float | None = None
    date_recorded: date | None = None
    notes: str | None = None
    
    @field_serializer('date_recorded')
    def serialize_date_recorded(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

# Health data type model for database
class HealthDataType(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    unit: str
    is_compound: bool = False
    normal_range: str | None = None
    
    healthdata: list[HealthData] = Relationship(back_populates="type")
    
# Health data type response model, used for API responses
class HealthDataTypeResponse(SQLModel):
    id: uuid.UUID
    name: str
    unit: str
    is_compound: bool
    normal_range: str | None = None