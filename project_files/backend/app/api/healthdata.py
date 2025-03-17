from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, select
import uuid

from ..models import User, HealthData, HealthDataResponse, HealthDataType, HealthDataTypeResponse, SimpleHealthDataCreate, BloodPressureCreate, HealthDataUpdate
from ..utils import get_session, validate_session

router = APIRouter()

### Health Data endpoints
# Get all health data
@router.get("/me/healthdata", response_model=list[HealthDataResponse])
def get_healthdata(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    result = []
    
    for healthdata in user.healthdata:
        if healthdata.type.name == "Tensiune arterială":
            result.append({
                "id": healthdata.id,
                "name": healthdata.type.name,
                "unit": healthdata.type.unit,
                "value_systolic": healthdata.value_systolic,
                "value_diastolic": healthdata.value_diastolic,
                "date_recorded": healthdata.date_recorded,
                "notes": healthdata.notes,
                "date_added": healthdata.date_added,
                "normal_range": healthdata.type.normal_range
            })
        else:
            result.append({
                "id": healthdata.id,
                "name": healthdata.type.name,
                "unit": healthdata.type.unit,
                "value": healthdata.value,
                "date_recorded": healthdata.date_recorded,
                "notes": healthdata.notes,
                "date_added": healthdata.date_added,
                "normal_range": healthdata.type.normal_range
            })
    
    return result

# Add health data - simple
@router.post("/me/healthdata")
def add_healthdata(healthdata: SimpleHealthDataCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    data_type = session.exec(select(HealthDataType).where(HealthDataType.name == healthdata.name)).first()
      
    new_healthdata = HealthData(
        value = healthdata.value,
        date_recorded = healthdata.date_recorded,
        user = user,
        type = data_type,
        )
    
    if healthdata.notes:
        new_healthdata.notes = healthdata.notes
        
    healthdata_response = HealthDataResponse(
        id = new_healthdata.id,
        name = new_healthdata.type.name,
        unit = new_healthdata.type.unit,
        value = new_healthdata.value,
        date_recorded = new_healthdata.date_recorded,
        notes = new_healthdata.notes,
        date_added = new_healthdata.date_added,
        normal_range = new_healthdata.type.normal_range
    )
          
    session.add(new_healthdata)
    session.commit()
    session.refresh(new_healthdata)
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Health data added successfully",
        "healthdata": healthdata_response
    }
    
# Add health data - blood pressure
@router.post("/me/healthdata/bp")
def add_complex_healthdata(healthdata: BloodPressureCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    data_type = session.exec(select(HealthDataType).where(HealthDataType.name == healthdata.name)).first()
    
    new_healthdata = HealthData(
        value_systolic = healthdata.value_systolic,
        value_diastolic = healthdata.value_diastolic,
        date_recorded = healthdata.date_recorded,
        user = user,
        type = data_type,
        )
    
    if healthdata.notes:
        new_healthdata.notes = healthdata.notes
        
    healthdata_response = HealthDataResponse(
        id = new_healthdata.id,
        name = new_healthdata.type.name,
        unit = new_healthdata.type.unit,
        value_systolic = new_healthdata.value_systolic,
        value_diastolic = new_healthdata.value_diastolic,
        date_recorded = new_healthdata.date_recorded,
        notes = new_healthdata.notes,
        date_added = new_healthdata.date_added,
        normal_range = new_healthdata.type.normal_range
    )
          
    session.add(new_healthdata)
    session.commit()
    session.refresh(new_healthdata)
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Health data added successfully",
        "healthdata": healthdata_response
    }
    
# Delete health data
@router.delete("/me/healthdata/{healthdata_id}")
def delete_healthdata(healthdata_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    healthdata = session.get(HealthData, healthdata_id)
    
    if not healthdata:
        raise HTTPException(status_code=404, detail="Health data not found")

    if healthdata.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this health data")
    
    session.delete(healthdata)
    session.commit()
    return {
        "status": status.HTTP_200_OK,
        "message": "Health data deleted successfully"
    }
    
# Get a specific health data
@router.get("/me/healthdata/{healthdata_id}", response_model=HealthDataResponse)
def get_healthdata(healthdata_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    healthdata = session.get(HealthData, healthdata_id)
    
    if not healthdata:
        raise HTTPException(status_code=404, detail="Health data not found")
    
    if healthdata.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this health data")
    
    return healthdata

# Update health data
@router.patch("/me/healthdata/{healthdata_id}")
def update_healthdata(healthdata_id: uuid.UUID, healthdata_new: HealthDataUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    healthdata_db = session.get(HealthData, healthdata_id)
    
    if not healthdata_db:
        raise HTTPException(status_code=404, detail="Health data not found")
    
    if healthdata_db.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this health data")
    
    healthdata_data = healthdata_new.model_dump(exclude_unset=True)
    
    if "name" in healthdata_data:
        data_type = session.exec(select(HealthDataType).where(HealthDataType.name == healthdata_data["name"])).first()
        healthdata_data["type"] = data_type      
    
    healthdata_db.sqlmodel_update(healthdata_data)
    session.add(healthdata_db)
    session.commit()
    session.refresh(healthdata_db)
    
    updated_healthdata = HealthDataResponse(
        id = healthdata_db.id,
        name = healthdata_db.type.name,
        unit = healthdata_db.type.unit,
        normal_range = healthdata_db.type.normal_range,
        date_recorded = healthdata_db.date_recorded,
        notes = healthdata_db.notes,
        date_added = healthdata_db.date_added
    )    
    
    if healthdata_db.value:
        updated_healthdata.value = healthdata_db.value
    elif healthdata_db.value_diastolic and healthdata_db.value_systolic:
        updated_healthdata.value_systolic = healthdata_db.value_systolic
        updated_healthdata.value_diastolic = healthdata_db.value_diastolic
    else: 
        raise HTTPException(status_code=500, detail="An error occurred when updating health data")
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Health data updated successfully",
        "healthdata": updated_healthdata
    }
    
# Get all health data types
@router.get("/healthdata/types", response_model=list[HealthDataTypeResponse])
def get_healthdata_types(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    healthdata_types = session.exec(select(HealthDataType)).all()
    return healthdata_types