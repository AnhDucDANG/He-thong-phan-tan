"""
Script để fix avatar URLs trong database
Thêm '/' vào đầu các avatar_url bị thiếu
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_avatar_urls():
    # Kết nối MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["rental_db"]
    users_collection = db["users"]
    
    # Tìm users có avatar_url không bắt đầu với '/'
    users = await users_collection.find({
        "avatar_url": {"$regex": "^api/users/avatars/"}
    }).to_list(length=None)
    
    print(f"Found {len(users)} users with incorrect avatar URLs")
    
    # Update từng user
    for user in users:
        old_url = user["avatar_url"]
        new_url = f"/{old_url}"
        
        await users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"avatar_url": new_url}}
        )
        
        print(f"✅ Fixed: {user['email']}")
        print(f"   Old: {old_url}")
        print(f"   New: {new_url}")
    
    print(f"\n✅ Done! Fixed {len(users)} avatar URLs")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_avatar_urls())
