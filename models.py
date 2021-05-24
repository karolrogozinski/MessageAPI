from pydantic import BaseModel


class Message(BaseModel):
    owner: str
    title: str
    text: str


class MessageText(BaseModel):
    message_id: int
    text: str
