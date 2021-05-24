from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import random
import asyncio
import os


conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL"),
    MAIL_PASSWORD = os.getenv("PASSWORD"),
    MAIL_FROM = os.getenv("MAIL"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME= "MessageAPI",
    MAIL_TLS = True,
    MAIL_SSL = False
)


def generate_password() -> str:
    return ''.join(random.sample('QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*()', 32))


async def send_email(email: str) -> str:
    password = generate_password()
    message = MessageSchema(
        subject = "MessageAPI Auth",
        recipients = [email],
        body = f'Hello! Your one-time password to MessageAPI is: {password}',
        subtype = "html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return password
