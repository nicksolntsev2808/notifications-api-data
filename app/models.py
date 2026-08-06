from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Channel(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"


class Status(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class NotificationCreate(BaseModel):
    recipient: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=1000)
    channel: Channel


class NotificationOut(BaseModel):
    id: str
    recipient: str
    message: str
    channel: Channel
    status: Status
    created_at: datetime
    sent_at: Optional[datetime] = None
