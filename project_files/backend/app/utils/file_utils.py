from fastapi import HTTPException, status, File, UploadFile
from ..models import Vaccine
from sqlmodel import Session
from pathlib import Path
import uuid
from datetime import datetime

from .encrypt_utils import encrypt_file

async def validate_file(file: UploadFile) -> bytes:
    
    # check file type against allowed file types - currently only jpeg, png, and pdf
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="File type not allowed")
    
    content = await file.read()
    if len(content) > 10 * 1024 * 1024: # 10MB file size limit
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File size too large")
    
    return content

async def get_connected_record(record_type: str, record_id: uuid.UUID, user_id: uuid.UUID, session: Session):
    type_map = {
        "vaccine": Vaccine
        # Will add more record types here later
    }
    
    if record_type not in type_map:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid record type")
    
    record = session.get(type_map[record_type], record_id)
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    
    if record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return record

def save_file(content: bytes, record_id: uuid.UUID, user_id: uuid.UUID, file_id: uuid.UUID, original_filename: str):
    file_extension = Path(original_filename).suffix
    upload_time = datetime.now().strftime("%d%m%Y_%H%M%S")
    
    secure_name = f"{record_id}_{upload_time}_{file_id}{file_extension}"
    
    upload_dir = Path("uploads") / str(user_id) / str(record_id)
    upload_dir.mkdir(parents=True, exist_ok=True) # create directory if it doesn't exist, parents=True creates parent directories if needed and exist_ok=True doesn't raise an error if the directory already exists
    
    file_path = upload_dir / secure_name
    encrypted_content = encrypt_file(content)
    
    with open(file_path, "wb") as f:
        f.write(encrypted_content)
        
    return secure_name, file_path  