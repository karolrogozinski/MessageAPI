import sqlite3
import asyncio

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from typing import List

from mails import send_email


app = FastAPI()
app.secrets = []


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("messages.db")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/login/{email}")
async def login(email: str):
    password = asyncio.run(send_email(email))
    return {"message": "email has been sent"}


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
