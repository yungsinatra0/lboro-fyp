from fastapi import Depends, HTTPException, status, APIRouter, Request
from sqlmodel import Session, select
import uuid

from ..models import LabResult, LabTest, LabsCreate, MedicalHistory, User, LabTestResponse, LabResultResponse, MedicalHistoryResponseLab
from ..utils import get_connected_record, decrypt_file, get_session, validate_session, read_file, extract_with_llm, check_is_numeric, sort_by_date, limiter


router = APIRouter()

# Extract lab tests from uploaded file
@router.post('/labtests/extract/{medicalhistory_id}', status_code=status.HTTP_200_OK) 
@limiter.limit("5/minute")
async def extract_lab_tests(request: Request, medicalhistory_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Extract lab test data from a file associated with a medical history record.
    
    This endpoint uses LLM technology to analyze and extract structured lab test data from medical documents.
    The file is retrieved from the database, decrypted, and processed to identify lab tests, values, and reference ranges.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        medicalhistory_id (uuid.UUID): ID of the medical history record containing the file to analyze.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT_FOUND if the file is not found associated with the medical history record.

    Returns:
        dict: Extracted lab test data in structured format, usually containing:
            - lab_tests: List of detected lab tests with their values, units, and reference ranges
            - date_collection: Detected date when the lab tests were performed
        status: 200 OK: Lab tests extracted successfully
    """
    
    # Get file from database
    record = await get_connected_record("medicalhistory", medicalhistory_id, user_id, session)
    
    uploaded_file = record.file
    if not uploaded_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
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
@router.post('/me/labtests/', status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_lab_tests(request: Request, extraction_result: LabsCreate, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Create lab test records in the database based on extracted data.
    
    This endpoint takes the results from the lab test extraction process and persists them in the database.
    It creates or updates lab test definitions as needed and records the individual test results for the user.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        extraction_result (LabsCreate): Contains extracted lab test data including:
            - medicalhistory_id: UUID of the associated medical history record
            - date_collection: Date when the lab tests were collected
            - lab_tests: List of lab tests with name, code, value, unit, reference range, and method
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT_FOUND if the medical history record is not found.
        HTTPException: 403 FORBIDDEN if the user does not have permission to access the medical history record.
        HTTPException: 500 INTERNAL_SERVER_ERROR if an error occurs during database operations.

    Returns:
        dict: A message indicating successful creation
            - "message": "Lab tests created successfully" 
        status: 201 CREATED: Lab tests created successfully
    """
    medhistory = session.get(MedicalHistory, extraction_result.medicalhistory_id)
    user = session.get(User, user_id)
    
    if not medhistory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical history not found")
    
    if medhistory.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this medical history")
    
    try:
        # Check if extract lab test name already exists, if not create it in the database
        for lab_item in extraction_result.lab_tests:
            lab_test = session.exec(select(LabTest).where(LabTest.name == lab_item.name)).first()
            
            if not lab_test:
                lab_test = LabTest(
                    name = lab_item.name,
                    code = lab_item.code,
                )
                session.add(lab_test)
                session.flush() # Use flush to get the id of the newly created lab_test
            
            # Create the lab result record in the database
            lab_result = LabResult(
                value = lab_item.value,
                is_numeric = check_is_numeric(lab_item.value),
                unit = lab_item.unit,
                reference_range = lab_item.reference_range,
                date_collection = extraction_result.date_collection,
                test = lab_test,
                medicalhistory = medhistory,
                user = user,
                method = lab_item.method
            )
            
            session.add(lab_result)
            session.flush()
            
        session.commit()
        
        return {
            "message": "Lab tests created successfully"
            }
    
    except Exception as e:
        session.rollback()
        print(f"Error creating lab tests: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating lab tests")

# Get all lab tests for the user    
@router.get('/me/labtests/', response_model=list[LabTestResponse], status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_lab_tests(request: Request, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    """ Retrieve all lab tests and their results for the logged in user.
    
    This endpoint fetches all lab test types that have results for the user, along with the
    complete history of results for each test type. Results are organized by test type and
    sorted chronologically, allowing for tracking changes in values over time.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        user_id (uuid.UUID, optional): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session, optional): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Returns:
        list[LabTestResponse]: A list of lab test types, each containing:
            - id: UUID of the lab test type
            - name: Name of the lab test
            - code: Lab test code, if available
            - results: Chronologically sorted list of results for this test type, each containing:
                - id: UUID of the result
                - value: The test result value
                - is_numeric: Boolean indicating if the value is numeric
                - unit: Unit of measurement
                - reference_range: Normal range for this test
                - date_collection: Date when the sample was collected
                - method: Testing method used, if available
                - medicalhistory: Information about the associated medical history record
        status: 200 OK: Lab tests retrieved successfully
    """
    user = session.get(User, user_id)
    
    # Get all lab tests of LabTest and their corresponding results of LabResult for the user
    lab_tests = session.exec(select(LabTest).where(LabTest.results.any(user_id=user.id))).all()
    
    response = []
    
    # Iterate through the lab tests and their results
    for test in lab_tests:
        lab_test = LabTestResponse(
            id = test.id,
            name = test.name,
            code = test.code,
            results = []
        )
        
        for result in test.results:
            lab_result = LabResultResponse(
                id = result.id,
                value = result.value,
                is_numeric = result.is_numeric,
                unit = result.unit,
                reference_range = result.reference_range,
                date_collection = result.date_collection,
                method = result.method,
                medicalhistory = MedicalHistoryResponseLab(
                    id = result.medicalhistory.id,
                    file = True if result.medicalhistory.file else False,
                )
            )
            
            lab_test.results.append(lab_result)
        
        # Sort the results by date_collection
        lab_test.results = sort_by_date(lab_test.results)
        response.append(lab_test)

    return response
