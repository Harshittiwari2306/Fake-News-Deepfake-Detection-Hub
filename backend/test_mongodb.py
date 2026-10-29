
import asyncio
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    if not settings.MONGODB_URI:
        print("ERROR: MongoDB URI is missing.")
        return

    client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000
    )

    try:
        await client.admin.command("ping")
        print("SUCCESS: Application MongoDB driver connected!")
        print("Database configured:", settings.MONGODB_DATABASE)
    except Exception as exc:
        print("Connection failed:", type(exc).__name__)
        print(str(exc))
    finally:
        client.close()

asyncio.run(main())
