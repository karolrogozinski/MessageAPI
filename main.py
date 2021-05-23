import sqlite3
import asyncio

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from typing import List

from mails import send_email
from login import encrypt, check_login


app = FastAPI()
app.session_tokens: List[str] = []


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("messages.db")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()

#
# Send email iwth password to given email
#
@app.get("/send_secrets/{email}")
async def send_email(email: str, response: Response):
    #
    # Generate one-time password, send it to user and redirect to login
    #
    password = await send_email(email)
    return RedirectResponse("", 303)


#
# Login window
#
@app.get("/login")
async def login(email: str, password: str, response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    #
    # Add new session token and set Cookie
    #
    session_token = check_login(email, password, credentials)
    app.session_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    return {"message": "Logged in"}


#
# Display all messages in format:
# {id, owner, title}
#
@app.get("/messages")
async def messages() -> List[dict]:
    messages = app.db_connection.execute("""
        SELECT MessageID, Owner, Title FROM Messages
        """).fetchall()
    return [{"id": x[0], "owner": x[1], "title": x[2]} for x in messages]


#
# Display message with specyfied id in format:
# {owner, title, text, counter}
#
@app.get("/messages/{message_id}")
async def get_message(message_id: int) -> dict:
    #
    # Increase display counter by 1
    #
    app.db_connection.execute("""
        UPDATE Messages SET Counter = Counter + 1 WHERE MessageID=?
        """, (str(message_id)))
    app.db_connection.commit()

    #
    # Find the message and return it
    #
    message = app.db_connection.execute("""
        SELECT Owner, Title, Text, Counter FROM Messages WHERE MessageID=?
        """, (str(message_id))).fetchone()
    if not message:
        raise HTTPException(status_code=404, detail="Not found")

    return {"owner": message[0], "title:": message[1], "text": message[2], "counter": message[3]}
