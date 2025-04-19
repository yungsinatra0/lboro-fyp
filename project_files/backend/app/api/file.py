from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session
import uuid

from ..models import User, FileUpload, FileResponse
from ..utils import validate_file, save_file, get_connected_record, decrypt_file, get_session, validate_session, limiter

router = APIRouter()

### File endpoints
# Upload a file
@router.post("/upload/{record_type}/{record_id}", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def upload_file(
                request: Request,
                file: UploadFile, 
                record_type = str,
                record_id = uuid.UUID,
                user_id: uuid.UUID = Depends(validate_session), 
                session: Session = Depends(get_session)
):
    """ Upload a file and associate it with a specific record (vaccine or medical history). The file will be encrypted and stored securely.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        file (UploadFile): The file to be uploaded.
        record_type (str): Type of record to associate the file with ('vaccine' or 'medicalhistory').
        record_id (uuid.UUID): ID of the record to associate the file with.
        user_id (uuid.UUID): User ID of the logged in user. This is automatically used by the endpoint to get the user ID from the session cookie and validate for database access.
        session (Session): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT FOUND if the associated record is not found.
        HTTPException: 403 FORBIDDEN if the user does not have permission to access the record.
        HTTPException: 500 INTERNAL_SERVER_ERROR if an error occurs during file upload or database operations.

    Returns:
        dict: A message indicating successful upload
            - "message": "File uploaded successfully"
        status: 201 CREATED: File uploaded successfully
    """
    
    # Validate the file
    content = await validate_file(file)
    
    # Get the connected record (e.g., vaccine or medical history)
    record = await get_connected_record(record_type, record_id, user_id, session)
    
    # Generate a UUID for the file, will be used to create the file path
    file_id = uuid.uuid4()
    
    # Encrypt & save the file
    secure_name, file_path = save_file(content, record_id, user_id, file_id, file.filename)
    
    # Create a new FileUpload record
    try:
        new_file = FileUpload(
            id=file_id,
            name=secure_name,
            file_path=str(file_path),
            file_type=file.content_type,
            file_size=len(content),
        )
        
        if record_type == "vaccine":
            new_file.vaccine_id = record_id
            new_file.vaccine = record
        
        elif record_type == "medicalhistory":
            new_file.medhistory_id = record_id
            new_file.medicalhistory = record

        session.add(new_file)
        session.commit()
        session.refresh(new_file)
        
        return {
            "message": "File uploaded successfully"
        }
    except Exception as e:
        session.rollback()
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload file")
    
# Get a file by ID
@router.get("/files/{record_type}/{record_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_file(
    request: Request,
    record_type: str,
    record_id: uuid.UUID,
    user_id: User = Depends(validate_session),
    session: Session = Depends(get_session)    
):
    """ Retrieve a file associated with a specific record (vaccine or medical history). The file will be decrypted before streaming to the client.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        record_type (str): Type of record the file is associated with ('vaccine' or 'medicalhistory').
        record_id (uuid.UUID): ID of the record the file is associated with.
        user_id (User): User object of the logged in user. This is automatically used by the endpoint to validate access rights.
        session (Session): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT_FOUND if the record or associated file is not found.
        HTTPException: 403 FORBIDDEN if the user does not have permission to access this record.

    Returns:
        StreamingResponse: The decrypted file content streamed to the client with appropriate headers for content type and disposition.
        status: 200 OK: File retrieved successfully
    """
    
    # Get the connected record (e.g., vaccine or medical history)
    record = await get_connected_record(record_type, record_id, user_id, session)
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    
    # Will need to change this to something more elegant later, but for now it works
    # Find the file record based on the record type
    if record_type == "vaccine":
        file_record = record.certificate
        
    elif record_type == "medicalhistory":
        file_record = record.file   
        
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    # Stream the file content back to the client while decrypting it
    # This is a generator function that reads the file in chunks and decrypts it
    async def get_data_from_file():
        with open(file_record.file_path, "rb") as f:
            encrypted_content = f.read()
            
        decrypted_content = decrypt_file(encrypted_content)

        yield decrypted_content
    
    # Return the StreamingResponse with the decrypted content and appropriate headers    
    return StreamingResponse(
        content=get_data_from_file(),
        media_type=file_record.file_type,
        headers={"Content-Disposition": f"inline; filename={file_record.name}"}
    )

# Get file metadata
@router.get("/files/{record_type}/{record_id}/metadata", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_file_metadata(
    request: Request,
    record_type: str,
    record_id: uuid.UUID,
    user_id: User = Depends(validate_session),
    session: Session = Depends(get_session)    
):
    """ Retrieve metadata about a file associated with a specific record (vaccine or medical history). 
    This provides information about the file without downloading the actual file content.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        record_type (str): Type of record the file is associated with ('vaccine' or 'medicalhistory').
        record_id (uuid.UUID): ID of the record the file is associated with.
        user_id (User): User object of the logged in user. This is automatically used by the endpoint to validate access rights.
        session (Session): Session is automatically used by the endpoint to access the database by using the SQLModel ORM.

    Raises:
        HTTPException: 404 NOT_FOUND if the record or associated file is not found.
        HTTPException: 403 FORBIDDEN if the user does not have permission to access this record.

    Returns:
        FileResponse: Object containing file metadata with the following fields:
            - id: UUID: ID of the file
            - name: str: Name of the file
            - file_type: str: MIME type of the file
            - file_path: str: Path to the stored file
        status: 200 OK: File metadata retrieved successfully
    """
    
    # Get the connected record (e.g., vaccine or medical history)
    record = await get_connected_record(record_type, record_id, user_id, session)
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    
    if record_type == "vaccine":
        file_record = record.certificate
    elif record_type == "medicalhistory":
        file_record = record.file
        
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    return FileResponse(
        id = file_record.id,
        name = file_record.name,
        file_type = file_record.file_type,
        file_path = file_record.file_path,
    )