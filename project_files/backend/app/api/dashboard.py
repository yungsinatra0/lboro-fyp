from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session, select, col
import uuid

from ..models import User, Vaccine, VaccineResponse, Allergy, AllergyResponse, HealthData, HealthDataResponse, Medication, MedicationResponse, UserDashboard, MedicalHistory, MedicalHistoryResponse, LabResultResponseDashboard, LabResult, MedicalHistoryResponseLab
from ..utils import get_session, validate_session, limiter

router = APIRouter()

# Homepage/dashboard endpoint, returns the user object with related data to display in the dashboard
@router.get("/dashboard", response_model=UserDashboard, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_dashboard(request: Request, user_id: uuid.UUID = Depends(validate_session),  session: Session = Depends(get_session)):
    """ Dashboard endpoint. Will be used to get all the user-related health data from the database, order it by date added and return it to the client.
    This will be used to display the data in the dashboard page of the application.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID from the database.

    Returns:
        user_dashboard: Object with all the user-related health data to display in the dashboard page of the application.
    """
    
    # Get the session ID from the request cookie and get the user id from the database
    user = session.get(User, user_id)
    
    # Compare the user ID from the session with the user ID from the database
    if user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this endpoint!")   
    
    # Get all the objects in the database, sorted by date added in descending order (newest first)
    newest_vaccines = session.exec(select(Vaccine).where(Vaccine.user_id == user_id).order_by(col(Vaccine.date_added).desc())).all()
    newest_allergies = session.exec(select(Allergy).where(Allergy.user_id == user_id).order_by(col(Allergy.date_added).desc())).all()
    newest_healthdata = session.exec(select(HealthData).where(HealthData.user_id == user_id).order_by(col(HealthData.date_recorded).desc())).all()
    newest_medications = session.exec(select(Medication).where(Medication.user_id == user_id).order_by(col(Medication.date_added).desc())).all()
    newest_medicalhistory = session.exec(select(MedicalHistory).where(MedicalHistory.user_id == user_id).order_by(col(MedicalHistory.date_added).desc())).all()
    newest_labresults = session.exec(select(LabResult).where(LabResult.user_id == user_id).order_by(col(LabResult.date_added).desc())).all()
    
    # Iterate through vaccines to get only the relevant fields - this is because VaccineResponse expects a bool for certificate
    vaccines_response = []
    for vaccine in newest_vaccines:
        vaccines_response.append(
            VaccineResponse(
                id = vaccine.id,
                name = vaccine.name,
                provider = vaccine.provider,
                date_received = vaccine.date_received,
                certificate = True if vaccine.certificate else False,
                date_added = vaccine.date_added 
            ))
    
    # Iterate through allergies to get only allergen names and reactions - this is because AllergyResponse expects a list of str for allergens and reactions
    allergies_response = []
    for allergy in newest_allergies:
        if allergy.severity.name == 'Severă' or allergy.severity.name == 'Moderată':
            allergens = [allergen.name for allergen in allergy.allergens]
            reactions = [reaction.name for reaction in allergy.reactions]
            allergies_response.append(
                AllergyResponse(
                    id = allergy.id,
                    date_diagnosed = allergy.date_diagnosed,
                    allergens = allergens,
                    reactions = reactions,
                    severity = allergy.severity.name,
                    notes = allergy.notes,
                    date_added = allergy.date_added
            ))
    
    # Iterate through medications to get route and form names - same as above, expects str
    medications_response = []
    for medication in newest_medications:
        route = medication.route.name if medication.route else None
        form = medication.form.name if medication.form else None
        medications_response.append(
            MedicationResponse(
                id = medication.id,
                name = medication.name,
                dosage=medication.dosage,
                frequency=medication.frequency,
                date_prescribed=medication.date_prescribed,
                duration_days=medication.duration_days,
                route=route,
                form=form,
                notes=medication.notes,
                date_added=medication.date_added               
        ))
    
    # Iterate through health data to get only the relevant fields, which differ for blood pressure.
    healthdata_response = []
    for data in newest_healthdata:
        healthdata_response.append(HealthDataResponse(
            id = data.id,
            name = data.type.name,
            unit = data.type.unit,
            value = None if data.type.name == "Tensiune arterială" else data.value,
            value_systolic = data.value_systolic if data.type.name == "Tensiune arterială" else None,
            value_diastolic = data.value_diastolic if data.type.name == "Tensiune arterială" else None,
            date_recorded = data.date_recorded,
            notes = data.notes,
            date_added = data.date_added
        ))
    
    # Iterate through medical history to get only the relevant fields - same as above, expects str for category, subcategory and labsubcategory    
    medicalhistory_response = []
    for history in newest_medicalhistory:
        category = history.category.name if history.category else None
        subcategory = history.subcategory.name if history.subcategory else None
        labsubcategory = history.labsubcategory.name if history.labsubcategory else None
        medicalhistory_response.append(
            MedicalHistoryResponse(
                id = history.id,
                name = history.name,
                doctor_name = history.doctor_name,
                place = history.place,
                notes = history.notes,
                category = category,
                subcategory = subcategory,
                labsubcategory= labsubcategory,
                file = True if history.file else False,
                date_consultation = history.date_consultation,
                date_added = history.date_added
            ))
    
    # Iterate through lab results to get only the relevant fields, will also add lab test fields such as name, code
    labresults_response = []
    for labresult in newest_labresults:
        labresults_response.append(
            LabResultResponseDashboard(
                id = labresult.id,
                value = labresult.value,
                is_numeric = labresult.is_numeric,
                unit = labresult.unit,
                reference_range = labresult.reference_range,
                date_collection = labresult.date_collection,
                method = labresult.method,
                name = labresult.test.name,
                code = labresult.test.code,
                medicalhistory = MedicalHistoryResponseLab(
                    id = labresult.medicalhistory.id,
                    file = True if labresult.medicalhistory.file else False,
            )))
    
    # Create the user dashboard object with all the data, which also will be validated by Pydantic to ensure all the fields are correct
    user_dashboard = UserDashboard(
        id = user.id,
        name = user.name,
        vaccines = vaccines_response,
        allergies = allergies_response,
        vitals = healthdata_response,
        medications = medications_response,
        medicalhistory = medicalhistory_response,
        labresults = labresults_response,
    )
    
    return user_dashboard