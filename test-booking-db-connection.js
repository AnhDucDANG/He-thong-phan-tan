// Test MongoDB Connection for Booking Service
// Chạy script này từ container booking service để test kết nối

const MONGO_URL = process.env.MONGO_URL || "mongodb://100.69.63.99:27017";
const MONGO_DB = process.env.MONGO_DB || "rental";

console.log("🔧 Testing MongoDB Connection...");
console.log("📍 MONGO_URL:", MONGO_URL);
console.log("📍 MONGO_DB:", MONGO_DB);
console.log("");

// Test với MongoDB driver
async function testConnection() {
    const { MongoClient } = require('mongodb');
    
    let client;
    try {
        console.log("⏳ Connecting to MongoDB...");
        
        client = new MongoClient(MONGO_URL, {
            serverSelectionTimeoutMS: 5000,
            connectTimeoutMS: 5000,
        });
        
        await client.connect();
        console.log("✅ Connected successfully!");
        console.log("");
        
        // Kiểm tra database
        const db = client.db(MONGO_DB);
        console.log("📊 Database:", db.databaseName);
        console.log("");
        
        // List collections
        const collections = await db.listCollections().toArray();
        console.log("📁 Available Collections:");
        collections.forEach(col => {
            console.log(`   - ${col.name}`);
        });
        console.log("");
        
        // Test query
        console.log("🔍 Testing query on 'bookings' collection...");
        const bookingsCount = await db.collection('bookings').countDocuments();
        console.log(`   Total bookings: ${bookingsCount}`);
        console.log("");
        
        // Kiểm tra sharding status
        console.log("🌐 Checking Sharding Status...");
        const admin = client.db('admin');
        const shardStatus = await admin.command({ listShards: 1 });
        console.log("   Available Shards:", shardStatus.shards.length);
        shardStatus.shards.forEach(shard => {
            console.log(`   - ${shard._id}: ${shard.host}`);
        });
        console.log("");
        
        console.log("✅ All tests passed!");
        
    } catch (error) {
        console.error("❌ Connection failed!");
        console.error("Error:", error.message);
        console.error("");
        console.error("📋 Troubleshooting:");
        console.error("1. Check if mongos router is running:");
        console.error("   docker ps | grep mongos");
        console.error("");
        console.error("2. Check if Tailscale IP is correct:");
        console.error("   ping 100.69.63.99");
        console.error("");
        console.error("3. Check if port 27017 is accessible:");
        console.error("   telnet 100.69.63.99 27017");
        console.error("");
        console.error("4. Check MONGO_URL format (should NOT have /database at end):");
        console.error("   ✅ Correct: mongodb://100.69.63.99:27017");
        console.error("   ❌ Wrong: mongodb://100.69.63.99:27017/rental");
        
        process.exit(1);
        
    } finally {
        if (client) {
            await client.close();
            console.log("🔌 Connection closed.");
        }
    }
}

testConnection();
