from pydantic import BaseModel


class User(BaseModel):
    username: str
    first_name: str
    user_id: str | int
    chat_id: str | int

    class Config:
        extra = "forbid"
