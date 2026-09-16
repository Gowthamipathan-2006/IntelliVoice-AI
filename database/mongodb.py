import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "intellivoice_db"
)


if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is missing in .env"
    )


# ============================================================
# MONGODB CLIENT
# ============================================================

client = MongoClient(
    MONGODB_URI,

    # Connection timeout
    connectTimeoutMS=10000,

    # Server selection timeout
    serverSelectionTimeoutMS=5000,

    # Socket timeout
    socketTimeoutMS=20000,

    # Keep connection alive
    retryWrites=True,

    # Use TLS
    tls=True
)


# ============================================================
# DATABASE
# ============================================================

db = client[MONGODB_DATABASE]

chat_collection = db["chat_history"]


# ============================================================
# TEST CONNECTION
# ============================================================

def test_connection():

    try:

        client.admin.command("ping")

        print("✅ MongoDB Atlas connection successful")

        return True

    except PyMongoError as e:

        print("❌ MongoDB Atlas connection failed:")
        print(str(e))

        return False


# ============================================================
# SAVE CHAT
# ============================================================

def save_chat(user_message, ai_response, action):

    document = {
        "user_message": user_message,
        "ai_response": ai_response,
        "action": action,
        "timestamp": datetime.now(timezone.utc)
    }

    try:

        result = chat_collection.insert_one(document)

        print(
            f"✅ MongoDB: Chat saved successfully "
            f"(ID: {result.inserted_id})"
        )

        return {
            "success": True,
            "id": str(result.inserted_id)
        }

    except PyMongoError as e:

        print("❌ MongoDB save error:")
        print(str(e))

        return {
            "success": False,
            "error": str(e)
        }


# ============================================================
# GET CHAT HISTORY
# ============================================================

def get_chat_history(limit=50):

    try:

        chats = (
            chat_collection
            .find({})
            .sort("timestamp", -1)
            .limit(limit)
        )

        history = []

        for chat in chats:

            timestamp = chat.get("timestamp")

            if timestamp:

                timestamp = timestamp.isoformat()

            history.append({
                "id": str(chat.get("_id")),
                "user_message": chat.get(
                    "user_message",
                    ""
                ),
                "ai_response": chat.get(
                    "ai_response",
                    ""
                ),
                "action": chat.get(
                    "action",
                    "direct"
                ),
                "timestamp": timestamp
            })

        # Return oldest → newest
        history.reverse()

        print(
            f"✅ MongoDB: Retrieved {len(history)} conversations"
        )

        return history

    except PyMongoError as e:

        print("❌ MongoDB history error:")
        print(str(e))

        return []


# ============================================================
# CLEAR CHAT HISTORY
# ============================================================

def clear_chat_history():

    try:

        result = chat_collection.delete_many({})

        print(
            f"🗑️ MongoDB: Deleted "
            f"{result.deleted_count} conversations"
        )

        return {
            "success": True,
            "deleted_count": result.deleted_count
        }

    except PyMongoError as e:

        print("❌ MongoDB delete error:")
        print(str(e))

        return {
            "success": False,
            "error": str(e)
        }