from fastapi import Depends, HTTPException, status, APIRouter, Body, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
import uuid
from datetime import datetime, timedelta
from typing import Annotated

from ..models import User, ShareToken, CreateShareToken, ShareTokenResponse, ShareItemsResponse, FileResponse
from ..utils import get_session, validate_session, create_hash, verify_hash, get_item_data, get_connected_record, decrypt_file, limiter

router = APIRouter()

@router.post("/share/create", response_model=ShareTokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_share_token(
    request: Request,
    share_data: CreateShareToken,
    session: Session = Depends(get_session),
    user_id: uuid.UUID = Depends(validate_session)
):
    """ Create a new share token that allows temporary access to specific health records.
    
    This endpoint generates a unique sharing link with PIN protection, letting users securely share
    selected health information with healthcare providers or family members.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        share_data (CreateShareToken): Contains sharing parameters:
            - pin: str: PIN code that will be needed to access the data
            - token_length: int: Duration in minutes that the sharing link will remain valid
            - shared_items: list: List of items to share (medications, allergies, lab results, etc.)
        session (Session): Database session
        user_id (uuid.UUID): ID of the authenticated user creating the share

    Raises:
        HTTPException: 404 NOT FOUND if the user is not found in the database
        HTTPException: 500 INTERNAL SERVER ERROR if an error occurs during token creation

    Returns:
        ShareTokenResponse: Object containing sharing details:
            - id: UUID of the share token
            - code: Unique share code to use in the sharing URL
            - expiration_time: Date and time when the share token will expire
        status: 201 CREATED: Share token created successfully
    """
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Hash the PIN created in the create share link form
    hashed_pin = create_hash(share_data.pin)
    
    # Create a share token with the given PIN and expiration time
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
@limiter.limit("5/minute")
async def check_share_token(
    request: Request,
    share_code: str,
    session: Session = Depends(get_session)
):
    """ Validate if a share token exists and is still active.
    
    This endpoint checks whether a given share code is valid and has not expired.
    It is typically used before prompting for the PIN to avoid revealing whether a
    share token exists.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        share_code (str): The unique code from the share token
        session (Session): Database session

    Raises:
        HTTPException: 404 NOT FOUND if the share token does not exist
        HTTPException: 410 GONE if the share token has expired

    Returns:
        dict: Simple validation response
            - "valid": True
        status: 200 OK: Share token is valid
    """
    share_token = session.exec(select(ShareToken).where(ShareToken.share_code == share_code)).first()
    
    if not share_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share token not found")
    
    if share_token.expiration_time < datetime.now():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share token has expired")
    
    return {
        "valid": True
    }
    
@router.post("/share/{share_code}/verify", status_code=status.HTTP_200_OK, response_model=ShareItemsResponse)
@limiter.limit("5/minute")
async def verify_share_token(
    request: Request,
    share_code: str,
    pin: Annotated[str, Body(embed=True)],
    session: Session = Depends(get_session)
):
    """ Verify a share token with PIN and retrieve the shared health data.
    
    This endpoint authenticates access to shared data by verifying the PIN.
    When successful, it returns all health data that was selected for sharing.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        share_code (str): The unique code from the share token
        pin (str): PIN code associated with the share token
        session (Session): Database session

    Raises:
        HTTPException: 404 NOT FOUND if the share token does not exist
        HTTPException: 403 FORBIDDEN if the provided PIN does not match

    Returns:
        ShareItemsResponse: Comprehensive object containing:
            - expiration_time: When the share will expire
            - patient: Basic patient information (name, date of birth)
            - items: Dictionary of all shared health items organized by category
        status: 200 OK: PIN verification successful, shared data returned
    """
    share_token = session.exec(select(ShareToken).where(ShareToken.share_code == share_code)).first()
    
    if not share_token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share token not found")
    
    # Check the PIN against the hashed PIN stored in the database
    if not verify_hash(pin, share_token.hashed_pin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid PIN")
    
    user = session.exec(select(User).where(User.id == share_token.user_id)).first()
    
    user_data = {
        "name": user.name,
        "dob": user.dob.strftime("%d-%m-%Y") if user.dob else None,
    }
    
    # Process the shared items, which are stored as a JSON string in the database
    items_data = get_item_data(share_token.shared_items, session)
    
    items_response = ShareItemsResponse(
        expiration_time=share_token.expiration_time,
        patient=user_data,
        items=items_data
    )
    
    return items_response
    
    
@router.delete("/share/{share_code}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_share_token(
    request: Request,
    share_code: str,
    session: Session = Depends(get_session),
    user_id: uuid.UUID = Depends(validate_session)
):
    """ Delete a share token to immediately revoke access to shared health data.
    
    This endpoint allows users to invalidate a previously created share token before
    its natural expiration time, providing control over who can access their health data.

    Args:
        request (Request): Request is automatically used by the endpoint and the rate limiter middleware to limit the number of requests from a single IP address.
        share_code (str): The unique code from the share token to delete
        session (Session): Database session
        user_id (uuid.UUID): ID of the authenticated user requesting deletion

    Raises:
        HTTPException: 404 NOT FOUND if the share token does not exist
        HTTPException: 403 FORBIDDEN if the requesting user is not the owner of the share token

    Returns:
        dict: Confirmation message
            - "detail": "Share token deleted successfully"
        status: 200 OK: Share token successfully deleted
    """
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
@router.get("/share/{share_code}/{record_type}/{record_id}/metadata", response_model=FileResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_file_metadata(
    share_code: str,
    record_type: str,
    record_id: uuid.UUID,
    request: Request,
    session: Session = Depends(get_session)    
):
    """ Retrieve metadata about a shared file without downloading it.
    
    This endpoint is similar to the original file metadata endpoint, but instead of requiring session-based
    authentication, it requires the share token's PIN in the Authorization header for access. It provides
    information about a shared file without transferring the file content.

    Args:
        share_code (str): The unique code from the share token
        record_type (str): Type of record the file is associated with ('vaccine' or 'medicalhistory')
        record_id (uuid.UUID): ID of the record the file is associated with
        request (Request): Request object containing the Authorization header with the PIN
        session (Session): Database session

    Raises:
        HTTPException: 404 NOT FOUND if the share token or file does not exist
        HTTPException: 410 GONE if the share token has expired
        HTTPException: 403 FORBIDDEN if the PIN in the Authorization header is invalid or missing

    Returns:
        FileResponse: Object containing file metadata with the following fields:
            - id: UUID: ID of the file
            - name: str: Name of the file
            - file_type: str: MIME type of the file
            - file_path: str: Path to the stored file
        status: 200 OK: File metadata retrieved successfully
    """
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
    
@router.get("/share/{share_code}/file/{record_type}/{record_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def get_shared_file(
    share_code: str,
    record_type: str,
    record_id: uuid.UUID,
    request: Request,
    session: Session = Depends(get_session)
):
    """ Retrieve a shared file through the sharing mechanism.
    
    This endpoint is similar to the original file download endpoint, but instead of requiring session-based
    authentication, it requires the share token's PIN in the Authorization header for access. It retrieves,
    decrypts, and streams the requested file to the client if authentication is successful.

    Args:
        share_code (str): The unique code from the share token
        record_type (str): Type of record the file is associated with ('vaccine' or 'medicalhistory')
        record_id (uuid.UUID): ID of the record the file is associated with
        request (Request): Request object containing the Authorization header with the PIN
        session (Session): Database session

    Raises:
        HTTPException: 404 NOT FOUND if the share token or file does not exist
        HTTPException: 410 GONE if the share token has expired
        HTTPException: 403 FORBIDDEN if the PIN in the Authorization header is invalid or missing

    Returns:
        StreamingResponse: The decrypted file content streamed to the client with appropriate headers
        status: 200 OK: File retrieved successfully
    """
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