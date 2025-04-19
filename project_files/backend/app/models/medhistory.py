from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional, List
import uuid
from .other import FileUpload

if TYPE_CHECKING:
    from .user import User  # Avoid circular import issues

# Medical History model for date and serializers
class MedicalHistoryDates(SQLModel):
    date_consultation: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_consultation')
    def serialize_date_consultation(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Medical History model for database - medical history are records that include things like consultations, imaging and lab tests.
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
    
# Medical Category model for database, example categories include "Consultation", "Imaging", "Lab Test"
class MedicalCategory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medicalhistory: list["MedicalHistory"] = Relationship(back_populates="category")
    
# Medical Subcategory model for database, examples of subcategories include "Cardiology", "Dermatology"
class MedicalSubcategory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medicalhistory: list["MedicalHistory"] = Relationship(back_populates="subcategory")
    
# Lab Subcategory model for database, examples include "Blood Tests", "Urine Tests"
class LabSubcategory(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medicalhistory: list["MedicalHistory"] = Relationship(back_populates="labsubcategory")

# Medical History response model, used for API responses
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
    
# Medical History response model for lab results, used for API responses
class MedicalHistoryResponseLab(SQLModel):
    id: uuid.UUID
    file: bool | None = None
    
# Medical History create model, used for API requests to create a new medical history entry
class MedicalHistoryCreate(MedicalHistoryDates):
    name: str
    doctor_name: str
    place: str | None = None
    notes: str | None = None
    category: str
    subcategory: str | None = None
    labsubcategory: str | None = None
    
# Medical History update model, used for API requests to update an existing medical history entry
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
    
# Medical Category response model, used for API responses
class MedicalCategoryResponse(SQLModel):
    id: uuid.UUID
    name: str
    
# Medical Subcategory response model, used for API responses
class MedicalSubcategoryResponse(SQLModel):
    id: uuid.UUID
    name: str
    
# Lab Subcategory response model, used for API responses
class LabSubcategoryResponse(SQLModel):
    id: uuid.UUID
    name: str
    
# Lab model for date and serializers
class LabDates(SQLModel):
    date_collection: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_collection')
    def serialize_date_collection(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Lab Test model for database - lab test are parent records that only include the name of the test and a code. The actual results are stored in the LabResult model.
class LabTest(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str 
    code: str | None = None
    
    results: List["LabResult"] = Relationship(back_populates="test")
    
# Lab Result model for database - lab result are child records that include the actual results of the lab tests. Each lab test can have multiple results.
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
    
# Lab Result create model, used for API requests to create a new lab result
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
    
# Labs create model, used for API requests to create multiple lab results at once
class LabsCreate(SQLModel):
    lab_tests: List[LabResultCreate]
    date_collection: date
    
    # Relationships
    medicalhistory_id: uuid.UUID
    
# Lab Result Medical History model, used for simplified medical history representation in lab results
class LabResultMedicalHistory(SQLModel):
    id: uuid.UUID
    file: bool
    
# Lab Result response model, used for API responses
class LabResultResponse(LabDates):
    id: uuid.UUID
    value: str
    is_numeric: bool
    unit: str | None = None
    reference_range: str | None = None 
    method: str | None = None
    medicalhistory: MedicalHistoryResponseLab
    
# Lab Test response model, used for API responses
class LabTestResponse(SQLModel):
    id: uuid.UUID
    name: str
    code: str | None = None
    results: List[LabResultResponse]
    
# Lab Result response model for dashboard, used for API responses in the dashboard
class LabResultResponseDashboard(LabDates):
    id: uuid.UUID
    value: str
    is_numeric: bool
    unit: str | None = None
    reference_range: str | None = None 
    method: str | None = None
    medicalhistory: MedicalHistoryResponseLab
    
    # Taken from LabTest to show the name of the test without having to join the table
    name: str
    code: str | None = None