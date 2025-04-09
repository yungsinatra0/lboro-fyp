from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session, select, col
import uuid

from ..models import User, Vaccine, VaccineResponse, Allergy, AllergyResponse, HealthData, HealthDataResponse, Medication, MedicationResponse, UserDashboard, MedicalHistory, MedicalHistoryResponse, LabResultResponseDashboard, LabResult
from ..utils import get_session, validate_session

router = APIRouter()

# Homepage/dashboard endpoint, returns the user object with related data to display in the dashboard
@router.get("/dashboard", response_model=UserDashboard)
async def get_dashboard(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    if user_id != user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this endpoint!")   
    
    newest_vaccines = session.exec(select(Vaccine).where(Vaccine.user_id == user_id).order_by(col(Vaccine.date_added).desc()).limit(5)).all()
    newest_allergies = session.exec(select(Allergy).where(Allergy.user_id == user_id).order_by(col(Allergy.date_added).desc()).limit(5)).all()
    newest_healthdata = session.exec(select(HealthData).where(HealthData.user_id == user_id).order_by(col(HealthData.date_added))).all()
    newest_medications = session.exec(select(Medication).where(Medication.user_id == user_id).order_by(col(Medication.date_added).desc()).limit(5)).all()
    newest_medicalhistory = session.exec(select(MedicalHistory).where(MedicalHistory.user_id == user_id).order_by(col(MedicalHistory.date_added).desc()).limit(5)).all()
    newest_labresults = session.exec(select(LabResult).where(LabResult.user_id == user_id).order_by(col(LabResult.date_added).desc()).limit(5)).all()
    
    vaccines_response = []
    for vaccine in newest_vaccines:
        vaccines_response.append(
            VaccineResponse(
                id = vaccine.id,
                name = vaccine.name,
                provider = vaccine.provider,
                date_received = vaccine.date_received,
                certificate = vaccine.certificate,
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
    
    grouped_healthdata = group_compare_healthdata(newest_healthdata)
        
    healthdata_response = []
    for data in grouped_healthdata:
        healthdata = data["healthdata"]
        response = None
        if healthdata.type.name == "Tensiune arterială":
            response = HealthDataResponse(
                id = healthdata.id,
                name = healthdata.type.name,
                unit = healthdata.type.unit,
                value_systolic = healthdata.value_systolic,
                value_diastolic = healthdata.value_diastolic,
                date_recorded = healthdata.date_recorded,
                notes = healthdata.notes,
                date_added = healthdata.date_added
            )
        else:
            response = HealthDataResponse(
                id = healthdata.id,
                name = healthdata.type.name,
                unit = healthdata.type.unit,
                value = healthdata.value,
                date_recorded = healthdata.date_recorded,
                notes = healthdata.notes,
                date_added = healthdata.date_added
            )
        response.trend = data["trend"]
        healthdata_response.append(response)
        
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
                file = history.file,
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
                medicalhistory = MedicalHistoryResponse(
                    id = labresult.medicalhistory.id,
                    name = labresult.medicalhistory.name,
                    doctor_name = labresult.medicalhistory.doctor_name,
                    place = labresult.medicalhistory.place,
                    notes = labresult.medicalhistory.notes,
                    category = labresult.medicalhistory.category.name,
                    subcategory = labresult.medicalhistory.subcategory.name if labresult.medicalhistory.subcategory else None,
                    labsubcategory = labresult.medicalhistory.labsubcategory.name if labresult.medicalhistory.labsubcategory else None,
                    date_consultation = labresult.medicalhistory.date_consultation,
                    date_added = labresult.medicalhistory.date_added,
                    file = labresult.medicalhistory.file
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

def group_compare_healthdata(healthdata: list[HealthData]):
    grouped_data = {}
    
    for data in healthdata:
        if data.type.name not in grouped_data:
            grouped_data[data.type.name] = []
        grouped_data[data.type.name].append(data)
        
    data_trends = []        
    for key, values in grouped_data.items():
        if not values:
            continue
        
        latest = values[0]
        trend = "stable"
        
        if latest.type.name in ["Înălțime", "Greutate"]:
            trend = "stable"

        elif latest.type.name == "Tensiune arterială":
            range_str = latest.type.normal_range
            if range_str:
                low, high = range_str.split(" - ")
                low_sys = float(low.split("/")[0].strip())
                high_sys = float(high.split(' ')[0].split("/")[0].strip())
                
                if latest.value_systolic > high_sys:
                    trend = "up"
                elif latest.value_systolic < low_sys:
                    trend = "down"
        
        elif latest.type.normal_range:
            range_str = latest.type.normal_range
            try:
                low, high = range_str.split(" - ")
                range_min = float(low.strip())
                range_max = float(high.split(" ")[0].strip())                
                
                if latest.value > range_max:
                    trend = "up"
                elif latest.value < range_min:
                    trend = "down"
            except (ValueError, AttributeError):
                trend = "stable"
            
        data_trends.append({
            "healthdata": latest,
            "trend": trend,
        })
          
    return data_trends