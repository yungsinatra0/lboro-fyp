from fastapi import HTTPException, status, File, UploadFile
from ..models import Vaccine, MedicalHistory
from sqlmodel import Session
from pathlib import Path
import uuid
from datetime import datetime

from .encrypt_utils import encrypt_file

async def validate_file(file: UploadFile) -> bytes:
    """ Validate uploaded file by checking its MIME type and size.
    
    Args:
        file (UploadFile): The file to validate from the FastAPI request.
        
    Raises:
        HTTPException: 415 UNSUPPORTED_MEDIA_TYPE if the file type is not allowed (only jpeg, png, and pdf are allowed).
        HTTPException: 413 REQUEST_ENTITY_TOO_LARGE if the file size exceeds 10MB.
        
    Returns:
        bytes: The validated file content as bytes.
    """
    
    # check file type against allowed file types - currently only jpeg, png, and pdf
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="File type not allowed")
    
    # read the file content
    content = await file.read()
    if len(content) > 10 * 1024 * 1024: # 10MB file size limit
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File size too large")
    
    return content

async def get_connected_record(record_type: str, record_id: uuid.UUID, user_id: uuid.UUID, session: Session):
    """ Retrieve and validate a record (Vaccine or MedicalHistory) based on its type and ID.
    
    This function validates that the record exists and that the requesting user has permission to access it.
    
    Args:
        record_type (str): Type of record to retrieve ('vaccine' or 'medicalhistory').
        record_id (uuid.UUID): ID of the record to retrieve.
        user_id (uuid.UUID): ID of the user requesting access to the record.
        session (Session): Database session for retrieving the record.
        
    Raises:
        HTTPException: 400 BAD_REQUEST if the record type is invalid.
        HTTPException: 404 NOT_FOUND if the record with the specified ID does not exist.
        HTTPException: 403 FORBIDDEN if the user does not have permission to access the record.
        
    Returns:
        The record object (either Vaccine or MedicalHistory) if validation is successful.
    """
    type_map = {
        "vaccine": Vaccine,
        "medicalhistory": MedicalHistory
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
    """ Save an encrypted file with a secure filename in a structured directory.
    
    This function creates a secure filename based on the record ID, timestamp, and file ID,
    creates the necessary directory structure if it doesn't exist, encrypts the file content,
    and saves the encrypted content to disk.
    
    Args:
        content (bytes): The file content to save.
        record_id (uuid.UUID): ID of the record the file is associated with.
        user_id (uuid.UUID): ID of the user who owns the file.
        file_id (uuid.UUID): Unique ID for the file.
        original_filename (str): Original filename from which to extract the extension.
        
    Returns:
        tuple: A tuple containing:
            - secure_name (str): The generated secure filename
            - file_path (Path): The full path where the file was saved
    """
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