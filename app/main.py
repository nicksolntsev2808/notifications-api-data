import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import engine, Base, get_session
from app.models import Notification, Status, Channel
from app.schemas import NotificationCreate, NotificationOut
from app.settings import settings

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post(f"{settings.api_prefix}/notifications", response_model=NotificationOut, status_code=201)
async def create_notification(payload: NotificationCreate, session: AsyncSession = Depends(get_session)):
    notification = Notification(
        recipient=payload.recipient,
        message=payload.message,
        channel=payload.channel,
        status=Status.pending,
    )
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


@app.get(f"{settings.api_prefix}/notifications", response_model=list[NotificationOut])
async def list_notifications(
    status: Status | None = None,
    channel: Channel | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    query = select(Notification).order_by(Notification.created_at.desc()).limit(limit)
    if status is not None:
        query = query.where(Notification.status == status)
    if channel is not None:
        query = query.where(Notification.channel == channel)

    result = await session.execute(query)
    return result.scalars().all()


async def get_notification_or_404(notification_id: uuid.UUID, session: AsyncSession) -> Notification:
    result = await session.execute(select(Notification).where(Notification.id == notification_id))
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification


@app.get(f"{settings.api_prefix}/notifications/{{notification_id}}", response_model=NotificationOut)
async def get_notification(notification_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    return await get_notification_or_404(notification_id, session)


@app.patch(f"{settings.api_prefix}/notifications/{{notification_id}}/send", response_model=NotificationOut)
async def mark_sent(notification_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    notification = await get_notification_or_404(notification_id, session)
    if notification.status != Status.pending:
        raise HTTPException(status_code=409, detail=f"Cannot send from status '{notification.status.value}'")

    notification.status = Status.sent
    notification.sent_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(notification)
    return notification


@app.patch(f"{settings.api_prefix}/notifications/{{notification_id}}/fail", response_model=NotificationOut)
async def mark_failed(notification_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    notification = await get_notification_or_404(notification_id, session)
    if notification.status != Status.pending:
        raise HTTPException(status_code=409, detail=f"Cannot fail from status '{notification.status.value}'")

    notification.status = Status.failed
    await session.commit()
    await session.refresh(notification)
    return notification


@app.delete(f"{settings.api_prefix}/notifications/{{notification_id}}", status_code=204)
async def delete_notification(notification_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    notification = await get_notification_or_404(notification_id, session)
    await session.delete(notification)
    await session.commit()
    return None
