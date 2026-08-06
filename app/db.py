from motor.motor_asyncio import AsyncIOMotorClient
from app.settings import settings

client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.mongo_uri)
    return client


def get_collection():
    mongo = get_client()
    return mongo[settings.mongo_db][settings.mongo_collection]
