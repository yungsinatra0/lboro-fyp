from fastapi import Depends, HTTPException, status, APIRouter, Request
from sqlmodel import Session, select
import uuid

from ..models import User, HealthData, HealthDataResponse, HealthDataType, HealthDataTypeResponse, SimpleHealthDataCreate, BloodPressureCreate, HealthDataUpdate
from ..utils import get_session, validate_session, limiter

router = APIRouter()

### Health Data endpoints
# Get all health data
@router.get("/me/healthdata", response_model=list[HealthDataResponse], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def get_healthdata(request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Get all health data for the logged in user. This will be used to display the health data in the health data page of the application.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Returns:
        result: List of all health data for the logged in user. Each health data entry contains the following fields depending on type:
            - id: UUID: ID of the health data
            - name: str: Name of the health data type
            - unit: str: Unit of measurement
            - value: float: Value of the health data measurement (for regular types)
            - value_systolic: float: Systolic value (for blood pressure)
            - value_diastolic: float: Diastolic value (for blood pressure)
            - date_recorded: str: Date when the measurement was taken
            - notes: str: Notes about the measurement
            - date_added: str: Date when the data was added to the database
            - normal_range: str: Normal range for this health data type
        status: 200 OK: Health data retrieved successfully
    """
    
    # Get user from the database based on the user_id from the session cookie
    user = session.get(User, user_id)
    
    result = []
    
    # Iterate through the user's health data and append to the result list
    # If the health data type is "Tensiune arterială", include systolic and diastolic values
    # Otherwise, include the regular value
    # Also include the normal range for each health data type
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
@router.post("/me/healthdata", status_code=status.HTTP_201_CREATED, response_model=HealthDataResponse)
@limiter.limit("5/minute")
def add_healthdata(request: Request, healthdata: SimpleHealthDataCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Add a simple health data measurement for the logged in user. This will be used to add a new health data entry to the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        healthdata (SimpleHealthDataCreate): Contains health data: name as str, value as float, date_recorded as str, and optional notes as str.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the health data type is not found in the database.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when adding the health data.

    Returns:
        healthdata_response: Object with the following fields:
            - id: UUID: ID of the health data
            - name: str: Name of the health data type
            - unit: str: Unit of measurement
            - value: float: Value of the health data measurement
            - date_recorded: str: Date when the measurement was taken
            - notes: str: Notes about the measurement
            - date_added: str: Date when the data was added to the database
            - normal_range: str: Normal range for this health data type
        status: 201 CREATED: Health data added successfully
    """
    
    # Get user from the database based on the user_id from the session cookie
    user = session.get(User, user_id)
    
    # Get the data type - simple or complex (blood pressure)
    data_type = session.exec(select(HealthDataType).where(HealthDataType.name == healthdata.name)).first()
    
    if not data_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health data type not found")
    
    try:
        new_healthdata = HealthData(
            value = healthdata.value,
            date_recorded = healthdata.date_recorded,
            user = user,
            type = data_type,
            )
        
        if healthdata.notes:
            new_healthdata.notes = healthdata.notes
            
        session.add(new_healthdata)
        session.commit()
        session.refresh(new_healthdata)
        
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
        
        return healthdata_response
    
    except Exception as e:
        session.rollback()
        print(f"Error adding health data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add health data")
    
# Add health data - blood pressure
@router.post("/me/healthdata/bp", status_code=status.HTTP_201_CREATED, response_model=HealthDataResponse)
@limiter.limit("5/minute")
def add_complex_healthdata(request: Request, healthdata: BloodPressureCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Add a blood pressure measurement for the logged in user. This will be used to add a new blood pressure entry to the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        healthdata (BloodPressureCreate): Contains blood pressure data: name as str, value_systolic as float, value_diastolic as float, date_recorded as str, and optional notes as str.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the health data type is not found in the database.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when adding the health data.

    Returns:
        healthdata_response: Object with the following fields:
            - id: UUID: ID of the health data
            - name: str: Name of the health data type
            - unit: str: Unit of measurement
            - value_systolic: float: Systolic blood pressure value
            - value_diastolic: float: Diastolic blood pressure value
            - date_recorded: str: Date when the measurement was taken
            - notes: str: Notes about the measurement
            - date_added: str: Date when the data was added to the database
            - normal_range: str: Normal range for this health data type
        status: 201 CREATED: Health data added successfully
    """
    user = session.get(User, user_id)
    
    # Same as above, but for blood pressure
    data_type = session.exec(select(HealthDataType).where(HealthDataType.name == healthdata.name)).first()
    
    if not data_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health data type not found")
    
    try:
        new_healthdata = HealthData(
            value_systolic = healthdata.value_systolic,
            value_diastolic = healthdata.value_diastolic,
            date_recorded = healthdata.date_recorded,
            user = user,
            type = data_type,
            )
        
        if healthdata.notes:
            new_healthdata.notes = healthdata.notes
                
        session.add(new_healthdata)
        session.commit()
        session.refresh(new_healthdata)
        
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
        return healthdata_response

    except Exception as e:
        session.rollback()
        print(f"Error adding health data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add health data")
    
# Delete health data
@router.delete("/me/healthdata/{healthdata_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def delete_healthdata(request: Request, healthdata_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Delete a health data entry for the logged in user. This will be used to remove a health data entry from the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        healthdata_id (uuid.UUID): ID of the health data entry to delete.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the health data entry is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID of the health data entry.

    Returns:
        "message": Health data deleted successfully
        status: 200 OK: Health data deleted successfully
    """
    
    healthdata = session.get(HealthData, healthdata_id)
    
    if not healthdata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health data not found")

    if healthdata.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this health data")
    
    session.delete(healthdata)
    session.commit()
    return {
        "message": "Health data deleted successfully"
    }

# Update health data
@router.patch("/me/healthdata/{healthdata_id}", response_model=HealthDataResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def update_healthdata(request: Request, healthdata_id: uuid.UUID, healthdata_new: HealthDataUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Update a health data entry for the logged in user. This will be used to modify an existing health data entry in the database.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        healthdata_id (uuid.UUID): ID of the health data entry to update.
        healthdata_new (HealthDataUpdate): Contains updated health data fields. All fields are optional.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the health data entry is not found in the database.
        HTTPException: 403 FORBIDDEN if the user ID from the session does not match the user ID of the health data entry.
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs when updating the health data.

    Returns:
        updated_healthdata: Object with the following fields (fields depend on health data type):
            - id: UUID: ID of the health data
            - name: str: Name of the health data type
            - unit: str: Unit of measurement
            - value: float: Value of the health data measurement (for regular types)
            - value_systolic: float: Systolic value (for blood pressure)
            - value_diastolic: float: Diastolic value (for blood pressure)
            - date_recorded: str: Date when the measurement was taken
            - notes: str: Notes about the measurement
            - date_added: str: Date when the data was added to the database
            - normal_range: str: Normal range for this health data type
        status: 200 OK: Health data updated successfully
    """
    healthdata_db = session.get(HealthData, healthdata_id)
    
    if not healthdata_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health data not found")
    
    if healthdata_db.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to update this health data")
    
    healthdata_data = healthdata_new.model_dump(exclude_unset=True)
    
    if "name" in healthdata_data:
        data_type = session.exec(select(HealthDataType).where(HealthDataType.name == healthdata_data["name"])).first()
        healthdata_data["type"] = data_type
              
    try:
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
        
        return updated_healthdata
    except Exception as e:
        session.rollback()
        print(f"Error updating health data: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update health data")
    
# Get all health data types
@router.get("/healthdata/types", response_model=list[HealthDataTypeResponse], status_code=status.HTTP_200_OK)
def get_healthdata_types(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Retrieve all available health data types from the database.

    This endpoint requires a valid user session but does not use the user_id for filtering,
    as health data types are global and not user-specific.

    Args:
        user_id (uuid.UUID): User ID from the validated session token (unused but required for authorization)
        session (Session): Database session

    Returns:
        list[HealthDataTypeResponse]: List of all health data types with their units and normal ranges
        status: 200 OK: Health data types retrieved successfully
    """
    healthdata_types = session.exec(select(HealthDataType)).all()
    return healthdata_types