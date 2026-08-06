from datetime import datetime, timezone
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from app.db import get_collection, get_client
from app.models import NotificationCreate, NotificationOut, Status, Channel
from app.settings import settings

app = FastAPI(title=settings.app_name)


def serialize(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "recipient": doc["recipient"],
        "message": doc["message"],
        "channel": doc["channel"],
        "status": doc["status"],
        "created_at": doc["created_at"],
        "sent_at": doc.get("sent_at"),
    }


async def get_notification_or_404(notification_id: str) -> dict:
    if not ObjectId.is_valid(notification_id):
        raise HTTPException(status_code=400, detail="Invalid notification id")
    collection = get_collection()
    doc = await collection.find_one({"_id": ObjectId(notification_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Notification not found")
    return doc


@app.on_event("startup")
async def startup():
    client = get_client()
    await client.admin.command("ping")
    collection = get_collection()
    await collection.create_index("status")
    await collection.create_index("channel")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post(f"{settings.api_prefix}/notifications", response_model=NotificationOut, status_code=201)
async def create_notification(payload: NotificationCreate):
    doc = {
        "recipient": payload.recipient,
        "message": payload.message,
        "channel": payload.channel.value,
        "status": Status.pending.value,
        "created_at": datetime.now(timezone.utc),
        "sent_at": None,
    }
    collection = get_collection()
    result = await collection.insert_one(doc)
    saved = await collection.find_one({"_id": result.inserted_id})
    return serialize(saved)


@app.get(f"{settings.api_prefix}/notifications", response_model=list[NotificationOut])
async def list_notifications(
    status: Status | None = None,
    channel: Channel | None = None,
    limit: int = Query(default=20, ge=1, le=100),
):
    query = {}
    if status is not None:
        query["status"] = status.value
    if channel is not None:
        query["channel"] = channel.value

    collection = get_collection()
    cursor = collection.find(query).sort("created_at", -1).limit(limit)
    result = []
    async for doc in cursor:
        result.append(serialize(doc))
    return result


@app.get(f"{settings.api_prefix}/notifications/{{notification_id}}", response_model=NotificationOut)
async def get_notification(notification_id: str):
    doc = await get_notification_or_404(notification_id)
    return serialize(doc)


@app.patch(f"{settings.api_prefix}/notifications/{{notification_id}}/send", response_model=NotificationOut)
async def mark_sent(notification_id: str):
    doc = await get_notification_or_404(notification_id)
    if doc["status"] != Status.pending.value:
        raise HTTPException(status_code=409, detail=f"Cannot send from status '{doc['status']}'")

    collection = get_collection()
    await collection.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"status": Status.sent.value, "sent_at": datetime.now(timezone.utc)}},
    )
    updated = await collection.find_one({"_id": ObjectId(notification_id)})
    return serialize(updated)


@app.patch(f"{settings.api_prefix}/notifications/{{notification_id}}/fail", response_model=NotificationOut)
async def mark_failed(notification_id: str):
    doc = await get_notification_or_404(notification_id)
    if doc["status"] != Status.pending.value:
        raise HTTPException(status_code=409, detail=f"Cannot fail from status '{doc['status']}'")

    collection = get_collection()
    await collection.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": {"status": Status.failed.value}},
    )
    updated = await collection.find_one({"_id": ObjectId(notification_id)})
    return serialize(updated)


@app.delete(f"{settings.api_prefix}/notifications/{{notification_id}}", status_code=204)
async def delete_notification(notification_id: str):
    await get_notification_or_404(notification_id)
    collection = get_collection()
    await collection.delete_one({"_id": ObjectId(notification_id)})
    return None
