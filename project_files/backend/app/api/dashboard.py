from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session, select, col
import uuid

from ..models import User, Vaccine, VaccineResponse, Allergy, AllergyResponse, HealthData, HealthDataResponse, Medication, MedicationResponse, UserDashboard, MedicalHistory, MedicalHistoryResponse, LabResultResponseDashboard, LabResult, MedicalHistoryResponseLab
from ..utils import get_session, validate_session, group_compare_healthdata

router = APIRouter()

# Homepage/dashboard endpoint, returns the user object with related data to display in the dashboard
@router.get("/dashboard", response_model=UserDashboard)
async def get_dashboard(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    if user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this endpoint!")   
    
    newest_vaccines = session.exec(select(Vaccine).where(Vaccine.user_id == user_id).order_by(col(Vaccine.date_added).desc())).all()
    newest_allergies = session.exec(select(Allergy).where(Allergy.user_id == user_id).order_by(col(Allergy.date_added).desc())).all()
    newest_healthdata = session.exec(select(HealthData).where(HealthData.user_id == user_id).order_by(col(HealthData.date_recorded).desc())).all()
    newest_medications = session.exec(select(Medication).where(Medication.user_id == user_id).order_by(col(Medication.date_added).desc())).all()
    newest_medicalhistory = session.exec(select(MedicalHistory).where(MedicalHistory.user_id == user_id).order_by(col(MedicalHistory.date_added).desc())).all()
    newest_labresults = session.exec(select(LabResult).where(LabResult.user_id == user_id).order_by(col(LabResult.date_added).desc())).all()
    
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