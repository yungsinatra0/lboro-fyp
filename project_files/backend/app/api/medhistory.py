from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session, select
import uuid
import os

from ..models import MedicalHistory, MedicalHistoryResponse, MedicalHistoryCreate, MedicalHistoryUpdate, User, MedicalCategory, MedicalSubcategory, MedicalCategoryResponse, MedicalSubcategoryResponse, LabSubcategory, LabSubcategoryResponse
from ..utils import get_session, validate_session

router = APIRouter()

### Medical History endpoints
# Get all medical history records
@router.get("/me/medicalhistory", response_model=list[MedicalHistoryResponse])
def get_medicalhistory(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    result = []
    
    for history in user.medicalhistory:
        item = {
            "id": history.id,
            "name": history.name,
            "doctor_name": history.doctor_name,
            "place": history.place,
            "notes": history.notes,
            "category": history.category.name,
            "file": history.file,
            "date_consultation": history.date_consultation,
            "date_added": history.date_added
        }
        
        if history.subcategory:
            item["subcategory"] = history.subcategory.name
        if history.labsubcategory:
            item["labsubcategory"] = history.labsubcategory.name
        
        result.append(item)          
            
    return result

# Add a medical history record
@router.post("/me/medicalhistory")
def create_medicalhistory(medhistory: MedicalHistoryCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    category = session.exec(select(MedicalCategory).where(MedicalCategory.name == medhistory.category)).first()
    subcategory = session.exec(select(MedicalSubcategory).where(MedicalSubcategory.name == medhistory.subcategory)).first()
    labsubcategory = session.exec(select(MedicalSubcategory).where(MedicalSubcategory.name == medhistory.labsubcategory)).first()
    
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
        file = new_medicalhistory.file,
        date_consultation = new_medicalhistory.date_consultation,
    )
    
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Medical History record added successfully",
        "medicalhistory": medicalhistory_response
    }
    
# Update a medical history record
@router.patch("/me/medicalhistory/{medhistory_id}")
def update_medicalhistory(medhistory_id: uuid.UUID, medhistory: MedicalHistoryUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medhistory_db = session.get(MedicalHistory, medhistory_id)
    
    if not medhistory_db:
        raise HTTPException(status_code=404, detail="Medical History record not found")
    
    if medhistory_db.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this medical history record")
    
    medhistory_data = medhistory.model_dump(exclude_unset=False)
    
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
    
    
    medhistory_db.sqlmodel_update(medhistory_data)
    session.add(medhistory_db)
    session.commit()
    session.refresh(medhistory_db)
    
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
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Medical History record updated successfully",
        "medicalhistory": medicalhistory_response
    }
    
# Delete a medical history record
@router.delete("/me/medicalhistory/{medhistory_id}")
def delete_medicalhistory(medhistory_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medhistory = session.get(MedicalHistory, medhistory_id)
    
    if not medhistory:
        raise HTTPException(status_code=404, detail="Medical History record not found")
    
    if medhistory.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this medical history record")
    
    if medhistory.file:
        file_path = medhistory.file.file_path
        folder_path = os.path.dirname(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            try:
                os.rmdir(folder_path)
            except PermissionError:
                print("Error deleting folder due to Windows permissions error")
        
    session.delete(medhistory)
    session.commit()
    return {
        "status": status.HTTP_200_OK,
        "message": "Medical History record deleted successfully"
    }

# Get a specific medical history record
@router.get("/me/medicalhistory/{medhistory_id}", response_model=MedicalHistoryResponse)
def get_medicalhistory(medhistory_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medhistory = session.get(MedicalHistory, medhistory_id)
    
    if not medhistory:
        raise HTTPException(status_code=404, detail="Medical History record not found")
    
    if medhistory.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this medical history record")
    
    return medhistory

# Get all medical categories
@router.get("/medicalcategories", response_model=list[MedicalCategoryResponse])
def get_medicalcategories(session: Session = Depends(get_session)):
    return session.exec(select(MedicalCategory)).all()

# Get all medical subcategories
@router.get("/medicalsubcategories", response_model=list[MedicalSubcategoryResponse])
def get_medicalsubcategories(session: Session = Depends(get_session)):
    return session.exec(select(MedicalSubcategory)).all()

# Get all lab subcategories
@router.get("/labsubcategories", response_model=list[LabSubcategoryResponse])
def get_labsubcategories(session: Session = Depends(get_session)):
    return session.exec(select(LabSubcategory)).all()