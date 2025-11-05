from datetime import datetime
from bson import ObjectId

class UserModel:
    @staticmethod
    def serialize_user(user: dict) -> dict:
        """Convert MongoDB document to dict with string ID"""
        if user:
            user["id"] = str(user.pop("_id"))
            return user
        return None

    @staticmethod
    def create_user_dict(username: str, email: str, hashed_password: str, role: str = "customer") -> dict:
        """Create user document for MongoDB"""
        return {
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": role,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }