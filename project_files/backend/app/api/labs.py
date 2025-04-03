from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, select
import uuid

from ..models import LabResult, LabTest, LabSubcategory, LabResultResponse, LabTestResponse, LabResultCreate, LabTestCreate, LabsCreate, MedicalHistory, User
from ..utils import validate_file, save_file, get_connected_record, decrypt_file, get_session, validate_session, read_file, extract_with_llm


router = APIRouter()

# Extract lab tests from uploaded file
@router.post('/labtests/extract/{medicalhistory_id}')
async def extract_lab_tests(medicalhistory_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    
    print("-" * 20, "Extracting lab tests")
    
    # Get file from database
    record = await get_connected_record("medicalhistory", medicalhistory_id, user_id, session)
    
    print("-" * 20, record)
    
    uploaded_file = record.file
    if not uploaded_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    print("-" * 20, record.file)
    
    # Read the encrypted file
    encrypted_file_content = await read_file(uploaded_file.file_path)
    
    # Decrypt the file
    decrypted_file_content = decrypt_file(encrypted_file_content)
    
    # Get the file type
    file_type = uploaded_file.file_type
    
    # Get JSON response from LLM
    response = extract_with_llm(decrypted_file_content, file_type)
    
    return response

# Create the lab test records in the database
@router.post('/me/labtests/')
async def create_lab_tests(extraction_result: LabsCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    medhistory = session.get(MedicalHistory, extraction_result.medicalhistory_id)
    user = session.get(User, user_id)
    
    if not medhistory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical history not found")
    
    if medhistory.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this medical history")
    
    labsubcategory = session.exec(select(LabSubcategory).where(LabSubcategory.name == extraction_result.labsubcategory)).first()
    
    if not labsubcategory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lab subcategory not found")
    
    for lab_item in extraction_result.lab_tests:
        lab_test = session.exec(select(LabTest).where(LabTest.name == lab_item.name)).first()
        
        if not lab_test:
            lab_test = LabTest(
                name = lab_item.name,
                code = lab_item.code,
                labsubcategory = labsubcategory
            )
            session.add(lab_test)
            session.flush()
        
        lab_result = LabResult(
            value = lab_item.value,
            unit = lab_item.unit,
            reference_range = lab_item.reference_range,
            date_collection = extraction_result.date_collection,
            test = lab_test,
            medicalhistory = medhistory,
            user = user
            # method = lab_item.method TODO: Add method and need to change the prompt for that
        )
        
        session.add(lab_result)
        session.flush()
        
        # TODO: Maybe later have an array to store the lab results and return them all at once
        
    session.commit()
    
    return {
        "status": status.HTTP_201_CREATED,
        "message": "Lab tests created successfully"
        }