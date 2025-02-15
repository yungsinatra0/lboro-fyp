from sqlmodel import Field, SQLModel, Relationship
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
    vaccines: list["Vaccine"] = Relationship(back_populates="user", cascade_delete=True)
    allergies: list["Allergy"] = Relationship(back_populates="user", cascade_delete=True)
    medications: list["Medication"] = Relationship(back_populates="user", cascade_delete=True)
    healthdata: list["HealthData"] = Relationship(back_populates="user", cascade_delete=True)

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
    
# Vaccine Table model used for table creation
class Vaccine(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    provider: str
    date_received: date
    # Later to add a file field for storing the vaccine certificate
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="vaccines")
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")

# Vaccine response model
class VaccineResponse(SQLModel):
    id: uuid.UUID
    name: str
    provider: str
    date_received: date
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")

# Vaccine create model
class VaccineCreate(SQLModel):
    name: str
    provider: str
    date_received: date
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")

# Vaccine update model
class VaccineUpdate(SQLModel):
    name: str | None = None
    provider: str | None = None
    date_received: date | None = None
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")   

# Allergy Table models used for table creation
class AllergyAllergensLink(SQLModel, table=True):
    allergy_id: uuid.UUID = Field(foreign_key="allergy.id", primary_key=True)
    allergen_id: uuid.UUID = Field(foreign_key="allergens.id", primary_key=True)
    
class AllergyReactionsLink(SQLModel, table=True):
    allergy_id: uuid.UUID = Field(foreign_key="allergy.id", primary_key=True)
    reaction_id: uuid.UUID = Field(foreign_key="reactions.id", primary_key=True)

class Allergy(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_diagnosed: date
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="allergies")
    
    allergens: list["Allergens"] = Relationship(back_populates="allergies", link_model=AllergyAllergensLink)
    reactions: list["Reactions"] = Relationship(back_populates="allergies", link_model=AllergyReactionsLink)
    
    @field_serializer('date_diagnosed')
    def serialize_date_diagnosed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")

# Allergy response model
class AllergyResponse(SQLModel):
    id: uuid.UUID
    date_diagnosed: date
    allergens: list[str]
    reactions: list[str]
    
    @field_serializer('date_diagnosed')
    def serialize_date_diagnosed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Allergy create model
class AllergyCreate(SQLModel):
    date_diagnosed: date
    allergens: list[str]
    reactions: list[str]
    
    @field_serializer('date_diagnosed')
    def serialize_date_diagnosed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")  
    
# Allergy update model
class AllergyUpdate(SQLModel):
    date_diagnosed: date | None = None
    allergens: list[str] | None = None
    reactions: list[str] | None = None
    
    @field_serializer('date_diagnosed')
    def serialize_date_diagnosed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")

class Allergens(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    allergies: list[Allergy] = Relationship(back_populates="allergens", link_model=AllergyAllergensLink)
    
class Reactions(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    allergies: list[Allergy] = Relationship(back_populates="reactions", link_model=AllergyReactionsLink)
    
# Medication Table models used for table creation
class Medication(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    dosage: str
    frequency: str
    date_prescribed: date
    date_ending: date | None = None
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="medications")
    
    form_id : uuid.UUID = Field(foreign_key="medicationform.id")
    form: "MedicationForm" = Relationship(back_populates="medications")
    
    @field_serializer('date_prescribed')
    def serialize_date_prescribed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
    @field_serializer('date_ending')
    def serialize_date_ending(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Medication response model
class MedicationResponse(SQLModel):
    id: uuid.UUID
    name: str
    dosage: str
    frequency: str
    date_prescribed: date
    date_ending: date | None = None
    form: str
    
    @field_serializer('date_prescribed')
    def serialize_date_prescribed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
    @field_serializer('date_ending')
    def serialize_date_ending(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Medication create model
class MedicationCreate(SQLModel):
    name: str
    dosage: str
    frequency: str
    date_prescribed: date
    date_ending: date | None = None
    form: str
    
    @field_serializer('date_prescribed')
    def serialize_date_prescribed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
    @field_serializer('date_ending')
    def serialize_date_ending(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Medication update model
class MedicationUpdate(SQLModel):
    name: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    date_prescribed: date | None = None
    date_ending: date | None = None
    form: str | None = None
    
    @field_serializer('date_prescribed')
    def serialize_date_prescribed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
    @field_serializer('date_ending')
    def serialize_date_ending(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
class MedicationForm(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medications: list[Medication] = Relationship(back_populates="form")
    
# Health data Table models used for table creation    
class HealthData(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    value: float
    date_recorded: date
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="healthdata")
    
    type_id : uuid.UUID = Field(foreign_key="healthdatatype.id")
    type: "HealthDataType" = Relationship(back_populates="healthdata") 
    
    @field_serializer('date_recorded')
    def serialize_date_recorded(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Health data response model
class HealthDataResponse(SQLModel):
    id: uuid.UUID
    name: str
    value: float
    date_recorded: date
    type: str
    
    @field_serializer('date_recorded')
    def serialize_date_recorded(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Health data create model
class HealthDataCreate(SQLModel):
    name: str
    value: float
    date_recorded: date
    type: str
    
    @field_serializer('date_recorded')
    def serialize_date_recorded(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Health data update model
class HealthDataUpdate(SQLModel):
    name: str | None = None
    value: float | None = None
    date_recorded: date | None = None
    type: str | None = None
    
    @field_serializer('date_recorded')
    def serialize_date_recorded(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")

class HealthDataType(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    healthdata: list[HealthData] = Relationship(back_populates="type")