from sqlmodel import Field, SQLModel
from pydantic import EmailStr, field_serializer
from datetime import date, datetime
import uuid

# Base model that contains the field serializer for date formatting to dd-mm-yyyy and the date field itself
class DateFormattingModel(SQLModel):
    dob: date | None = None
    
    @field_serializer('dob')
    def serialize_dob(self, value: date) -> str:
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

class UserResponse(DateFormattingModel):
    id: uuid.UUID
    name: str
    email: EmailStr

# User Data model used for login    
class UserAuth(DateFormattingModel):
    email: EmailStr
    password: str
    name: str | None = None # Will only be used for registration

# User Data model used for most API responses
class UserPublic(DateFormattingModel):
    id: uuid.UUID
    
# User Data model used for updating user info
class UserUpdate(DateFormattingModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None