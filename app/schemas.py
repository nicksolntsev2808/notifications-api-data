import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models import Channel, Status


class NotificationCreate(BaseModel):
    recipient: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=1000)
    channel: Channel


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recipient: str
    message: str
    channel: Channel
    status: Status
    created_at: datetime
    sent_at: Optional[datetime] = None
