from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, select
import uuid

from ..models import User, Medication, MedicationResponse, MedicationCreate, MedicationRoute, MedicationForm, MedicationRouteResponse, MedicationFormResponse, MedicationUpdate
from ..utils import get_session, validate_session

router = APIRouter()

### Medication endpoints
# Get all medications
@router.get("/me/medications", response_model=list[MedicationResponse])
def get_medications(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    # Need to do this because each user has multiple medications, and each medication has a route 
    result = []
    for medication in user.medications:
        med = {
            "id": medication.id,
            "name": medication.name,
            "dosage": medication.dosage,
            "frequency": medication.frequency,
            "date_prescribed": medication.date_prescribed,
            "duration_days": medication.duration_days,
            "route": medication.route.name if medication.route else None,
            "form": medication.form.name if medication.form else None,
            "notes": medication.notes,
            "date_added": medication.date_added,
            "time_of_day": medication.time_of_day
        }
        result.append(med)
    
    return result

# Add medication
@router.post("/me/medications")
def add_medication(medication: MedicationCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    # Find the medication route using the route name
    medication_route = session.exec(select(MedicationRoute).where(MedicationRoute.name == medication.route)).first()
    
    # Find the medication form using the form name
    medication_form = session.exec(select(MedicationForm).where(MedicationForm.name == medication.form)).first()
    
    new_medication = Medication(
        name = medication.name,
        dosage = medication.dosage,
        frequency = medication.frequency,
        date_prescribed = medication.date_prescribed,
        duration_days = medication.duration_days,
        route = medication_route,
        form = medication_form,
        notes = medication.notes,
        user = user,
        time_of_day=medication.time_of_day
        )
          
    session.add(new_medication)
    session.commit()
    session.refresh(new_medication)
    
    medication_response = MedicationResponse(
        id = new_medication.id,
        name = new_medication.name,
        dosage = new_medication.dosage,
        frequency = new_medication.frequency,
        date_prescribed = new_medication.date_prescribed,
        duration_days = new_medication.duration_days,
        route = new_medication.route.name,
        form = new_medication.form.name,
        notes = new_medication.notes,
        date_added = new_medication.date_added,
        time_of_day = new_medication.time_of_day
    )
    
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Medication added successfully",
        "medication": medication_response
    }
    
# Delete medication
@router.delete("/me/medications/{medication_id}")
def delete_medication(medication_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medication = session.get(Medication, medication_id)
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    if medication.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this medication")
    
    session.delete(medication)
    session.commit()
    return {
        "status": status.HTTP_200_OK,
        "message": "Medication deleted successfully"
    }
    
# Get a specific medication
@router.get("/me/medications/{medication_id}", response_model=MedicationResponse)
def get_medication(medication_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medication = session.get(Medication, medication_id)
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    if medication.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this medication")
    
    return medication

# Update medication
@router.patch("/me/medications/{medication_id}")
def update_medication(medication_id: uuid.UUID, medication_new: MedicationUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medication_db = session.get(Medication, medication_id)
    
    if not medication_db:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    if medication_db.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this medication")
    
    medication_data = medication_new.model_dump(exclude_unset=True)
    
    if medication_data["route"] is not None:
        route_name = medication_data.pop("route")
        route = session.exec(select(MedicationRoute).where(MedicationRoute.name == route_name)).first()
        
        if route:
            medication_db.route = route
    
    if medication_data["form"] is not None:
        form_name = medication_data.pop("form")
        form = session.exec(select(MedicationForm).where(MedicationForm.name == form_name)).first()
        
        if form:
            medication_db.form = form
    
    medication_db.sqlmodel_update(medication_data)
    session.add(medication_db)
    session.commit()
    session.refresh(medication_db)
    
    medication_response = MedicationResponse(
        id = medication_db.id,
        name = medication_db.name,
        dosage = medication_db.dosage,
        frequency = medication_db.frequency,
        date_prescribed = medication_db.date_prescribed,
        duration_days = medication_db.duration_days,
        route = medication_db.route.name,
        form = medication_db.form.name,
        notes = medication_db.notes,
        date_added = medication_db.date_added,
        time_of_day = medication_db.time_of_day
    )
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Medication updated successfully",
        "medication": medication_response
    }
    
# Get all medication routes
@router.get("/medications/routes", response_model=list[MedicationRouteResponse])
def get_medication_routes(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medication_routes = session.exec(select(MedicationRoute)).all()
    return medication_routes

# Get all medication forms
@router.get("/medications/forms", response_model=list[MedicationFormResponse])
def get_medication_forms(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medication_forms = session.exec(select(MedicationForm)).all()
    return medication_forms