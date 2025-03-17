from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_serializer
from datetime import date, datetime
import uuid
from typing import Any

User = Any # Using this to avoid Pylance errors

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
    user: "User" = Relationship(back_populates="allergies")
    
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