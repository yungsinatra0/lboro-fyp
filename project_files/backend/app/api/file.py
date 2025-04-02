from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlmodel import Session
import uuid

from ..models import User, FileUpload, FileResponse
from ..utils import validate_file, save_file, get_connected_record, decrypt_file, get_session, validate_session

router = APIRouter()

### File endpoints
# Upload a file
@router.post("/upload/{record_type}/{record_id}")
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
    
    elif record_type == "medicalhistory":
        new_file.medhistory_id = record_id
        new_file.medicalhistory = record

    session.add(new_file)
    session.commit()
    session.refresh(new_file)
    
    return {
        "status": status.HTTP_201_CREATED,
        "message": "File uploaded successfully"
    }
    
# Get a file by ID
@router.get("/files/{record_type}/{record_id}")
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
        
    elif record_type == "medicalhistory":
        file_record = record.file   
    
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

# Get file metadata
@router.get("/files/{record_type}/{record_id}/metadata")
async def get_file_metadata(
    record_type: str,
    record_id: uuid.UUID,
    user_id: User = Depends(validate_session),
    session: Session = Depends(get_session)    
):
    
    record = await get_connected_record(record_type, record_id, user_id, session)
    
    if record_type == "vaccine":
        file_record = record.certificate
    elif record_type == "medicalhistory":
        file_record = record.file
    
    return FileResponse(
        id = file_record.id,
        name = file_record.name,
        file_type = file_record.file_type,
        file_path = file_record.file_path,
    )