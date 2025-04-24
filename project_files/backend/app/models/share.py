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

# Helper function to generate random strings for share codes
def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

# Share Token model for database, used to store information about generated share tokens. Share token is the main object that is used to share health data with other doctors.
class ShareToken(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    share_code: str = Field(index=True, unique=True, default_factory=lambda: generate_random_string(8))
    expiration_time: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    hashed_pin: str
    shared_items: dict = Field(default_factory=dict, sa_column=Column(JSON))
   
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="share_tokens")
    
# Share Token create model, used for API requests to create a new share token
class CreateShareToken(SQLModel):
    token_length: int
    pin: str
    shared_items: dict
   
# Share Token response model, used for API responses when returning token information
class ShareTokenResponse(SQLModel):
    id: uuid.UUID
    expiration_time: datetime
    code: str

# Share Categories model, used to organize the different types of health data that can be shared and displayed in the frontend. Is used by ShareItemsResponse to group the data into categories.
class ShareCategories(SQLModel):
    vaccines: List[VaccineResponse] = []
    allergies: List[AllergyResponse] = []
    medications: List[MedicationResponse] = []
    vitals: List[HealthDataResponse] = []
    medicalhistory: List[MedicalHistoryResponse] = []
    labtests: List[LabTestResponse] = []
   
# Share Items response model, used for API responses when returning shared health data. Main model that is used to return the data to the frontend when fetching shared data.
class ShareItemsResponse(SQLModel):
    expiration_time: datetime
    patient: UserShare
    items: ShareCategories