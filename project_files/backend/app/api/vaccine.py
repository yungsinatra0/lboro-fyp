from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session
import uuid
import os

from ..models import Vaccine, VaccineResponse, VaccineCreate, VaccineUpdate, User
from ..utils import get_session, validate_session

router = APIRouter()

### Vaccine endpoints
# Get all vaccines
@router.get("/me/vaccines", response_model=list[VaccineResponse])
def get_vaccines(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return user.vaccines

# Add a vaccine
@router.post("/me/vaccines")
def add_vaccine(vaccine: VaccineCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    new_vaccine = Vaccine(
        name = vaccine.name,
        provider = vaccine.provider,
        date_received = vaccine.date_received,
        user = user)
    
    session.add(new_vaccine)
    session.commit()
    session.refresh(new_vaccine)
    
    vaccine_response = VaccineResponse(
        id = new_vaccine.id,
        name = new_vaccine.name,
        provider = new_vaccine.provider,
        date_received = new_vaccine.date_received,
        certificate = new_vaccine.certificate,
    )
    
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Vaccine added successfully",
        "vaccine": vaccine_response
    }

# Delete a vaccine
@router.delete("/me/vaccines/{vaccine_id}")
def delete_vaccine(vaccine_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    vaccine = session.get(Vaccine, vaccine_id)
    
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    
    if vaccine.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this vaccine")
    
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
        "status": status.HTTP_200_OK,
        "message": "Vaccine deleted successfully"
    }

# Get a specific vaccine
@router.get("/me/vaccines/{vaccine_id}", response_model=VaccineResponse)
def get_vaccine(vaccine_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    vaccine = session.get(Vaccine, vaccine_id)
    
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    
    if vaccine.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this vaccine")
    
    return vaccine


# Update a vaccine
@router.patch("/me/vaccines/{vaccine_id}")
def update_vaccine(vaccine_id: uuid.UUID, vaccine_new: VaccineUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    vaccine_db = session.get(Vaccine, vaccine_id)
    
    if not vaccine_db:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    
    if vaccine_db.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this vaccine")
    
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
        # certificate = vaccine_db.certificate,
        date_added = vaccine_db.date_added
    )
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Vaccine updated successfully",
        "vaccine": vaccine_response
    }