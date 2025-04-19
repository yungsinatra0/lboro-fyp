import os
import aiofiles
from fastapi import HTTPException, status
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

API_KEY = os.getenv("API_KEY")

# Client connection to Gemini API using the API key in the .env file
client = genai.Client(api_key=API_KEY)


async def read_file(file_path: str):
    """
    Asynchronously read a file from the given file path.
    
    Args:
        file_path: Path to the file to be read
        
    Returns:
        bytes: The content of the file
        
    Raises:
        HTTPException: If the file is not found or there's an error reading the file
    """
    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")    
    
    try:    
        async with aiofiles.open(file_path, 'rb') as f:
            content = await f.read()
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error reading file: {str(e)}")
    
    return content
    
def extract_with_llm(file_content: bytes, file_type: str):
    """
    Extract lab results from a document using a Large Language Model (Gemini).
    
    Takes a document containing lab results in Romanian and extracts structured data
    in JSON format with test name, code, value, unit, reference range, and method.
    
    Args:
        file_content: Binary content of the file
        file_type: MIME type of the file
        
    Returns:
        str: The extracted lab results in JSON format
    """
    prompt = """
    You have been given a document that contains lab results that is written in the Romanian language. Your job is to extract all lab results from this document in JSON format with the following fields: test_name, test_code, value, unit, reference_range, method. Sometimes the code of the test will be in the name itself, and it is your job to determine if the code is there, for example in brackets or separated by a comma, and separate the name and the code. Sometimes the lab result will not have a method specified, and in that case you return an empty string. The document is in Romanian, however the JSON keys should be in English.

    EXTREMELY IMPORTANT FORMATTING INSTRUCTIONS:
    1. Return ONLY the raw JSON array
    2. DO NOT use code blocks, backticks, or markdown formatting
    3. DO NOT include ```json or ``` anywhere in your response
    4. DO NOT include any explanations or text before or after the JSON
    5. Your response must start with the '[' character and end with the ']' character
    6. The output should be valid JSON that can be parsed directly
    7. Use period (.) as the decimal separator, not comma (,)

    Example of how your output should look, starting from the very first character:
    [{"test_name":"Hemoglobină","test_code":"HGB","value":"14.3","unit":"mg/dL","reference_range":"13.2-17.3", "method":"Chemiluminiscență"}]
    
    if there is no method specified, return an empty string:
    [{"test_name":"Hemoglobină","test_code":"HGB","value":"14.3","unit":"mg/dL","reference_range":"13.2-17.3", "method":""}]
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

def check_is_numeric(value: str) -> bool:
    """
    Check if a string value can be converted to a numeric type.
    
    Args:
        value: The string value to check
        
    Returns:
        bool: True if the value can be converted to a float, False otherwise
    """
    try:
        float(value)
        return True
    except ValueError:
        return False
    
def sort_by_date(results: list):
    """
    Sort a list of results by their collection date in descending order.
    
    Args:
        results: List of result objects with a date_collection attribute
        
    Returns:
        list: The sorted list with most recent results first
    """
    return sorted(results, key=lambda x: x.date_collection, reverse=True)