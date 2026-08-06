import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Channel(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"


class Status(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipient: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    channel: Mapped[Channel] = mapped_column(Enum(Channel, name="channel_enum"), nullable=False)
    status: Mapped[Status] = mapped_column(Enum(Status, name="status_enum"), default=Status.pending, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
