from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr, field_serializer
from datetime import date, datetime
import uuid
from .vaccine import Vaccine, VaccineResponse
from .allergy import Allergy, AllergyResponse
from .medication import Medication, MedicationResponse
from .healthdata import HealthData, HealthDataResponse
from .medhistory import MedicalHistory, MedicalHistoryResponse, LabResult, LabResultResponseDashboard

# Base model that contains the field serializer for date formatting to dd-mm-yyyy and the date field itself
class DateFormattingModel(SQLModel):
    dob: date | None = None
    
    @field_serializer('dob')
    def serialize_dob(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

# Session table model used for storing sessions in the database.
class AuthSession(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)    
    
# User Table model used for table creation, also contains sensitive info like email, password hash and MFA secret
class User(DateFormattingModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str
#   MFA_secret: str | None = None # To be added later
    vaccines: list["Vaccine"] = Relationship(back_populates="user", cascade_delete=True)
    allergies: list["Allergy"] = Relationship(back_populates="user", cascade_delete=True)
    medications: list["Medication"] = Relationship(back_populates="user", cascade_delete=True)
    healthdata: list["HealthData"] = Relationship(back_populates="user", cascade_delete=True)
    medicalhistory: list["MedicalHistory"] = Relationship(back_populates="user", cascade_delete=True)
    labresults: list["LabResult"] = Relationship(back_populates="user", cascade_delete=True)

class UserResponse(DateFormattingModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    
# User object response for dashboard
class UserDashboard(SQLModel):
    id: uuid.UUID
    name: str
    vaccines: list["VaccineResponse"]
    allergies: list["AllergyResponse"]
    medications: list["MedicationResponse"]
    vitals: list["HealthDataResponse"]
    medicalhistory: list["MedicalHistoryResponse"]
    labresults: list["LabResultResponseDashboard"]

# User Data model used for login and registration  
class UserAuth(DateFormattingModel):
    email: EmailStr
    password: str
    name: str | None = None # Will only be used for registration
    
# User data model used for password change
class UserPasswordChange(SQLModel):
    current_password: str
    new_password: str

# User Data model used for most API responses
class UserPublic(SQLModel):
    id: uuid.UUID
    
# User Data model used for updating user info
class UserUpdate(DateFormattingModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None