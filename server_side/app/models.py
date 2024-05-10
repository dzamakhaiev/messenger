from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    phone: str
    password: str


class Session(BaseModel):
    id: int
    session_id: int
    expiration_date: datetime


class UserAddress(BaseModel):
    id: int
    user_id: int
    user_address: str
    last_used: datetime


class Message(BaseModel):
    id: int
    user_sender_id: int
    user_receiver_id: int
    sender_username: str
    message: str
    receive_date: datetime
