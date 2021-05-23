from fastapi import Depends, FastAPI, HTTPException, status
from typing import List
import hashlib


secret_key = 'm3SS'


def encrypt(string: str) -> str:
    return hashlib.sha256(f'{string}{secret_key}'.encode()).hexdigest()


def check_login(email: str, password: str, credentials: List[str]) -> str:
    if encrypt(credentials[0]) != email:
        raise HTTPException(status_code=401, detail="Incorrect email address")
    if encrypt(credentials[1]) != password:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return email
