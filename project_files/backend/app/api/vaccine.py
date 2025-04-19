from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session
import uuid
import os

from ..models import Vaccine, VaccineResponse, VaccineCreate, VaccineUpdate, User
from ..utils import get_session, validate_session, limiter

router = APIRouter()

### Vaccine endpoints
# Get all vaccines
@router.get("/me/vaccines", response_model=list[VaccineResponse], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def get_vaccines(request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Get all vaccines for the logged in user. This will be used to display the vaccines in the vaccines page of the application.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the user is not found in the database.
        HTTPException: 404 NOT FOUND if no vaccines are found for the user.

    Returns:
        vaccine_responses: List of all vaccines for the logged in user. Each vaccine contains the following fields:
            - id: UUID: ID of the vaccine
            - name: str: Name of the vaccine
            - provider: str: Provider of the vaccine
            - date_received: str: Date when the vaccine was received
            - certificate: bool: Whether the vaccine has an associated certificate
            - date_added: str: Date when the vaccine was added to the database
        status: 200 OK: Vaccines retrieved successfully
    """
    user = session.get(User, user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user.vaccines:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No vaccines found")
    
    vaccine_responses = []
    
    # Iterate through the user's vaccines and create a response for each one
    for vaccine in user.vaccines:
        vaccine_response = VaccineResponse(
            **vaccine.model_dump(exclude={"user", "certificate", "date_received"}), # Will omit the user and certificate fields from the response, which will be added manually due to different field types in the response model
            certificate=True if vaccine.certificate else False,
            date_received=vaccine.date_received
        )
        vaccine_responses.append(vaccine_response)
        
    return vaccine_responses

# Add a vaccine
@router.post("/me/vaccines", status_code=status.HTTP_201_CREATED, response_model=VaccineResponse)
@limiter.limit("5/minute")
def add_vaccine(request: Request, vaccine: VaccineCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Add a vaccine for the logged in user. This will be used to add a new vaccine to the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        vaccine (VaccineCreate): Contains vaccine data: name as str, provider as str, date_received as str.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when adding the vaccine.

    Returns:
        vaccine_response: Object with the following fields:
            - id: UUID: ID of the vaccine
            - name: str: Name of the vaccine
            - provider: str: Provider of the vaccine
            - date_received: str: Date when the vaccine was received
            - certificate: bool: Whether the vaccine has an associated certificate
            - date_added: str: Date when the vaccine was added to the database
        status: 201 CREATED: Vaccine added successfully
    """
    user = session.get(User, user_id)
    
    new_vaccine = Vaccine(
        name = vaccine.name,
        provider = vaccine.provider,
        date_received = vaccine.date_received,
        user = user)
    
    try :
        session.add(new_vaccine)
        session.commit()
        session.refresh(new_vaccine)
        
        vaccine_response = VaccineResponse(
            id = new_vaccine.id,
            name = new_vaccine.name,
            provider = new_vaccine.provider,
            date_received = new_vaccine.date_received,
            certificate = True if new_vaccine.certificate else False,
        )
        
        return  vaccine_response
    
    except Exception as e:
        session.rollback()
        print(f"Error adding vaccine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when adding the vaccine: {e}")

# Delete a vaccine
@router.delete("/me/vaccines/{vaccine_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def delete_vaccine(request: Request, vaccine_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Delete a vaccine for the logged in user. This will also delete any associated certificate file.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        vaccine_id (uuid.UUID): ID of the vaccine to delete.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the vaccine is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID of the vaccine.

    Returns:
        "message": Vaccine deleted successfully
        status: 200 OK: Vaccine deleted successfully
    """
    # Get the vaccine from the database
    vaccine = session.get(Vaccine, vaccine_id)
    
    if not vaccine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine not found")
    
    if vaccine.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this vaccine")
    
    # Delete the file associated with the vaccine
    file_record = vaccine.certificate
    if file_record:
        # Delete file from the file system
        file_path = file_record.file_path
        if os.path.exists(file_path):
            folder_path = os.path.dirname(file_path)
            os.remove(file_path)
            try:
                os.rmdir(folder_path)
            except PermissionError:
                print("Error deleting folder due to Windows permissions error")
                  
        session.delete(file_record)
    
    session.delete(vaccine)
    session.commit()
    return {
        "message": "Vaccine deleted successfully"
    }

# Update a vaccine
@router.patch("/me/vaccines/{vaccine_id}", status_code=status.HTTP_200_OK, response_model=VaccineResponse)
@limiter.limit("5/minute")
def update_vaccine(request: Request, vaccine_id: uuid.UUID, vaccine_new: VaccineUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Update a vaccine for the logged in user. This will be used to modify an existing vaccine in the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        vaccine_id (uuid.UUID): ID of the vaccine to update.
        vaccine_new (VaccineUpdate): Contains updated vaccine data with all fields as optional: name as str, provider as str, date_received as str.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the vaccine is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID of the vaccine.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when updating the vaccine.

    Returns:
        vaccine_response: Object with the following fields:
            - id: UUID: ID of the vaccine
            - name: str: Name of the vaccine
            - provider: str: Provider of the vaccine
            - date_received: str: Date when the vaccine was received
            - date_added: str: Date when the vaccine was added to the database
        status: 200 OK: Vaccine updated successfully
    """
    vaccine_db = session.get(Vaccine, vaccine_id)
    
    if not vaccine_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine not found")
    
    if vaccine_db.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this vaccine")
    
    try:
        vaccine_data = vaccine_new.model_dump(exclude_unset=True)
        vaccine_db.sqlmodel_update(vaccine_data)
        session.add(vaccine_db)
        session.commit()
        session.refresh(vaccine_db)
        
        vaccine_response = VaccineResponse(
            id = vaccine_db.id,
            name = vaccine_db.name,
            provider = vaccine_db.provider,
            date_received = vaccine_db.date_received,
            # certificate = vaccine_db.certificate, # This is a file object, so we need to handle it differently
            date_added = vaccine_db.date_added
        )
        
        return  vaccine_response
    
    except Exception as e:
        session.rollback()
        print(f"Error updating vaccine: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when updating the vaccine: {e}")