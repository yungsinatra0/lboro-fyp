from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import datetime
import uuid
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # Avoid circular import issues
    from .vaccine import Vaccine  # Avoid circular import issues
    from .medhistory import MedicalHistory, LabResult
    
# API Response model for standardized API responses
class APIResponse(SQLModel):
    status: int
    message: str
    data: dict | list | None = None
    
# File Upload model for database, used to store information about uploaded files
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
    
    @field_serializer('uploaded_at')
    def serialize_uploaded_at(self, value: datetime) -> str:
        return value.strftime("%d-%m-%Y %H:%M:%S")
    
# File response model, used for API responses when returning file metadata
class FileResponse(SQLModel):
    id: uuid.UUID
    name: str
    file_type: str
    file_path: str