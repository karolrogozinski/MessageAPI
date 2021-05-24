import sqlite3
import asyncio

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from typing import List

from mails import send_email
from login import encrypt, check_login
from models import Message, MessageText


app = FastAPI()
security = HTTPBasic()
app.session_tokens = []


#
# Connect to database
#
@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("messages.db", check_same_thread=False)


#
# Close database connection
#
@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


#
# Send email iwth password to given email
# After that redirect to login window
#
@app.get("/send_secrets/{email}")
async def send_secrets(email: str):
    #
    # Generate one-time password, send it to user and redirect to login
    #
    password = await send_email(email)
    email = encrypt(email)
    password = encrypt(password)
    return RedirectResponse(f"/login?email={email}&password={password}", 303)


#
# Login window
# Don't use it, only derirect from send_secrets
#
@app.get("/login")
def login(email: str, password: str, response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    #
    # Add new session token and set Cookie
    #
    session_token = check_login(email, password, [credentials.username, credentials.password])
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


#
# Delete message with given id
# You have to be owner to do that
#
@app.delete("/messages/{message_id}/delete")
async def delete_message(message_id: int, session_token: str = Cookie(None)):
    #
    # Check if user is logged in
    #
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=403, detail="Unathorised")

    #
    # Check if message exist
    #
    message = app.db_connection.execute("""
        SELECT Owner, Title FROM Messages WHERE MessageID=?
        """, (str(message_id))).fetchone()
    if not message:
        raise HTTPException(status_code=404, detail="Not found")

    #
    # Check if user is message owner
    #
    if encrypt(message[0]) != session_token:
        raise HTTPException(status_code=403, detail="You are not the owner")

    #
    # Delete message
    #
    app.db_connection.execute("""
        DELETE FROM Messages WHERE MessageID=?
        """, str(message_id))
    app.db_connection.commit()
    return {"deleted": message[1]}


#
# Create new message
# Requires Owner, Title and Text
#
@app.post("/messages/new", status_code=201)
async def create_message(message: Message, session_token: str = Cookie(None)):
    #
    # Check if user is logged in
    #
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=403, detail="Unathorised")

    #
    # Check if all parameters was specified
    #
    if not (message.owner and message.title and message.text):
        raise HTTPException(status_code=402, detail="All parameters have to be specified")

    #
    # Check is message has alllowed length
    #
    if len(message.text) > 160:
        raise HTTPException(status_code=402, detail="Your message is too long")

    #
    # Check if user is the owner
    #
    if encrypt(message.owner) != session_token:
        raise HTTPException(status_code=403, detail="You do not have access to create message as this user")

    #
    # Add message to database
    #
    app.db_connection.execute("""
        INSERT INTO Messages (Owner, Title, Text) VALUES (?, ?, ?)
        """, (message.owner, message.title, message.text))
    app.db_connection.commit()
    return {"created": message.title}


#
# Put new text in existing message
# You have to be owner to do that
#
@app.post("/messages/{message_id}/edit")
async def edit_message(message_text: MessageText, session_token: str = Cookie(None)):
    #
    # Check if user is logged in
    #
    if session_token not in app.session_tokens:
        raise HTTPException(status_code=403, detail="Unathorised")

    #
    # Check if message exist
    #
    message = app.db_connection.execute("""
        SELECT Owner, Title FROM Messages WHERE MessageID=?
        """, (str(message_id))).fetchone()
    if not message:
        raise HTTPException(status_code=404, detail="Not found")

    #
    # Check if user is the owner and message is correct
    #
    if encrypt(message[0]) != session_token:
        raise HTTPException(status_code=403, detail="You do not have access to edit this message")
    if not message_text.text or len(message_text.text) > 160:
        raise HTTPException(status_code=402, detail="Incorrect message text")

    #
    # Change message text
    #
    app.db_connection.execute("""
        UPDATE Messages SET Text=? WHERE MessageID=?
        """, (str(message_text.text, message_id)))
    app.db_connection.commit()
    return {"edited": message[1]}
