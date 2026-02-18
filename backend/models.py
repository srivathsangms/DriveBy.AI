from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="driver")  # driver | family
    created_at = Column(DateTime, default=datetime.utcnow)

class Log(Base):
    __tablename__ = "logs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    driver_id = Column(String, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    fatigue_score = Column(Float)
    emotion = Column(String)
    drowsy_status = Column(Boolean)
