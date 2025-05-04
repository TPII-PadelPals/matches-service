from sqlmodel import SQLModel


# Generic message
class Message(SQLModel):
    message: str


class BotMessage(Message):
    chat_id: int
