from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime
from typing import Any, Optional, List
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
    name: str = Field(unique=True)
    doctor_name: str
    place: str | None = None
    notes: str | None = None
    
    category_id: uuid.UUID = Field(foreign_key="medicalcategory.id")
    category: "MedicalCategory" = Relationship(back_populates="medicalhistory")
    
    subcategory_id: uuid.UUID | None = Field(default=None, foreign_key="medicalsubcategory.id")
    subcategory: Optional["MedicalSubcategory"] = Relationship(back_populates="medicalhistory")
    
    labsubcategory_id: uuid.UUID | None = Field(default=None, foreign_key="labsubcategory.id")
    labsubcategory: Optional["LabSubcategory"] = Relationship(back_populates="medicalhistory")
    
    labresults: List["LabResult"] = Relationship(back_populates="medicalhistory", cascade_delete=True)
    
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
    
class LabSubcategory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medicalhistory: list["MedicalHistory"] = Relationship(back_populates="labsubcategory")

# Medical History response model
class MedicalHistoryResponse(MedicalHistoryDates):
    id: uuid.UUID
    name: str
    doctor_name: str
    place: str | None = None
    notes: str | None = None
    category: str
    subcategory: str | None = None
    labsubcategory: str | None = None
    file: bool | None = None
    
class MedicalHistoryResponseLab(SQLModel):
    id: uuid.UUID
    file: bool | None = None
    
# Medical History create model
class MedicalHistoryCreate(MedicalHistoryDates):
    name: str
    doctor_name: str
    place: str | None = None
    notes: str | None = None
    category: str
    subcategory: str | None = None
    labsubcategory: str | None = None
    
# Medical History update model
class MedicalHistoryUpdate(SQLModel):
    name: str | None = None
    doctor_name: str | None = None
    place: str | None = None
    date_consultation: date | None = None
    notes: str | None = None
    category: str | None = None
    subcategory: str | None = None
    labsubcategory: str | None = None
    
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
    
class LabSubcategoryResponse(SQLModel):
    id: uuid.UUID
    name: str
    
class LabDates(SQLModel):
    date_collection: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_collection')
    def serialize_date_collection(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
class LabTest(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str 
    code: str | None = None
    
    results: List["LabResult"] = Relationship(back_populates="test")
    
class LabResult(LabDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    value: str
    is_numeric: bool
    unit: str | None = None
    reference_range: str | None = None 
    method: str | None = None
    
    # Relationships
    test_id: uuid.UUID = Field(foreign_key="labtest.id")
    test: LabTest = Relationship(back_populates="results")
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="labresults")
    medicalhistory_id: uuid.UUID = Field(foreign_key="medicalhistory.id")
    medicalhistory: MedicalHistory = Relationship(back_populates="labresults")
    
class LabResultCreate(SQLModel):
    # Fields for labtest
    name: str
    code: str | None = None
    
    # Fields for labresult
    value: str
    unit: str | None = None
    is_numeric: bool | None = None
    reference_range: str | None = None 
    method: str | None = None
    
class LabsCreate(SQLModel):
    lab_tests: List[LabResultCreate]
    date_collection: date
    
    # Relationships
    medicalhistory_id: uuid.UUID
    
class LabResultMedicalHistory(SQLModel):
    id: uuid.UUID
    file: bool
    
class LabResultResponse(LabDates):
    id: uuid.UUID
    value: str
    is_numeric: bool
    unit: str | None = None
    reference_range: str | None = None 
    method: str | None = None
    medicalhistory: MedicalHistoryResponseLab
    
class LabTestResponse(SQLModel):
    id: uuid.UUID
    name: str
    code: str | None = None
    results: List[LabResultResponse]
    
class LabResultResponseDashboard(LabDates):
    id: uuid.UUID
    value: str
    is_numeric: bool
    unit: str | None = None
    reference_range: str | None = None 
    method: str | None = None
    medicalhistory: MedicalHistoryResponse
    
    # Taken from LabTest to show the name of the test
    name: str
    code: str | None = None    