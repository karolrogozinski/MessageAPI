from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List
import hashlib


security = HTTPBasic()
secret_key = 'm3SS'


def get_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    return credentials.username, credentials.password


def encrypt(string: str) -> str:
    return hashlib.sha256(f'{string}{secret_key}'.encode()).hexdigest()


def check_login(email: str, password: str, credentials: List[str]) -> str:
    if credentials[0] != email:
        raise HTTPException(status_code=401, detail="Incorrect email address")
    if credentials[1] != password:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return encrypt(email)
