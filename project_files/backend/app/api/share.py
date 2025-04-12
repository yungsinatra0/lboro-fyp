from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
import uuid
from datetime import datetime

from ..models import User, ShareToken, SharedItem, CreateShareToken, CreateShareItem, ShareTokenResponse, ShareItemsResponse
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
            expiration_time=share_data.expiration_time,
            hashed_pin=hashed_pin,
            user = user
        )
        
        session.add(share_token)
        session.flush()
    
        shared_items = []
        for item in share_data.shared_items:
            shared_item = SharedItem(
                item_type=item.item_type,
                item_id=item.item_id,
                share_token=share_token
            )
            shared_items.append(shared_item)
            session.add(shared_item)
        
        session.commit()
        session.refresh(share_token)
        
        return ShareTokenResponse(
            id=share_token.id,
            code=share_token.share_code,
            expiration_time=share_token.expiration_time
        )
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating share token")
        
    
@router.post("/share/{share_code}/verify", status_code=status.HTTP_200_OK, response_model=ShareItemsResponse)
async def verify_share_token(
    share_code: str,
    pin: str,
    session: Session = Depends(get_session)
):
    share_token = session.exec(select(ShareToken).where(ShareToken.share_code == share_code)).first()
    
    if not share_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share token not found")
    
    if share_token.expiration_time < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Share token has expired")
    
    if not verify_hash(pin, share_token.hashed_pin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid PIN")
    
    user = session.exec(select(User).where(User.id == share_token.user_id)).first()
    
    shared_items = session.exec(
        select(SharedItem).where(SharedItem.share_token_id == share_token.id)
    ).all()
    
    grouped_items = {}
    for item in shared_items:
        if item.item_type not in grouped_items:
            grouped_items[item.item_type] = []
        grouped_items[item.item_type].append(item.item_id)
        
    items_data = get_item_data(grouped_items, session)
    
    return {
        "expiration_time": share_token.expiration_time,
        "patient": user,
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
    
@router.get("/share/{share_code}/file/{record_type}/{record_id}")
async def get_shared_file(
    share_code: str,
    record_type: str,
    record_id: uuid.UUID,
    session: Session = Depends(get_session)
):
    share_token = session.exec(select(ShareToken).where(ShareToken.share_code == share_code)).first()
    
    if not share_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share token not found") 
    
    if share_token.expiration_time < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Share token has expired")
    
    shared_item = session.exec(
        select(SharedItem).where(
            SharedItem.share_token_id == share_token.id,
            SharedItem.item_id == record_id,
            SharedItem.item_type == record_type
        )
    ).first()
    
    if not shared_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared item not found")
    
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