from fastapi import Depends, HTTPException, status, APIRouter, Body, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
import uuid
from datetime import datetime, timedelta
from typing import Annotated

from ..models import User, ShareToken, CreateShareToken, ShareTokenResponse, ShareItemsResponse, FileResponse
from ..utils import get_session, validate_session, create_hash, verify_hash, get_item_data, get_connected_record, decrypt_file

router = APIRouter()

@router.post("/share/create", response_model=ShareTokenResponse, status_code=status.HTTP_201_CREATED)
async def create_share_token(
    share_data: CreateShareToken,
    session: Session = Depends(get_session),
    user_id: uuid.UUID = Depends(validate_session)
):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    hashed_pin = create_hash(share_data.pin)
    
    try:
        share_token = ShareToken(
            expiration_time=datetime.now() + timedelta(minutes=share_data.token_length),
            hashed_pin=hashed_pin,
            shared_items=share_data.shared_items,
            user = user
        )
        
        session.add(share_token)        
        session.commit()
        session.refresh(share_token)
        
        return ShareTokenResponse(
            id=share_token.id,
            code=share_token.share_code,
            expiration_time=share_token.expiration_time
        )
        
    except Exception as e:
        session.rollback()
        print(f"Share token creation error: {str(e)}")  # Or use a proper logger
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating share token: {str(e)}")
        
@router.get("/share/{share_code}", status_code=status.HTTP_200_OK)
async def check_share_token(
    share_code: str,
    session: Session = Depends(get_session)
):
    share_token = session.exec(select(ShareToken).where(ShareToken.share_code == share_code)).first()
    
    if not share_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share token not found")
    
    if share_token.expiration_time < datetime.now():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share token has expired")
    
    return {
        "valid": True
    }
    
@router.post("/share/{share_code}/verify", status_code=status.HTTP_200_OK, response_model=ShareItemsResponse)
async def verify_share_token(
    share_code: str,
    pin: Annotated[str, Body(embed=True)],
    session: Session = Depends(get_session)
):
    share_token = session.exec(select(ShareToken).where(ShareToken.share_code == share_code)).first()
    
    if not share_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share token not found")
    
    if not verify_hash(pin, share_token.hashed_pin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid PIN")
    
    user = session.exec(select(User).where(User.id == share_token.user_id)).first()
    
    user_data = {
        "name": user.name,
        "dob": user.dob.strftime("%d-%m-%Y") if user.dob else None,
    }
        
    items_data = get_item_data(share_token.shared_items, session)
    
    return {
        "expiration_time": share_token.expiration_time,
        "patient": user_data,
        "items": items_data
    }
    
    
@router.delete("/share/{share_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_share_token(
    share_code: str,
    session: Session = Depends(get_session),
    user_id: uuid.UUID = Depends(validate_session)
):
    share_token = session.exec(select(ShareToken).where(ShareToken.share_code == share_code)).first()
    
    if not share_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share token not found")
    
    if share_token.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this share token")
    
    session.delete(share_token)
    session.commit()

    return {
        "detail": "Share token deleted successfully"
    }
    
# Get file metadata
@router.get("/share/{share_code}/{record_type}/{record_id}/metadata")
async def get_file_metadata(
    share_code: str,
    record_type: str,
    record_id: uuid.UUID,
    request: Request,
    session: Session = Depends(get_session)    
):
    share_token = session.exec(select(ShareToken).where(ShareToken.share_code == share_code)).first()
    
    if not share_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share token not found")
    
    if share_token.expiration_time < datetime.now():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share token has expired")
    
    pin = request.headers.get('Authorization')
    
    if not pin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authorization header missing")
    
    if not verify_hash(pin, share_token.hashed_pin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid PIN")
    
    user_id = share_token.user_id
    
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
    
@router.get("/share/{share_code}/file/{record_type}/{record_id}")
async def get_shared_file(
    share_code: str,
    record_type: str,
    record_id: uuid.UUID,
    request: Request,
    session: Session = Depends(get_session)
):
    share_token = session.exec(select(ShareToken).where(ShareToken.share_code == share_code)).first()
    
    if not share_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share token not found") 
    
    if share_token.expiration_time < datetime.now():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share token has expired")
    
    pin = request.headers.get('Authorization')
    
    if not pin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Authorization header missing")
    
    if not verify_hash(pin, share_token.hashed_pin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid PIN")
    
    record = await get_connected_record(record_type, record_id, share_token.user_id, session)
    
    match record_type:
        case "vaccine":
            file_record = record.certificate
        case "medicalhistory":
            file_record = record.file
            
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
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