from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr, field_serializer
from datetime import date, datetime
import uuid
from typing import Optional

# API Response model
class APIResponse(SQLModel):
    status: int
    message: str
    data: dict | list | None = None

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
    # healthdata: list["HealthDataResponse"]

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
    
# Vaccine model containing dates and serializers
class VaccineDates(SQLModel):
    date_received: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
# Vaccine Table model used for table creation
class Vaccine(VaccineDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    provider: str
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="vaccines")
    
    certificate: Optional["FileUpload"] = Relationship(back_populates="vaccine", cascade_delete=True)

# Vaccine response model
class VaccineResponse(VaccineDates):
    id: uuid.UUID
    name: str
    provider: str
    certificate: Optional["FileUpload"]

# Vaccine create model
class VaccineCreate(VaccineDates):
    name: str
    provider: str

# Vaccine update model
class VaccineUpdate(SQLModel):
    name: str | None = None
    provider: str | None = None
    date_received: date | None = None
    
    @field_serializer('date_received')
    def serialize_date_received(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

# Allergy Table models used for table creation
class AllergyAllergensLink(SQLModel, table=True):
    allergy_id: uuid.UUID = Field(foreign_key="allergy.id", primary_key=True)
    allergen_id: uuid.UUID = Field(foreign_key="allergens.id", primary_key=True)
    
class AllergyReactionsLink(SQLModel, table=True):
    allergy_id: uuid.UUID = Field(foreign_key="allergy.id", primary_key=True)
    reaction_id: uuid.UUID = Field(foreign_key="reactions.id", primary_key=True)

# Allergy model for date and serializers
class AllergyDates(SQLModel):
    date_diagnosed: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_diagnosed')
    def serialize_date_diagnosed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")

class Allergy(AllergyDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    notes: str | None = None
        
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="allergies")
    
    allergens: list["Allergens"] = Relationship(back_populates="allergies", link_model=AllergyAllergensLink)
    reactions: list["Reactions"] = Relationship(back_populates="allergies", link_model=AllergyReactionsLink)
   
    severity_id : uuid.UUID = Field(foreign_key="severity.id")
    severity: "Severity" = Relationship(back_populates="allergies")

# Allergy response model
class AllergyResponse(AllergyDates):
    id: uuid.UUID
    severity: str
    allergens: list[str]
    reactions: list[str]
    notes: str | None = None
    
# Allergy create model
class AllergyCreate(AllergyDates):
    severity: str
    allergens: list[str]
    reactions: list[str]
    notes: str | None = None
    
# Allergy update model
class AllergyUpdate(SQLModel):
    severity: str | None = None
    allergens: list[str] | None = None
    reactions: list[str] | None = None
    notes: str | None = None
    date_diagnosed: date | None = None
    
    @field_serializer('date_diagnosed')
    def serialize_date_diagnosed(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

class Allergens(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    allergies: list[Allergy] = Relationship(back_populates="allergens", link_model=AllergyAllergensLink)
    
class Reactions(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    allergies: list[Allergy] = Relationship(back_populates="reactions", link_model=AllergyReactionsLink)
    
class Severity(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    allergies: list[Allergy] = Relationship(back_populates="severity")
    
class AllergensResponse(SQLModel):
    id: uuid.UUID
    name: str
    
class ReactionsResponse(SQLModel):
    id: uuid.UUID
    name: str
    
class SeverityResponse(SQLModel):
    id: uuid.UUID
    name: str
        
# Medication Table models used for table creation
class MedicationDates(SQLModel):
    date_prescribed: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_prescribed')
    def serialize_date_prescribed(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")

class Medication(MedicationDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    dosage: str
    frequency: str
    time_of_day: str | None = None
    duration_days: int | None = None
    notes: str | None = None
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="medications")
    
    route_id : uuid.UUID = Field(foreign_key="medicationroute.id")
    route: "MedicationRoute" = Relationship(back_populates="medications")
    
    form_id : uuid.UUID = Field(foreign_key="medicationform.id")
    form: "MedicationForm" = Relationship(back_populates="medications")

# Medication response model
class MedicationResponse(MedicationDates):
    id: uuid.UUID
    name: str
    dosage: str
    frequency: str
    time_of_day: str | None = None
    duration_days: int | None = None 
    route: str
    form: str
    notes: str | None = None

# Medication create model
class MedicationCreate(MedicationDates):
    name: str
    dosage: str
    frequency: str
    time_of_day: str | None = None
    duration_days: int | None = None
    route: str
    form: str
    notes: str | None = None
    
# Medication update model
class MedicationUpdate(SQLModel):
    name: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    time_of_day: str | None = None
    date_prescribed: date | None = None
    duration_days: int | None = None
    route: str | None = None
    form: str | None = None
    notes: str | None = None
    
    @field_serializer('date_prescribed')
    def serialize_date_prescribed(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

class MedicationRoute(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medications: list[Medication] = Relationship(back_populates="route")
    
class MedicationRouteResponse(SQLModel):
    id: uuid.UUID
    name: str
    
class MedicationForm(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    
    medications: list[Medication] = Relationship(back_populates="form")
    
class MedicationFormResponse(SQLModel):
    id: uuid.UUID
    name: str
    
# Health data Table models used for table creation
class HealthDataDates(SQLModel):
    date_recorded: date
    date_added: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('date_recorded')
    def serialize_date_recorded(self, value: date) -> str:
        return value.strftime("%d-%m-%Y")
    
class HealthData(HealthDataDates, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    value: float | None = None
    value_systolic: float | None = None
    value_diastolic: float | None = None
    notes: str | None = None
    
    user_id : uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="healthdata")
    
    type_id : uuid.UUID = Field(foreign_key="healthdatatype.id")
    type: "HealthDataType" = Relationship(back_populates="healthdata") 
    
# Health data response model
class HealthDataResponse(HealthDataDates):
    id: uuid.UUID
    name: str
    unit: str
    value: float | None = None
    value_systolic: float | None = None
    value_diastolic: float | None = None
    notes: str | None = None     
    
# Health data create model
class SimpleHealthDataCreate(HealthDataDates):
    name: str
    unit: str
    value: float
    notes: str | None = None
    
class BloodPressureCreate(HealthDataDates):
    name: str
    unit: str
    value_systolic: float
    value_diastolic: float
    notes: str | None = None
    
# Health data update model
class HealthDataUpdate(SQLModel):
    name: str | None = None
    value: float | None = None
    value_systolic: float | None = None
    value_diastolic: float | None = None
    date_recorded: date | None = None
    unit: str | None = None
    notes: str | None = None
    
    @field_serializer('date_recorded')
    def serialize_date_recorded(self, value: date) -> str | None:
        if value is None:
            return None
        return value.strftime("%d-%m-%Y")

class HealthDataType(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    unit: str
    is_compound: bool = False
    
    healthdata: list[HealthData] = Relationship(back_populates="type")
    
class HealthDataTypeResponse(SQLModel):
    id: uuid.UUID
    name: str
    unit: str
    is_compound: bool
    
# File Table models used for table creation
class FileUpload(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    file_path: str
    file_type: str
    file_size: int
    uploaded_at: datetime = Field(default_factory=datetime.now)
    
    vaccine_id : uuid.UUID | None = Field(default=None, foreign_key="vaccine.id")
    vaccine: Optional["Vaccine"] = Relationship(back_populates="certificate")
    
    @field_serializer('uploaded_at')
    def serialize_uploaded_at(self, value: datetime) -> str:
        return value.strftime("%d-%m-%Y %H:%M:%S")