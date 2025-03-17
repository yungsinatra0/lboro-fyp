from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, select
import uuid

from ..models import Allergy, AllergyResponse, AllergyCreate, AllergyUpdate, Allergens, Reactions, Severity, AllergensResponse, ReactionsResponse, SeverityResponse, User
from ..utils import get_session, validate_session

router = APIRouter()

### Allergy endpoints
# Get all allergies
@router.get("/me/allergies", response_model=list[AllergyResponse])
def get_allergies(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    result = []
    for allergy in user.allergies:
        result.append({
            "id": allergy.id,
            "date_diagnosed": allergy.date_diagnosed,
            "allergens": [allergen.name for allergen in allergy.allergens],
            "reactions": [reaction.name for reaction in allergy.reactions],
            "severity": allergy.severity.name,
            "notes": allergy.notes,
            "date_added": allergy.date_added
        })
    
    return result

# Add an allergy
@router.post("/me/allergies")
def add_allergy(allergy: AllergyCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    severity = session.exec(select(Severity).where(Severity.name == allergy.severity)).first()
    
    allergens = []
    for allergen_name in allergy.allergens:
        allergen_db = session.exec(select(Allergens).where(Allergens.name == allergen_name)).first()
        allergens.append(allergen_db)
    
    reactions = []
    for reaction_name in allergy.reactions:
        reaction_db = session.exec(select(Reactions).where(Reactions.name == reaction_name)).first()
        reactions.append(reaction_db)    
    
    new_allergy = Allergy(
        date_diagnosed = allergy.date_diagnosed,
        user = user,
        allergens = allergens,
        reactions = reactions,
        severity = severity,
        notes = allergy.notes,
        )
          
    session.add(new_allergy)
    session.commit()
    session.refresh(new_allergy)
    
    allergy_response = AllergyResponse(
        id = new_allergy.id,
        date_diagnosed = new_allergy.date_diagnosed,
        allergens = [allergen.name for allergen in new_allergy.allergens],
        reactions = [reaction.name for reaction in new_allergy.reactions],
        severity = new_allergy.severity.name,
        notes = new_allergy.notes,
        date_added = new_allergy.date_added
    )
    
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Allergy added successfully",
        "allergy": allergy_response
    }
    
# Delete an allergy
@router.delete("/me/allergies/{allergy_id}")
def delete_allergy(allergy_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    allergy = session.get(Allergy, allergy_id)
    
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")

    if allergy.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this allergy")
    
    session.delete(allergy)
    session.commit()
    return {
        "status": status.HTTP_200_OK,
        "message": "Allergy deleted successfully"
    }

# Get a specific allergy
@router.get("/me/allergies/{allergy_id}", response_model=AllergyResponse)
def get_allergy(allergy_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    allergy = session.get(Allergy, allergy_id)
    
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")
    
    if allergy.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this allergy")
    
    return allergy

# Update an allergy
@router.patch("/me/allergies/{allergy_id}")
def update_allergy(allergy_id: uuid.UUID, allergy_new: AllergyUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    allergy_db = session.get(Allergy, allergy_id)
    
    if not allergy_db:
        raise HTTPException(status_code=404, detail="Allergy not found")
    
    if allergy_db.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this allergy")
    
    allergy_data = allergy_new.model_dump(exclude_unset=True)
    
    if "severity" in allergy_data:
        severity = session.exec(select(Severity).where(Severity.name == allergy_data["severity"])).first()
        allergy_data["severity"] = severity
        
    if "allergens" in allergy_data:
        allergens = []
        for allergen_name in allergy_data["allergens"]:
            allergen_db = session.exec(select(Allergens).where(Allergens.name == allergen_name)).first()
            allergens.append(allergen_db)
        allergy_data["allergens"] = allergens
        
    if "reactions" in allergy_data:
        reactions = []
        for reaction_name in allergy_data["reactions"]:
            reaction_db = session.exec(select(Reactions).where(Reactions.name == reaction_name)).first()
            reactions.append(reaction_db)
        allergy_data["reactions"] = reactions        
    
    allergy_db.sqlmodel_update(allergy_data)
    session.add(allergy_db)
    session.commit()
    session.refresh(allergy_db)
    
    allergy_response = AllergyResponse(
        id = allergy_db.id,
        date_diagnosed = allergy_db.date_diagnosed,
        allergens = [allergen.name for allergen in allergy_db.allergens],
        reactions = [reaction.name for reaction in allergy_db.reactions],
        severity = allergy_db.severity.name,
        notes = allergy_db.notes,
        date_added = allergy_db.date_added
    )
    return {
        "status": status.HTTP_200_OK,
        "message": "Allergy updated successfully",
        'allergy': allergy_response
    }
    
# Get all allergens
@router.get("/allergens", response_model=list[AllergensResponse])
def get_allergens(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    allergens = session.exec(select(Allergens)).all()
    return allergens

# Get all reactions
@router.get("/reactions", response_model=list[ReactionsResponse])
def get_reactions(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    reactions = session.exec(select(Reactions)).all()
    return reactions

# Get all severities
@router.get("/severities", response_model=list[SeverityResponse])
def get_severities(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    severities = session.exec(select(Severity)).all()
    return severities