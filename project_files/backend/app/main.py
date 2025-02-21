from fastapi import FastAPI, Depends, HTTPException, status, Response, Request, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import uuid

# local imports
from database import create_db_and_tables, get_session
from models import *
from auth_utils import verify_hash, create_hash, create_session, validate_session, end_session
from encrypt_utils import *
from file_utils import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try creating the database and tables before starting the API server (will not do anything if they already exist)
    try:
        create_db_and_tables()
        print("Database and tables created successfully")
    except Exception as e:
        print(f"Error creating database and tables: {e}")
    yield
        
app = FastAPI(lifespan=lifespan)

# PUBLIC ROUTES
# Login endpoint
@app.post("/login")
async def login(*, session: Session = Depends(get_session), login_data: UserAuth, response: Response):
    user_db = session.exec(select(User).where(User.email == login_data.email)).first()
    
    # Check if user exists
    if not user_db: 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or user does not exist")
    
    # Check if password is correct
    if not verify_hash(login_data.password, user_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    # Create a session for the user
    session_id = await create_session(user_db.id, session)
    
    # Set the session cookie in the response and send it to the client
    response.set_cookie(
        "session_id",
        str(session_id),
        httponly=True,
        max_age=3600,
        samesite="strict",
        secure=True
    )
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Login successful",
        "user_id": user_db.id
    }    
    

# Register endpoint
@app.post("/register")
def register(*, session: Session = Depends(get_session), register_data: UserAuth):
    
    # Check if email is already registered
    if session.exec(select(User).where(User.email == register_data.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # Try to register the user and add to database
    try:
        user_db = User(
            name = register_data.name,
            email = register_data.email, 
            dob = register_data.dob,
            hashed_password=create_hash(register_data.password))
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
    
        return {
            "status": status.HTTP_201_CREATED,
            "message": "User registered successfully"
            }
    
    # Unlikely to happen, but if an error occurs, rollback the transaction and raise an exception
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred when registering: {e}")


################# PROTECTED ROUTES
# Logout endpoint
@app.post("/logout")
async def logout(response: Response, request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    
    session_id = request.cookies.get("session_id")
    cookie_user_id = session.get(AuthSession, uuid.UUID(session_id)).user_id
    
    if cookie_user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to log out this user")
    
    # Will use the end_session function to end the session in the database
    end_session(request, session) # Need to pass the request and session to the function, otherwise it will not work
    
    # Still need to delete the session cookie from the client
    response.delete_cookie(
        "session_id",
        samesite="strict",
        secure=True,
        httponly=True
        )
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Logout successful"
    }

# Get current user info endpoint
@app.get("/me", response_model=UserPublic)
async def read_users_me(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    return session.get(User, user_id)

# Update user endpoint - TODO: Add authentication to this endpoint   
@app.patch("/update", response_model=UserResponse)
def update_user(*, session: Session = Depends(get_session), user_update: UserUpdate, user_id: uuid.UUID = Depends(validate_session)):
    # Find the user to be updated, if not found, raise an exception
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get the user data to be updated
    user_data = user_update.model_dump(exclude_unset=True)
    extra_data = {}
    
    # If password is being updated, hash it before updating
    if "password" in user_data:
        extra_data["hashed_password"] = create_hash(user_data["password"]) # Do I need to pop this from user_data?
    
    # Update the user data
    try:
        user_db.sqlmodel_update(user_data, update=extra_data)
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        
        return {"message": "User updated successfully"}
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred when updating: {e}")        

# Homepage/dashboard endpoint TODO: Change this to a more useful endpoint
@app.get("/")
async def get_dashboard(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return {
        "message": f"Welcome {user.name}!"
        }

### Vaccine endpoints
# Get all vaccines
@app.get("/me/vaccines", response_model=list[VaccineResponse])
def get_vaccines(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return user.vaccines

# Add a vaccine
@app.post("/me/vaccines")
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
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Vaccine added successfully",
        "vaccine": new_vaccine
    }

# Delete a vaccine
@app.delete("/me/vaccines/{vaccine_id}")
def delete_vaccine(vaccine_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    vaccine = session.get(Vaccine, vaccine_id)
    
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    
    if vaccine.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this vaccine")
    
    session.delete(vaccine)
    session.commit()
    return {
        "status": status.HTTP_200_OK,
        "message": "Vaccine deleted successfully"
    }

# Get a specific vaccine
@app.get("/me/vaccines/{vaccine_id}", response_model=VaccineResponse)
def get_vaccine(vaccine_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    vaccine = session.get(Vaccine, vaccine_id)
    
    if not vaccine:
        raise HTTPException(status_code=404, detail="Vaccine not found")
    
    if vaccine.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this vaccine")
    
    return vaccine


# Update a vaccine
@app.patch("/me/vaccines/{vaccine_id}")
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
    )
    
    return {
        "status": status.HTTP_200_OK,
        "message": "Vaccine updated successfully",
        "vaccine": vaccine_response
    }
    
### Allergy endpoints
# Get all allergies
@app.get("/me/allergies", response_model=list[AllergyResponse])
def get_allergies(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return user.allergies

# Add an allergy
@app.post("/me/allergies")
def add_allergy(allergy: AllergyCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    new_allergy = Allergy(
        date_diagnosed = allergy.date_diagnosed,
        user = user,
        allergens = allergy.allergens,
        reactions = allergy.reactions)
          
    session.add(new_allergy)
    session.commit()
    session.refresh(new_allergy)
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Allergy added successfully"
    }
    
# Delete an allergy
@app.delete("/me/allergies/{allergy_id}")
def delete_allergy(allergy_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    allergy = session.get(Allergy, allergy_id)
    
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")

    if allergy.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this allergy")
    
    session.delete(allergy)
    session.commit()
    return {
        "status": status.HTTP_200_OK,
        "message": "Allergy deleted successfully"
    }

# Get a specific allergy
@app.get("/me/allergies/{allergy_id}", response_model=AllergyResponse)
def get_allergy(allergy_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    allergy = session.get(Allergy, allergy_id)
    
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")
    
    if allergy.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this allergy")
    
    return allergy

# Update an allergy
@app.patch("/me/allergies/{allergy_id}")
def update_allergy(allergy_id: uuid.UUID, allergy_new: AllergyUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    allergy_db = session.get(Allergy, allergy_id)
    
    if not allergy_db:
        raise HTTPException(status_code=404, detail="Allergy not found")
    
    if allergy_db.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this allergy")
    
    allergy_data = allergy_new.model_dump(exclude_unset=True)
    allergy_db.sqlmodel_update(allergy_data)
    session.add(allergy_db)
    session.commit()
    session.refresh(allergy_db)
    return {
        "status": status.HTTP_200_OK,
        "message": "Allergy updated successfully"
    }
    
# Get all allergens
@app.get("/allergens")
def get_allergens(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    allergens = session.exec(select(Allergens)).all()
    return allergens

# Get all reactions
@app.get("/reactions")
def get_reactions(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    reactions = session.exec(select(Reactions)).all()
    return reactions
    
### Health Data endpoints
# Get all health data
@app.get("/me/healthdata", response_model=list[HealthDataResponse])
def get_healthdata(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return user.healthdata

# Add health data
@app.post("/me/healthdata")
def add_healthdata(healthdata: HealthDataCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    new_healthdata = HealthData(
        name = healthdata.name,
        value = healthdata.value,
        date_recorded = healthdata.date_recorded,
        user = user,
        type=healthdata.type)
          
    session.add(new_healthdata)
    session.commit()
    session.refresh(new_healthdata)
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Health data added successfully"
    }
    
# Delete health data
@app.delete("/me/healthdata/{healthdata_id}")
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
@app.get("/me/healthdata/{healthdata_id}", response_model=HealthDataResponse)
def get_healthdata(healthdata_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    healthdata = session.get(HealthData, healthdata_id)
    
    if not healthdata:
        raise HTTPException(status_code=404, detail="Health data not found")
    
    if healthdata.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this health data")
    
    return healthdata

# Update health data
@app.patch("/me/healthdata/{healthdata_id}")
def update_healthdata(healthdata_id: uuid.UUID, healthdata_new: HealthDataUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    healthdata_db = session.get(HealthData, healthdata_id)
    
    if not healthdata_db:
        raise HTTPException(status_code=404, detail="Health data not found")
    
    if healthdata_db.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this health data")
    
    healthdata_data = healthdata_new.model_dump(exclude_unset=True)
    healthdata_db.sqlmodel_update(healthdata_data)
    session.add(healthdata_db)
    session.commit()
    session.refresh(healthdata_db)
    return {
        "status": status.HTTP_200_OK,
        "message": "Health data updated successfully"
    }
    
# Get all health data types
@app.get("/healthdata/types")
def get_healthdata_types(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    healthdata_types = session.exec(select(HealthDataType)).all()
    return healthdata_types

### Medication endpoints
# Get all medications
@app.get("/me/medications", response_model=list[MedicationResponse])
def get_medications(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    # Need to do this because each user has multiple medications, and each medication has a form 
    result = []
    for medication in user.medications:
        med = {
            "id": medication.id,
            "name": medication.name,
            "dosage": medication.dosage,
            "frequency": medication.frequency,
            "date_prescribed": medication.date_prescribed,
            "duration_days": medication.duration_days,
            "form": medication.form.name if medication.form else None,
            "notes": medication.notes      
        }
        result.append(med)
    
    return result

# Add medication
@app.post("/me/medications")
def add_medication(medication: MedicationCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    
    # Find the medication form using the form name
    medication_form = session.exec(select(MedicationForm).where(MedicationForm.name == medication.form)).first()
    
    new_medication = Medication(
        name = medication.name,
        dosage = medication.dosage,
        frequency = medication.frequency,
        date_prescribed = medication.date_prescribed,
        duration_days = medication.duration_days,
        form = medication_form,
        notes = medication.notes,
        user = user)
          
    session.add(new_medication)
    session.commit()
    session.refresh(new_medication)
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Medication added successfully",
        "medication": new_medication
    }
    
# Delete medication
@app.delete("/me/medications/{medication_id}")
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
@app.get("/me/medications/{medication_id}", response_model=MedicationResponse)
def get_medication(medication_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medication = session.get(Medication, medication_id)
    
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    if medication.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this medication")
    
    return medication

# Update medication
@app.patch("/me/medications/{medication_id}")
def update_medication(medication_id: uuid.UUID, medication_new: MedicationUpdate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medication_db = session.get(Medication, medication_id)
    
    if not medication_db:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    if medication_db.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to update this medication")
    
    medication_data = medication_new.model_dump(exclude_unset=True)
    medication_db.sqlmodel_update(medication_data)
    session.add(medication_db)
    session.commit()
    session.refresh(medication_db)
    return {
        "status": status.HTTP_200_OK,
        "message": "Medication updated successfully"
    }
    
# Get all medication forms
@app.get("/medications/forms", response_model=list[MedicationFormResponse])
def get_medication_forms(user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medication_forms = session.exec(select(MedicationForm)).all()
    return medication_forms

### File endpoints
# Upload a file
@app.post("/upload/{record_type}/{record_id}")
async def upload_file(
                file: UploadFile, 
                record_type = str,
                record_id = uuid.UUID,
                user_id: uuid.UUID = Depends(validate_session), 
                session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    
    # Validate the file
    content = await validate_file(file)
    
    record = await get_connected_record(record_type, record_id, user_id, session)
    
    # Generate a UUID for the file
    file_id = uuid.uuid4()
    
    # Encrypt & save the file
    secure_name, file_path = save_file(content, record_id, user_id, file_id, file.filename)
    
    # Create a new FileUpload record
    
    new_file = FileUpload(
        name=secure_name,
        file_path=str(file_path),
        file_type=file.content_type,
        file_size=len(content),
    )
    
    if record_type == "vaccine":
        new_file.vaccine_id = record_id
        new_file.vaccine = record
    # Add more record types here later

    session.add(new_file)
    session.commit()
    session.refresh(new_file)
    
    return {
        "status": status.HTTP_201_CREATED,
        "message": "File uploaded successfully"
    }
    
# Get a file by ID
@app.get("/files/{record_type}/{record_id}")
async def get_file(
    record_type: str,
    record_id: uuid.UUID,
    user_id: User = Depends(validate_session),
    session: Session = Depends(get_session)    
):
    
    print(f"GET request received for vaccine file: {record_id}")
    
    record = await get_connected_record(record_type, record_id, user_id, session)
    
    file_record = None
    
    # Will need to change this to something more elegant later, but for now it works
    if record_type == "vaccine":
        file_record = record.certificate
    
    
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    # I didn't know this, but apparently you need to use a generator function to stream the file content. Thanks random Medium article on the internet!
    async def get_data_from_file():
        with open(file_record.file_path, "rb") as f:
            encrypted_content = f.read()
            
        decrypted_content = decrypt_file(encrypted_content)

        yield decrypted_content
        
    return StreamingResponse(
        content=get_data_from_file(),
        media_type=file_record.file_type,
        status_code=status.HTTP_200_OK,
        headers={"Content-Disposition": f"inline; filename={file_record.name}"}
    )
