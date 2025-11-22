from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Thay thông tin USERNAME, PASSWORD, HOST, PORT, DATABASE nếu cần
mongo_url = "mongodb://localhost:27017/"

try:
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)  # timeout 5s
    # Thử kết nối
    client.admin.command('ping')
    print("✅ Kết nối MongoDB thành công!")
    print(client.list_database_names())

except ConnectionFailure as e:
    print("❌ Không thể kết nối MongoDB:", e)


