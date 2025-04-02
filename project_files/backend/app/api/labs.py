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
    prompt = """
    You have been given a document that contains lab results that is written in the Romanian language. Your job is to extract all lab results from this document in JSON format with the following fields: test_name, test_code, value, unit, reference_range. Sometimes the code of the test will be in the name itself, and it is your job to determine if the code is there, for example in brackets or separated by a comma, and separate the name and the code. The document is in Romanian, however the JSON keys should be in English.

    EXTREMELY IMPORTANT FORMATTING INSTRUCTIONS:
    1. Return ONLY the raw JSON array
    2. DO NOT use code blocks, backticks, or markdown formatting
    3. DO NOT include ```json or ``` anywhere in your response
    4. DO NOT include any explanations or text before or after the JSON
    5. Your response must start with the '[' character and end with the ']' character
    6. The output should be valid JSON that can be parsed directly
    7. Use period (.) as the decimal separator, not comma (,)

    Example of how your output should look, starting from the very first character:
    [{"test_name":"Hemoglobină","test_code":"HGB","value":"14.3","unit":"mg/dL","reference_range":"13.2-17.3"}]
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt,
                types.Part.from_bytes(
                data=file_content, 
                mime_type=file_type
                )
            ])
    
    return response.text

# def process_lab_tests(response_text: str):    
    