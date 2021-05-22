import sqlite3

from fastapi import Cookie, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from typing import List


app = FastAPI()


# conf = ConnectionConfig(
#     MAIL_USERNAME = "message.api.practise@gmail.com",
#     MAIL_PASSWORD = "Message123.",
#     MAIL_FROM = "message.api.practise@gmail.com",
#     MAIL_PORT = 587,
#     MAIL_SERVER = "smtp.gmail.com",
#     MAIL_FROM_NAME= "MessageAPI",
#     MAIL_TLS = True,
#     MAIL_SSL = False,
#     USE_CREDENTIALS = True
# )


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("messages.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/messages")
async def messages():
    messages = app.db_connection.execute("""
        SELECT Owner, Title, Counter FROM Messages
        """).fetchall()
    return messages
