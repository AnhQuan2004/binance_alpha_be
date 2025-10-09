from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        if cls.client is None:
            cls.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
        return cls.client
    
    @classmethod
    def get_db(cls):
        client = cls.get_client()
        return client[os.getenv("DB_NAME")]
    
    @classmethod
    async def close(cls):
        if cls.client:
            cls.client.close()
            cls.client = None


def get_collection():
    db = Database.get_db()
    return db["airdrops"]
