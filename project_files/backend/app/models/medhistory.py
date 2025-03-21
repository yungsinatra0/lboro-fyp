from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime
from typing import Any, Optional
import uuid
from .other import FileUpload

User = Any # Using this to avoid Pylance errors

# Medical History Table models used for table creation
class MedicalHistoryDates(SQLModel):
    date_consultation: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_consultation')
    def serialize_date_consultation(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
class MedicalHistory(MedicalHistoryDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    doctor_name: str
    place: str | None = None
    notes: str | None = None
    
    category_id: uuid.UUID = Field(foreign_key="medicalcategory.id")
    category: "MedicalCategory" = Relationship(back_populates="medicalhistory")
    
    subcategory_id: uuid.UUID = Field(foreign_key="medicalsubcategory.id")
    subcategory: "MedicalSubcategory" = Relationship(back_populates="medicalhistory")
    
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="medicalhistory")
    
    file: Optional["FileUpload"] = Relationship(back_populates="medicalhistory", cascade_delete=True)
    
class MedicalCategory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medicalhistory: list["MedicalHistory"] = Relationship(back_populates="category")
    
class MedicalSubcategory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medicalhistory: list["MedicalHistory"] = Relationship(back_populates="subcategory")

# Medical History response model
class MedicalHistoryResponse(MedicalHistoryDates):
    id: uuid.UUID
    name: str
    doctor_name: str
    place: str | None = None
    notes: str | None = None
    category: str
    subcategory: str
    file: Optional["FileUpload"]
    
# Medical History create model
class MedicalHistoryCreate(MedicalHistoryDates):
    name: str
    doctor_name: str
    place: str
    notes: str | None = None
    category: str
    subcategory: str
    
# Medical History update model
class MedicalHistoryUpdate(SQLModel):
    name: str | None = None
    doctor_name: str | None = None
    place: str | None = None
    date_consultation: date | None = None
    notes: str | None = None
    category: str | None = None
    subcategory: str | None = None
    
    @field_serializer('date_consultation')
    def serialize_date_consultation(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")
    
class MedicalCategoryResponse(SQLModel):
    id: uuid.UUID
    name: str
    
class MedicalSubcategoryResponse(SQLModel):
    id: uuid.UUID
    name: str