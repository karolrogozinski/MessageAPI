from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import hashlib


security = HTTPBasic()
secret_key = 'm3SS'


def get_user_token(email: str, password: str, credentials: HTTPBasicCredentials = Depends(security)) -> str:
    if credentials.username != email:
        raise HTTPException(status_code=401, detail="Incorrect email address")
    if credentials.password != password:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return encrypt(email)


def encrypt(string: str) -> str:
    return hashlib.sha256(f'{string}{secret_key}'.encode()).hexdigest()
