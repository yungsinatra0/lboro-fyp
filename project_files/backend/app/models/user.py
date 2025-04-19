from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr, field_serializer
from datetime import date, datetime
import uuid
from .vaccine import Vaccine, VaccineResponse
from .allergy import Allergy, AllergyResponse
from .medication import Medication, MedicationResponse
from .healthdata import HealthData, HealthDataResponse
from .medhistory import MedicalHistory, MedicalHistoryResponse, LabResult, LabResultResponseDashboard
from .share import ShareToken

# Base model that contains the field serializer for date formatting to dd-mm-yyyy and the date field itself
class DateFormattingModel(SQLModel):
    dob: date | None = None
    
    @field_serializer('dob')
    def serialize_dob(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

# Session table model used for storing authentication sessions in the database
class AuthSession(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)    
    
# User model for database, contains all user information and relationships to other models
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
    share_tokens: list["ShareToken"] = Relationship(back_populates="user", cascade_delete=True)

# User response model, used for API responses when returning basic user information
class UserResponse(DateFormattingModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    
# User dashboard model, used for API responses to populate user dashboard with all health data
class UserDashboard(SQLModel):
    id: uuid.UUID
    name: str
    vaccines: list["VaccineResponse"]
    allergies: list["AllergyResponse"]
    medications: list["MedicationResponse"]
    vitals: list["HealthDataResponse"]
    medicalhistory: list["MedicalHistoryResponse"]
    labresults: list["LabResultResponseDashboard"]

# User authentication model, used for API requests during login and registration
class UserAuth(DateFormattingModel):
    email: EmailStr
    password: str
    name: str | None = None # Will only be used for registration
    
# User password change model, used for API requests to change a user's password
class UserPasswordChange(SQLModel):
    current_password: str
    new_password: str

# User public model, minimal user data for API responses requiring only user ID
class UserPublic(SQLModel):
    id: uuid.UUID
    
# User update model, used for API requests to update user information
class UserUpdate(DateFormattingModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None