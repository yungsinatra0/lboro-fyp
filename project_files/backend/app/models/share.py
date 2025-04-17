from sqlmodel import Field, SQLModel, Relationship, Column, JSON
from pydantic import field_serializer
from datetime import date, datetime, timedelta
from typing import List, TYPE_CHECKING
import uuid
import string
import secrets
from .vaccine import VaccineResponse
from .allergy import AllergyResponse
from .medication import MedicationResponse
from .healthdata import HealthDataResponse
from .medhistory import MedicalHistoryResponse, LabTestResponse
from .share_user import UserShare

if TYPE_CHECKING:
    from .user import User  # Avoid circular import issues

# moved here to avoid circular import issues
def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

class ShareToken(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    share_code: str = Field(index=True, unique=True, default_factory=lambda: generate_random_string(8))
    expiration_time: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    hashed_pin: str
    shared_items: dict = Field(default_factory=dict, sa_column=Column(JSON))
   
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="share_tokens")  # Using Any for now
    
class CreateShareToken(SQLModel):
    token_length: int
    pin: str
    shared_items: dict
   
class ShareTokenResponse(SQLModel):
    id: uuid.UUID
    expiration_time: datetime
    code: str

class ShareCategories(SQLModel):
    vaccines: List[VaccineResponse] = []
    allergies: List[AllergyResponse] = []
    medications: List[MedicationResponse] = []
    healthdata: List[HealthDataResponse] = []
    medicalhistory: List[MedicalHistoryResponse] = []
    labtests: List[LabTestResponse] = []
   
class ShareItemsResponse(SQLModel):
    expiration_time: datetime
    patient: UserShare
    items: ShareCategories