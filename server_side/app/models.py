from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    username: str
    phone_number: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str
    user_address: str


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
    sender_id: int
    receiver_id: int
    session_id: str
    sender_username: str
    message: str
    send_date: datetime
