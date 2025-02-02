from sqlmodel import Field, SQLModel
from pydantic import EmailStr
from datetime import date
import uuid

class Token(SQLModel):
    access_token: str
    token_type: str

# User Table model used for table creation, also contains sensitive info like email, password hash and MFA secret
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    dob: date
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str
#   MFA_secret: str | None = None # To be added later

class UserResponse(SQLModel):
    id: uuid.UUID
    name: str
    dob: date
    email: EmailStr

# User Data model used for login    
class UserAuth(SQLModel):
    email: EmailStr
    password: str
    dob: date | None = None # Will only be used for registration
    name: str | None = None # Will only be used for registration

# User Data model used for most API responses
class UserPublic(SQLModel):
    id: uuid.UUID
    name: str
    
# User Data model used for updating user info
class UserUpdate(SQLModel):
    name: str | None = None
    dob: date | None = None
    email: EmailStr | None = None
    password: str | None = None