from pydantic import BaseModel


class Message(BaseModel):
    owner: str
    title: str
    text: str
