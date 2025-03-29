from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime
import uuid
from typing import Any

User = Any # Using this to avoid Pylance errors

# Health data Table models used for table creation
class HealthDataDates(SQLModel):
    date_recorded: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_recorded')
    def serialize_date_recorded(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
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
    
# Health data response model
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
    
# Health data create model
class SimpleHealthDataCreate(HealthDataDates):
    name: str
    value: float
    notes: str | None = None
    
class BloodPressureCreate(HealthDataDates):
    name: str
    value_systolic: float
    value_diastolic: float
    notes: str | None = None
    
# Health data update model
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

class HealthDataType(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    unit: str
    is_compound: bool = False
    normal_range: str | None = None
    
    healthdata: list[HealthData] = Relationship(back_populates="type")
    
class HealthDataTypeResponse(SQLModel):
    id: uuid.UUID
    name: str
    unit: str
    is_compound: bool
    normal_range: str | None = None