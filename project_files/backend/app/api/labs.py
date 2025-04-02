from fastapi import Depends, HTTPException, status, Response, Request, APIRouter
from sqlmodel import Session, select
import uuid
import os
import aiofiles

from ..models import LabResult, LabTest, LabSubcategory, LabResultResponse, LabTestResponse
from ..utils import validate_file, save_file, get_connected_record, decrypt_file, get_session, validate_session
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # Load environment variables from .env

API_KEY = os.getenv("API_KEY")

client = genai.Client(api_key=API_KEY)

router = APIRouter()

# Extract lab tests from uploaded file
@router.post('/me/labtests/extract/{medicalhistory_id}')
async def extract_lab_tests(medicalhistory_id: uuid.UUID, user_id: uuid.UUID = Depends(validate_session), session: Session = Depends(get_session)):
    
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
    
async def read_file(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")    
    
    try:    
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error reading file: {str(e)}")
    
    return content
    
def extract_with_llm(file_content: bytes, file_type: str):
    prompt = "You have been given a document that contains lab results that is written in the Romanian language. Your job is to extract all lab results from this document in JSON format with the following fields: test_name, value, unit, reference_range. The document is in Romanian, however the JSON keys should be in English. Only return the JSON object. Do not add any other text."
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt,
                types.Part.from_bytes(
                file_content, 
                mime_type=file_type
                )
            ])
    
    return response.text

# def process_lab_tests(response_text: str):    
    