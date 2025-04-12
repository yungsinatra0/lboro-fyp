from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime, timedelta
from typing import Any, Optional, List, Dict, ForwardRef
import uuid
import string
import secrets
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # These imports are only used by Pylance/mypy for type checking
    # They don't cause circular imports at runtime
    from .vaccine import VaccineResponse
    from .allergy import AllergyResponse
    from .medication import MedicationResponse
    from .healthdata import HealthDataResponse
    from .medhistory import MedicalHistoryResponse, LabResultResponse, LabTestResponse
    from .user import UserShare, User

# moved here to avoid circular import issues
def generate_random_string(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

class SharedItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    item_type: str  # "vaccine", "allergy", "medication", "healthdata", "medicalhistory", "labresult"
    item_id: uuid.UUID
   
    share_token_id: uuid.UUID = Field(foreign_key="sharetoken.id")
    share_token: "ShareToken" = Relationship(back_populates="shared_items")

class ShareToken(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    share_code: str = Field(index=True, unique=True, default_factory=lambda: generate_random_string(8))
    expiration_time: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    hashed_pin: str
    shared_items: List[SharedItem] = Relationship(back_populates="share_token", cascade_delete=True)
   
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="share_tokens")  # Using Any for now

class CreateShareItem(SQLModel):
    item_type: str  # "vaccine", "allergy", "medication", "healthdata", "medicalhistory", "labresult", "labtest"
    item_id: uuid.UUID

class CreateShareToken(SQLModel):
    expiration_time: datetime
    pin: str
    shared_items: List[CreateShareItem]
   
class ShareTokenResponse(SQLModel):
    id: uuid.UUID
    expiration_time: datetime
    code: str

class ShareCategories(SQLModel):
    vaccines: List["VaccineResponse"] = []
    allergies: List["AllergyResponse"] = []
    medications: List["MedicationResponse"] = []
    healthdata: List["HealthDataResponse"] = []
    medicalhistory: List["MedicalHistoryResponse"] = []
    labtests: List["LabTestResponse"] = []
   
class ShareItemsResponse(SQLModel):
    expiration_time: datetime
    patient: "UserShare"
    items: "ShareCategories"