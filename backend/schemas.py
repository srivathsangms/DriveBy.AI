from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: str = "driver"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class LogBase(BaseModel):
    fatigue_score: float
    emotion: str
    drowsy_status: bool

class LogCreate(LogBase):
    pass

class LogResponse(LogBase):
    id: str
    driver_id: str
    timestamp: datetime

    class Config:
        from_attributes = True
