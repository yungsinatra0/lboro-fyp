from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session, select
import uuid
import os

from ..models import MedicalHistory, MedicalHistoryResponse, MedicalHistoryCreate, MedicalHistoryUpdate, User, MedicalCategory, MedicalSubcategory, MedicalCategoryResponse, MedicalSubcategoryResponse, LabSubcategory, LabSubcategoryResponse
from ..utils import get_session, validate_session, limiter

router = APIRouter()

### Medical History endpoints
# Get all medical history records
@router.get("/me/medicalhistory", response_model=list[MedicalHistoryResponse], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def get_medicalhistory(request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Get all medical history records for the logged in user. This will be used to display the medical history records in the application.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the user is not found in the database.
        HTTPException: 404 NOT FOUND if no medical history records are found for the user.

    Returns:
        response: List of all medical history records for the logged in user. Each record contains:
            - id: UUID: ID of the medical history record
            - name: str: Name of the medical history record
            - doctor_name: str: Name of the doctor who created the record
            - place: str: Place where the record was created
            - notes: str: Notes about the record
            - category: str: Category of the medical history (Consultație, Imagistică, Laborator)
            - subcategory: str: Subcategory of the medical history (only for Consultație)
            - labsubcategory: str: Lab subcategory (only for Laborator)
            - file: bool: Whether the record has an associated file
            - date_consultation: str: Date when the consultation took place
        status: 200 OK: Medical history records retrieved successfully
    """
    user = session.get(User, user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user.medicalhistory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No medical history records found")
    
    response = []
    
    # Iterate through the user's medical history records and create a response for each one
    for history in user.medicalhistory:
        medhistory_response = MedicalHistoryResponse(
            **history.model_dump(exclude={"user", "labresults", "file", "category", "subcategory", "labsubcategory", "date_consultation"}), # Using model_dump to exclude certain fields which will be added manually because of response model types
            category = history.category.name,
            subcategory = history.subcategory.name if history.subcategory else None,
            labsubcategory = history.labsubcategory.name if history.labsubcategory else None,
            file = True if history.file else False,
            date_consultation = history.date_consultation,
        )
        response.append(medhistory_response)          
            
    return response

# Add a medical history record
@router.post("/me/medicalhistory", status_code=status.HTTP_201_CREATED, response_model=MedicalHistoryResponse)
@limiter.limit("5/minute")
def create_medicalhistory(request: Request, medhistory: MedicalHistoryCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Create a new medical history record for the logged in user. This will be used to add new medical history records to the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        medhistory (MedicalHistoryCreate): Contains medical history data: name, doctor_name, place, notes, category, subcategory, labsubcategory, and date_consultation.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 409 CONFLICT if a medical history record with the same name already exists.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when creating the medical history record.

    Returns:
        medicalhistory_response: Object with the following fields:
            - id: UUID: ID of the medical history record
            - name: str: Name of the medical history record
            - doctor_name: str: Name of the doctor who created the record
            - place: str: Place where the record was created
            - notes: str: Notes about the record
            - category: str: Category of the medical history
            - subcategory: str: Subcategory of the medical history (if applicable)
            - labsubcategory: str: Lab subcategory (if applicable)
            - file: bool: Whether the record has an associated file
            - date_consultation: str: Date when the consultation took place
        status: 201 CREATED: Medical history record created successfully
    """
    user = session.get(User, user_id)
    
    # Get the different categories and subcategories from the database based on the names provided in the request
    category = session.exec(select(MedicalCategory).where(MedicalCategory.name == medhistory.category)).first()
    subcategory = session.exec(select(MedicalSubcategory).where(MedicalSubcategory.name == medhistory.subcategory)).first()
    labsubcategory = session.exec(select(LabSubcategory).where(LabSubcategory.name == medhistory.labsubcategory)).first()
    
    medhistory_db = session.exec(select(MedicalHistory).where(MedicalHistory.name == medhistory.name)).first()
    
    if medhistory_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Medical History record with this name already exists") 
    
    # Create a new medical history record and add it to the database
    try:
        new_medicalhistory = MedicalHistory(
            name = medhistory.name,
            doctor_name = medhistory.doctor_name,
            place = medhistory.place,
            notes = medhistory.notes,
            category = category,
            subcategory = subcategory,
            labsubcategory= labsubcategory,
            user = user,
            date_consultation = medhistory.date_consultation,)
        
        session.add(new_medicalhistory)
        session.commit()
        session.refresh(new_medicalhistory)
        
        medicalhistory_response = MedicalHistoryResponse(
            id = new_medicalhistory.id,
            name = new_medicalhistory.name,
            doctor_name = new_medicalhistory.doctor_name,
            place = new_medicalhistory.place,
            notes = new_medicalhistory.notes,
            category = new_medicalhistory.category.name,
            subcategory = new_medicalhistory.subcategory.name if new_medicalhistory.subcategory else None,
            labsubcategory = new_medicalhistory.labsubcategory.name if new_medicalhistory.labsubcategory else None,
            file = True if new_medicalhistory.file else False,
            date_consultation = new_medicalhistory.date_consultation,
        )
        
        return medicalhistory_response
    
    except Exception as e:
        session.rollback()
        print(f"Error creating medical history record: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the medical history record") from e
    
# Update a medical history record
@router.patch("/me/medicalhistory/{medhistory_id}", status_code=status.HTTP_200_OK, response_model=MedicalHistoryResponse)
@limiter.limit("5/minute")
def update_medicalhistory(request: Request, medhistory_id: uuid.UUID, medhistory: MedicalHistoryUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Update a medical history record for the logged in user. This will be used to modify existing medical history records in the database. All fields are optional, so the user can update only the fields they want to change.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        medhistory_id (uuid.UUID): ID of the medical history record to update.
        medhistory (MedicalHistoryUpdate): Contains updated medical history data with all fields as optional.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the medical history record is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID of the medical history record.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when updating the medical history record.

    Returns:
        medicalhistory_response: Object with the following fields:
            - id: UUID: ID of the medical history record
            - name: str: Name of the medical history record
            - doctor_name: str: Name of the doctor who created the record
            - place: str: Place where the record was created
            - notes: str: Notes about the record
            - category: str: Category of the medical history
            - subcategory: str: Subcategory of the medical history (if applicable)
            - labsubcategory: str: Lab subcategory (if applicable)
            - file: bool: Whether the record has an associated file
            - date_consultation: str: Date when the consultation took place
        status: 200 OK: Medical history record updated successfully
    """
    medhistory_db = session.get(MedicalHistory, medhistory_id)
    
    if not medhistory_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical History record not found")
    
    if medhistory_db.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this medical history record")
    
    # Get the updated data by using model_dump to exclude unset fields (empty fields)
    # This will be used to update the medical history record in the database
    medhistory_data = medhistory.model_dump(exclude_unset=False)
    
    try:
        # Check if user's provided different categories and subcategories exist in the database
        if medhistory_data["category"] is not None:
            category_name = medhistory_data.pop("category")
            category = session.exec(select(MedicalCategory).where(MedicalCategory.name == category_name)).first()
            
            if category:
                medhistory_db.category = category
                
                match category_name:
                    case "Imagistică":
                        medhistory_db.subcategory = None
                        medhistory_db.labsubcategory = None
                    case "Laborator":
                        medhistory_db.subcategory = None
                    case "Consultație":
                        medhistory_db.labsubcategory = None
        
        if medhistory_data["subcategory"] is not None:
            subcategory_name = medhistory_data.pop("subcategory")
            subcategory = session.exec(select(MedicalSubcategory).where(MedicalSubcategory.name == subcategory_name)).first()
            
            if subcategory:
                medhistory_db.subcategory = subcategory
                
        if medhistory_data["labsubcategory"] is not None:
            labsubcategory_name = medhistory_data.pop("labsubcategory")
            labsubcategory = session.exec(select(LabSubcategory).where(LabSubcategory.name == labsubcategory_name)).first()
            
            if labsubcategory:
                medhistory_db.labsubcategory = labsubcategory
        
        # Update the medical history record in the database
        medhistory_db.sqlmodel_update(medhistory_data)
        session.add(medhistory_db)
        session.commit()
        session.refresh(medhistory_db)
        
        # Create a response object to return the updated medical history record
        medicalhistory_response = MedicalHistoryResponse(
            id = medhistory_db.id,
            name = medhistory_db.name,
            doctor_name = medhistory_db.doctor_name,
            place = medhistory_db.place,
            notes = medhistory_db.notes,
            category = medhistory_db.category.name,
            date_consultation = medhistory_db.date_consultation,
        )
        
        if medhistory_db.subcategory:
            medicalhistory_response.subcategory = medhistory_db.subcategory.name
        if medhistory_db.labsubcategory:
            medicalhistory_response.labsubcategory = medhistory_db.labsubcategory.name
        
        return medicalhistory_response
    
    except Exception as e:
        session.rollback()
        print(f"Error updating medical history record: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the medical history record") 
    
# Delete a medical history record
@router.delete("/me/medicalhistory/{medhistory_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def delete_medicalhistory(request: Request, medhistory_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Delete a medical history record for the logged in user. This will also delete any associated files.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        medhistory_id (uuid.UUID): ID of the medical history record to delete.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the medical history record is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID of the medical history record.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when deleting the associated file or folder.

    Returns:
        "message": Medical History record deleted successfully
        status: 200 OK: Medical history record deleted successfully
    """
    medhistory = session.get(MedicalHistory, medhistory_id)
    
    if not medhistory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical History record not found")
    
    if medhistory.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this medical history record")
    
    if medhistory.file:
        file_path = medhistory.file.file_path
        folder_path = os.path.dirname(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            try:
                os.rmdir(folder_path)
            except PermissionError:
                print("Error deleting folder due to Windows permissions error")
                # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while deleting the folder")
        
    session.delete(medhistory)
    session.commit()
    return {
        "message": "Medical History record deleted successfully"
    }

# Get all medical categories
@router.get("/medicalcategories", response_model=list[MedicalCategoryResponse], status_code=status.HTTP_200_OK)
def get_medicalcategories(session: Session = Depends(get_session)):
    """ Retrieve all available medical categories from the database.
    
    This endpoint does not require authentication as it provides reference data for the application.
    Categories typically include "Consultație", "Imagistică", and "Laborator".

    Args:
        session (Session): Database session

    Returns:
        list[MedicalCategoryResponse]: List of all medical categories
        status: 200 OK: Medical categories retrieved successfully
    """
    return session.exec(select(MedicalCategory)).all()

# Get all medical subcategories
@router.get("/medicalsubcategories", response_model=list[MedicalSubcategoryResponse], status_code=status.HTTP_200_OK)
def get_medicalsubcategories(session: Session = Depends(get_session)):
    """ Retrieve all available medical subcategories from the database.
    
    This endpoint does not require authentication as it provides reference data for the application.
    Subcategories are related to consultation types (e.g., "Cardiologie", "Neurologie").

    Args:
        session (Session): Database session

    Returns:
        list[MedicalSubcategoryResponse]: List of all medical subcategories
        status: 200 OK: Medical subcategories retrieved successfully
    """
    return session.exec(select(MedicalSubcategory)).all()

# Get all lab subcategories
@router.get("/labsubcategories", response_model=list[LabSubcategoryResponse], status_code=status.HTTP_200_OK)
def get_labsubcategories(session: Session = Depends(get_session)):
    """ Retrieve all available laboratory subcategories from the database.
    
    This endpoint does not require authentication as it provides reference data for the application.
    Lab subcategories are specialized types of laboratory tests (e.g., "Hematologie", "Biochimie").

    Args:
        session (Session): Database session

    Returns:
        list[LabSubcategoryResponse]: List of all laboratory subcategories
        status: 200 OK: Lab subcategories retrieved successfully
    """
    return session.exec(select(LabSubcategory)).all()