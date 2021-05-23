import sqlite3

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from pydantic import BaseModel

from typing import List


app = FastAPI()
app.secrets = []


conf = ConnectionConfig(
    MAIL_USERNAME = "message.api.practise@gmail.com",
    MAIL_PASSWORD = "Message123.",
    MAIL_FROM = "message.api.practise@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME= "MessageAPI",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True
)


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("messages.db")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/login/{email}")
async def login(email: str):
    message = MessageSchema(
        subject = "MessageAPI Auth"
        recipients = email
        body = "example email"
        subtype = "html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})


@app.get("/messages")
async def messages():
    messages = app.db_connection.execute("""
        SELECT MessageID, Owner, Title FROM Messages
        """).fetchall()
    return [{"id": x[0], "owner": x[1], "title": x[2]} for x in messages]


@app.get("/messages/{message_id}")
async def get_message(message_id: int):
    app.db_connection.execute("""
        UPDATE Messages SET Counter = Counter + 1 WHERE MessageID=?
        """, (str(message_id)))
    app.db_connection.commit()

    message = app.db_connection.execute("""
        SELECT Owner, Title, Text, Counter FROM Messages WHERE MessageID=?
        """, (str(message_id))).fetchone()
    if not message:
        raise HTTPException(status_code=404, detail="Not found")

    return {"owner": message[0], "title:": message[1], "text": message[2], "counter": message[3]}
