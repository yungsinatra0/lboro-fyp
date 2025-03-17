from dotenv import load_dotenv, set_key
import os
from cryptography.fernet import Fernet
from fastapi import HTTPException, status

load_dotenv()  # Load environment variables from .env

def get_encryption_key() -> bytes:
    
    key = os.getenv("SECRET_KEY")
    
    if not key:
        new_key = Fernet.generate_key().decode()
        print("New key generated:", new_key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Encryption key not found in .env file. A new key has been generated. Check the logs and restart the server."
        )
        
    return key.encode()

def encrypt_file(content: bytes) -> bytes:
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(content)

def decrypt_file(encrypted_content: bytes) -> bytes:
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_content)