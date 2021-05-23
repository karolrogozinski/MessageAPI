import sqlite3
import asyncio

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from typing import List

from mails import send_email
from login import get_user_token, encrypt


from fastapi.security import HTTPBasic, HTTPBasicCredentials
security = HTTPBasic()


app = FastAPI()
app.session_tokens: List[str] = []

@app.get("/users/me")
def read_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    return {"username": credentials.username, "password": credentials.password}


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("messages.db")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()

#
# Login via email
#
@app.get("/login/{email}")
async def login(email: str, response: Response):
    #
    # Generate one-time password and send it to user
    #
    password = await send_email(email)
    session_token = get_user_token(email, password)

    #
    # Add new session token and set Cookie
    #
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
