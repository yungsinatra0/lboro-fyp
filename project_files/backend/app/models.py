from sqlmodel import Field, SQLModel
from passlib.hash import bcrypt
from pydantic import EmailStr
from datetime import date

# User model used for table creation, also contains sensitive info like email, password hash and MFA secret
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    dob: date
    email: EmailStr = Field(index=True, unique=True)
    hashed_password: str
#   MFA_secret: str | None = None # To be added later
    
    def verify_hash(self, password: str) -> bool:
        return bcrypt.verify(password, self.hashed_password)
    
    @staticmethod
    def create_hash(password: str) -> str:
        return bcrypt.hash(password)

# User schema used for login    
class UserAuth(SQLModel):
    email: EmailStr
    password: str
    dob: date | None = None # Will only be used for registration
    name: str | None = None # Will only be used for registration

# User schema used for most API responses
class UserResponse(SQLModel):
    id: int
    name: str