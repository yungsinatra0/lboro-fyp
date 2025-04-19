from dotenv import load_dotenv, set_key
import os
from cryptography.fernet import Fernet
from fastapi import HTTPException, status

load_dotenv()  # Load environment variables from .env

def get_encryption_key() -> bytes:
    """
    Get the encryption key from the environment variable.
    
    If the key is not found, it generates a new key, which is printed 
    in the backend console and raises an HTTPException. This is to ensure 
    that the key is not exposed in the frontend or logs.
    
    Returns:
        bytes: The encryption key as bytes
        
    Raises:
        HTTPException: If the encryption key is not found in the .env file
    """
    file_key = os.getenv("FILE_KEY")
    
    if not file_key:
        new_key = Fernet.generate_key().decode()
        print("New key generated:", new_key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Encryption key not found in .env file. A new key has been generated. Check the logs and restart the server."
        )
        
    return file_key.encode()

def encrypt_file(content: bytes) -> bytes:
    """
    Encrypt file content using the encryption key.
    
    The encryption key is stored in the .env file and is used to encrypt 
    the file content before saving it to the file system.
    
    Args:
        content: The raw file content to encrypt
        
    Returns:
        bytes: The encrypted file content
    """
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(content)

def decrypt_file(encrypted_content: bytes) -> bytes:
    """
    Decrypt file content using the encryption key.
    
    Used by the API to decrypt files before streaming them to the frontend.
    
    Args:
        encrypted_content: The encrypted file content to decrypt
        
    Returns:
        bytes: The decrypted file content
    """
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_content)