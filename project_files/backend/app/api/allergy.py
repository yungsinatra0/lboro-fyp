from fastapi import Depends, HTTPException, status, APIRouter, Request
from sqlmodel import Session, select
import uuid

from ..models import Allergy, AllergyResponse, AllergyCreate, AllergyUpdate, Allergens, Reactions, Severity, AllergensResponse, ReactionsResponse, SeverityResponse, User
from ..utils import get_session, validate_session, limiter

router = APIRouter()

### Allergy endpoints
# Get all allergies
@router.get("/me/allergies", response_model=list[AllergyResponse], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def get_allergies(request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Get all allergies for the logged in user. This will be used to display the allergies in the allergies page of the application.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Returns:
        result: List of all allergies for the logged in user. Each allergy contains the following fields:
            - id: UUID: ID of the allergy
            - date_diagnosed: str: Date when the allergy was diagnosed
            - allergens: list[str]: List of allergen names
            - reactions: list[str]: List of reaction names
            - severity: str: Severity of the allergy
            - notes: str: Notes about the allergy
            - date_added: str: Date when the allergy was added to the database
        status: 200 OK: Allergies retrieved successfully
    """
    
    # Get the session ID from the request cookie and get the user id from the database
    user = session.get(User, user_id)
    
    if not user.allergies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No allergies found for this user")
    
    # Get all the allergies for the user
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
@router.post("/me/allergies", status_code=status.HTTP_201_CREATED, response_model=AllergyResponse)
@limiter.limit("5/minute")
def add_allergy(allergy: AllergyCreate, request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Add an allergy for the logged in user. This will be used to add a new allergy to the database.

    Args:
        allergy (AllergyCreate): Contains allergy data: date_diagnosed as str, allergens as list[str], reactions as list[str], severity as str, notes as str.
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the severity, allergens or reactions are not found in the database.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when adding the allergy.

    Returns:
        allergy_response: Object with the following fields:
            - id: UUID: ID of the allergy
            - date_diagnosed: str: Date when the allergy was diagnosed
            - allergens: list[str]: List of allergen names
            - reactions: list[str]: List of reaction names
            - severity: str: Severity of the allergy
            - notes: str: Notes about the allergy
            - date_added: str: Date when the allergy was added to the database
        status: 201 CREATED: Allergy added successfully
    """
    
    # Get the session ID from the request cookie and get the user id from the database
    user = session.get(User, user_id)
    
    # Find the severity from the database from the severity name passed in the request
    severity = session.exec(select(Severity).where(Severity.name == allergy.severity)).first()
    
    if not severity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Severity not found")
    
    # Find the allergens from the database from the allergen names passed in the request. Needs to be a list of allergen names
    allergens = []
    for allergen_name in allergy.allergens:
        allergen_db = session.exec(select(Allergens).where(Allergens.name == allergen_name)).first()
        allergens.append(allergen_db)
        
    if not allergens:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allergens not found")
    
    # Find the reactions from the database from the reaction names passed in the request. Needs to be a list of reaction names
    reactions = []
    for reaction_name in allergy.reactions:
        reaction_db = session.exec(select(Reactions).where(Reactions.name == reaction_name)).first()
        reactions.append(reaction_db)
    
    if not reactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reactions not found")    
    
    
    try: 
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
        
        return allergy_response
    
    except Exception as e:
        session.rollback()
        print(f"Error adding allergy: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when adding the allergy: {e}")
    
# Delete an allergy
@router.delete("/me/allergies/{allergy_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def delete_allergy(allergy_id: uuid.UUID, request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Delete an allergy for the logged in user. This will be used to delete an allergy from the database.

    Args:
        allergy_id (uuid.UUID): ID of the allergy to delete.
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the allergy is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID from the database.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when deleting the allergy.

    Returns:
        "message": Allergy deleted successfully
        status: 200 OK: Allergy deleted successfully
    """
    
    # Find the allergy from the database using the allergy ID passed in the request
    allergy = session.get(Allergy, allergy_id)
    
    if not allergy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allergy not found")

    if allergy.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this allergy")
    
    try:
        session.delete(allergy)
        session.commit()
        
        return {
            "message": "Allergy deleted successfully"
        }
    
    except Exception as e:
        session.rollback()
        print(f"Error deleting allergy: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when deleting the allergy: {e}")

# Update an allergy
@router.patch("/me/allergies/{allergy_id}", status_code=status.HTTP_200_OK, response_model=AllergyResponse)
@limiter.limit("5/minute")
def update_allergy(allergy_id: uuid.UUID, allergy_new: AllergyUpdate, request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Update an allergy for the logged in user. This will be used to update an allergy in the database.

    Args:
        allergy_id (uuid.UUID): ID of the allergy to update.
        allergy_new (AllergyUpdate): Contains allergy data, with all fields as optional: date_diagnosed as str, allergens as list[str], reactions as list[str], severity as str, notes as str.
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the allergy is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID from the database.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when updating the allergy.

    Returns:
        allergy_response: Object with the following fields:
            - id: UUID: ID of the allergy
            - date_diagnosed: str: Date when the allergy was diagnosed
            - allergens: list[str]: List of allergen names
            - reactions: list[str]: List of reaction names
            - severity: str: Severity of the allergy
            - notes: str: Notes about the allergy
            - date_added: str: Date when the allergy was added to the database
        status: 200 OK: Allergy updated successfully
    """
    
    # Find the allergy from the database using the allergy ID passed in the request
    allergy_db = session.get(Allergy, allergy_id)
    
    if not allergy_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Allergy not found")
    
    if allergy_db.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this allergy")
    
    # Use model_dump to get the data from the AllergyUpdate model and exclude unset values, useful when not all fields are provided in the request
    allergy_data = allergy_new.model_dump(exclude_unset=True)
    
    # Check whether the updated fields are not None and update the allergy in the database for those fields which have values
    if allergy_data["severity"] is not None:
        severity_name = allergy_data.pop("severity")
        severity = session.exec(select(Severity).where(Severity.name == severity_name)).first()
        
        if severity:
            allergy_db.severity = severity
    
    
    if allergy_data["allergens"] is not None:
        allergens = []
        for allergen_name in allergy_data["allergens"]:
            allergen_db = session.exec(select(Allergens).where(Allergens.name == allergen_name)).first()
            allergens.append(allergen_db)
            
        if allergens:
            allergy_db.allergens = allergens
        
    
    if allergy_data["reactions"] is not None:
        reactions = []
        for reaction_name in allergy_data["reactions"]:
            reaction_db = session.exec(select(Reactions).where(Reactions.name == reaction_name)).first()
            reactions.append(reaction_db)
            
        if reactions:
            allergy_db.reactions = reactions   
            
    try: 
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
        return allergy_response
        
    except Exception as e:
        session.rollback()
        print(f"Error updating allergy: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when updating the allergy: {e}")
    
# Get all allergens
@router.get("/allergens", response_model=list[AllergensResponse], status_code=status.HTTP_200_OK)
def get_allergens(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """
    Retrieves all allergens from the database.

    This endpoint requires user authentication but doesn't filter results by user.
    The user_id parameter is only used for session validation.

    Args:
        user_id (uuid.UUID): The ID of the authenticated user (used for validation only)
        session (Session): The database session
        
    Returns:
        list[AllergensResponse]: A list of all allergen records
    """
    allergens = session.exec(select(Allergens)).all()
    
    if not allergens:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No allergens found")
    
    return allergens

# Get all reactions
@router.get("/reactions", response_model=list[ReactionsResponse], status_code=status.HTTP_200_OK)
def get_reactions(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """
    Retrieves all reactions from the database.
    
    This endpoint requires user authentication but doesn't filter results by user.
    The user_id parameter is only used for session validation.

    Args:
        user_id (uuid.UUID): The ID of the authenticated user (used for validation only)
        session (Session): The database session

    Returns:
        list[ReactionsResponse]: A list of all reaction records
    """
    
    reactions = session.exec(select(Reactions)).all()
    
    if not reactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No reactions found")
    
    return reactions

# Get all severities
@router.get("/severities", response_model=list[SeverityResponse], status_code=status.HTTP_200_OK)
def get_severities(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """
    Retrieve all severity levels from the database.

    This endpoint requires a valid user session but does not use the user_id for filtering,
    as severity levels are global and not user-specific.

    Args:
        user_id (uuid.UUID): User ID from the validated session token (unused but required for authorization)
        session (Session): Database session
        
    Returns:
        list[SeverityResponse]: List of all severity levels
    """
    severities = session.exec(select(Severity)).all()
    
    if not severities:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No severities found")
    
    return severities