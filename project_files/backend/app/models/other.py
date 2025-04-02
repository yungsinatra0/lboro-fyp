from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import datetime
import uuid
from typing import Optional, Any

Vaccine = Any # Using this to avoid Pylance errors
MedicalHistory = Any # Using this to avoid Pylance errors
LabResult = Any # Using this to avoid Pylance errors

# API Response model
class APIResponse(SQLModel):
    status: int
    message: str
    data: dict | list | None = None
    
# File Table models used for table creation
class FileUpload(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    file_path: str
    file_type: str
    file_size: int
    uploaded_at: datetime = Field(default_factory=datetime.now)
    
    vaccine_id : uuid.UUID | None = Field(default=None, foreign_key="vaccine.id", ondelete="CASCADE")
    vaccine: Optional["Vaccine"] = Relationship(back_populates="certificate")
    
    medhistory_id : uuid.UUID | None = Field(default=None, foreign_key="medicalhistory.id", ondelete="CASCADE")
    medicalhistory: Optional["MedicalHistory"] = Relationship(back_populates="file")
    
    labresult_id: uuid.UUID | None = Field(default=None, foreign_key="labresult.id", ondelete="CASCADE")
    labresult: Optional["LabResult"] = Relationship(back_populates="file")
    
    @field_serializer('uploaded_at')
    def serialize_uploaded_at(self, value: datetime) -> str:
        return value.strftime("%d-%m-%Y %H:%M:%S")
    
class FileResponse(SQLModel):
    id: uuid.UUID
    name: str
    file_type: str
    file_path: str