from fastapi import Depends, HTTPException, status, APIRouter, Request
from sqlmodel import Session, select
import uuid

from ..models import User, Medication, MedicationResponse, MedicationCreate, MedicationRoute, MedicationForm, MedicationRouteResponse, MedicationFormResponse, MedicationUpdate
from ..utils import get_session, validate_session, limiter

router = APIRouter()

### Medication endpoints
# Get all medications
@router.get("/me/medications", response_model=list[MedicationResponse], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def get_medications(request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Get all medications for the logged in user. This will be used to display the medications in the medications page of the application.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Returns:
        result: List of all medications for the logged in user. Each medication contains the following fields:
            - id: UUID: ID of the medication
            - name: str: Name of the medication
            - dosage: str: Dosage amount
            - frequency: str: How often the medication should be taken
            - date_prescribed: str: Date when the medication was prescribed
            - duration_days: int: Number of days the medication should be taken
            - route: str: Administration route (e.g., "Oral", "Intravenous")
            - form: str: Medication form (e.g., "Tablet", "Capsule", "Suspension")
            - notes: str: Notes about the medication
            - date_added: str: Date when the medication was added to the database
            - time_of_day: str: Time of day when the medication should be taken
        status: 200 OK: Medications retrieved successfully
    """
    user = session.get(User, user_id)
    
    if not user.medications:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No medications found for this user")
    
    # Need to do this because each user has multiple medications, and each medication has a route which is a string and not a MedicationRoute object in the response model
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
@router.post("/me/medications", status_code=status.HTTP_201_CREATED, response_model=MedicationResponse)
@limiter.limit("5/minute")
def add_medication(request: Request, medication: MedicationCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Add a medication for the logged in user. This will be used to add a new medication to the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        medication (MedicationCreate): Contains medication data: name, dosage, frequency, date_prescribed, duration_days, route, form, notes, and time_of_day.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the medication route or form is not found in the database.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when adding the medication.

    Returns:
        medication_response: Object with the following fields:
            - id: UUID: ID of the medication
            - name: str: Name of the medication
            - dosage: str: Dosage amount
            - frequency: str: How often the medication should be taken
            - date_prescribed: str: Date when the medication was prescribed
            - duration_days: int: Number of days the medication should be taken
            - route: str: Administration route (e.g., "Oral", "Intravenous")
            - form: str: Medication form (e.g., "Tablet", "Capsule", "Suspension")
            - notes: str: Notes about the medication
            - date_added: str: Date when the medication was added to the database
            - time_of_day: str: Time of day when the medication should be taken
        status: 201 CREATED: Medication added successfully
    """
    user = session.get(User, user_id)
    
    # Find the medication route using the route name
    medication_route = session.exec(select(MedicationRoute).where(MedicationRoute.name == medication.route)).first()
    
    if not medication_route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication route not found")
    
    # Find the medication form using the form name
    medication_form = session.exec(select(MedicationForm).where(MedicationForm.name == medication.form)).first()
    
    if not medication_form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication form not found")
    
    # Create a new medication object
    try:
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
        
        return medication_response
    
    except Exception as e:
        session.rollback()
        print(f"Error adding medication: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while adding the medication") 
        
# Delete medication
@router.delete("/me/medications/{medication_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def delete_medication(request: Request, medication_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Delete a medication for the logged in user. This will be used to remove a medication from the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        medication_id (uuid.UUID): ID of the medication to delete.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the medication is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID of the medication.

    Returns:
        "message": Medication deleted successfully
        status: 200 OK: Medication deleted successfully
    """
    medication = session.get(Medication, medication_id)
    
    if not medication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")

    if medication.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this medication")
    
    session.delete(medication)
    session.commit()
    return {
        "message": "Medication deleted successfully"
    }

# Update medication
@router.patch("/me/medications/{medication_id}", status_code=status.HTTP_200_OK, response_model=MedicationResponse)
@limiter.limit("5/minute")
def update_medication(request: Request, medication_id: uuid.UUID, medication_new: MedicationUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Update a medication for the logged in user. This will be used to modify an existing medication in the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        medication_id (uuid.UUID): ID of the medication to update.
        medication_new (MedicationUpdate): Contains updated medication data with all fields as optional.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the medication is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID of the medication.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when updating the medication.

    Returns:
        medication_response: Object with the following fields:
            - id: UUID: ID of the medication
            - name: str: Name of the medication
            - dosage: str: Dosage amount
            - frequency: str: How often the medication should be taken
            - date_prescribed: str: Date when the medication was prescribed
            - duration_days: int: Number of days the medication should be taken
            - route: str: Administration route (e.g., "Oral", "Intravenous")
            - form: str: Medication form (e.g., "Tablet", "Capsule", "Suspension")
            - notes: str: Notes about the medication
            - date_added: str: Date when the medication was added to the database
            - time_of_day: str: Time of day when the medication should be taken
        status: 200 OK: Medication updated successfully
    """
    medication_db = session.get(Medication, medication_id)
    
    if not medication_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    
    if medication_db.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this medication")
    
    medication_data = medication_new.model_dump(exclude_unset=True)
    
    try:
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
        
        return  medication_response

    except Exception as e:
        session.rollback()
        print(f"Error updating medication: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while updating the medication")
    
# Get all medication routes
@router.get("/medications/routes", response_model=list[MedicationRouteResponse], status_code=status.HTTP_200_OK)
def get_medication_routes(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Retrieve all available medication routes from the database.

    This endpoint requires a valid user session but does not use the user_id for filtering,
    as medication routes are global and not user-specific.

    Args:
        user_id (uuid.UUID): User ID from the validated session token (used for authorization only)
        session (Session): Database session

    Returns:
        list[MedicationRouteResponse]: List of all medication routes (e.g., "Oral", "Intravenous", "Topical")
        status: 200 OK: Medication routes retrieved successfully
    """
    medication_routes = session.exec(select(MedicationRoute)).all()
    return medication_routes

# Get all medication forms
@router.get("/medications/forms", response_model=list[MedicationFormResponse], status_code=status.HTTP_200_OK)
def get_medication_forms(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Retrieve all available medication forms from the database.

    This endpoint requires a valid user session but does not use the user_id for filtering,
    as medication forms are global and not user-specific.

    Args:
        user_id (uuid.UUID): User ID from the validated session token (used for authorization only)
        session (Session): Database session

    Returns:
        list[MedicationFormResponse]: List of all medication forms (e.g., "Tablet", "Capsule", "Liquid")
        status: 200 OK: Medication forms retrieved successfully
    """
    medication_forms = session.exec(select(MedicationForm)).all()
    return medication_forms