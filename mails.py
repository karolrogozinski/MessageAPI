from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import random


conf = ConnectionConfig(
    MAIL_USERNAME = "message.api.practise@gmail.com",
    MAIL_PASSWORD = "Message123.",
    MAIL_FROM = "message.api.practise@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_FROM_NAME= "MessageAPI",
    MAIL_TLS = True,
    MAIL_SSL = False
)


def generate_password() -> str:
    return ''.join(random.sample('QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890', 32))


async def send_email(email: str) -> str:
    password = generate_password()
    message = MessageSchema(
        subject = "MessageAPI Auth",
        recipients = [email],
        body = f'Hello!/nYour one-time password to MessageAPI is:/n{password}',
        subtype = "html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return password
