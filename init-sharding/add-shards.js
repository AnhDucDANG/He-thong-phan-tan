print("🚀 Step 3: Adding Shards to Cluster and Configuring Sharding...");
print("=".repeat(80));

// Wait for mongos to be ready
function waitForMongos() {
    print("\n⏳ Waiting for mongos router...");
    const maxRetries = 30;
    let retries = 0;
    
    while (retries < maxRetries) {
        try {
            db.adminCommand({ ping: 1 });
            print("✅ Mongos is ready");
            return true;
        } catch (e) {
            retries++;
            print(`   Attempt ${retries}/${maxRetries}...`);
            sleep(2000);
        }
    }
    
    throw new Error("❌ Mongos not ready after " + maxRetries + " attempts");
}

waitForMongos();
sleep(5000);

// ==================== ADD SHARDS ====================
print("\n📦 Adding Shards to Cluster...");
print("-".repeat(60));

const shards = [
    { name: "shard1", conn: "shard1ReplSet/mongo-shard1:27021", description: "Users" },
    { name: "shard2a", conn: "shard2aReplSet/mongo-shard2a:27022", description: "Vehicles Hanoi" },
    { name: "shard2b", conn: "shard2bReplSet/mongo-shard2b:27023", description: "Vehicles HCM" },
    { name: "shard2c", conn: "shard2cReplSet/mongo-shard2c:27024", description: "Vehicles Danang" },
    { name: "shard3", conn: "shard3ReplSet/mongo-shard3:27025", description: "Bookings" },
    { name: "shard4", conn: "shard4ReplSet/mongo-shard4:27026", description: "Payments" }
];

shards.forEach(function(shard) {
    try {
        const result = sh.addShard(shard.conn);
        print(`✅ ${shard.name} (${shard.description}) added`);
    } catch (e) {
        if (e.message.includes("already exists") || e.codeName === "ShardAlreadyExists") {
            print(`ℹ️  ${shard.name} already exists`);
        } else {
            print(`⚠️  ${shard.name} error: ${e}`);
        }
    }
});

// ==================== ENABLE SHARDING ====================
print("\n🔓 Enabling Sharding for Database...");
print("-".repeat(60));

try {
    sh.enableSharding("rental_db");
    print("✅ Sharding enabled for rental_db");
} catch (e) {
    if (e.message.includes("already enabled")) {
        print("ℹ️  Sharding already enabled for rental_db");
    } else {
        print("⚠️  Error enabling sharding: " + e);
    }
}

sleep(3000);

// ==================== SHARD COLLECTIONS ====================
print("\n📊 Sharding Collections...");
print("-".repeat(60));

// 1. USERS Collection - Hash Sharding
print("\n1️⃣  Sharding 'users' collection (Hash on _id)...");
try {
    sh.shardCollection("rental_db.users", { _id: "hashed" });
    print("✅ Users collection sharded");
    
    sh.addShardTag("shard1ReplSet", "users_shard");
    sh.addTagRange(
        "rental_db.users",
        { _id: MinKey },
        { _id: MaxKey },
        "users_shard"
    );
    print("✅ Users tagged to shard1");
} catch (e) {
    if (e.message.includes("already sharded")) {
        print("ℹ️  Users collection already sharded");
    } else {
        print("⚠️  Users error: " + e);
    }
}

// 2. VEHICLES Collection - Geographic Sharding
print("\n2️⃣  Sharding 'vehicles' collection (Geographic on location)...");
try {
    sh.shardCollection("rental_db.vehicles", { location: 1, _id: 1 });
    print("✅ Vehicles collection sharded");
    
    // Add tags
    sh.addShardTag("shard2aReplSet", "hanoi");
    sh.addShardTag("shard2bReplSet", "hcm");
    sh.addShardTag("shard2cReplSet", "danang");
    
    // Hanoi
    sh.addTagRange(
        "rental_db.vehicles",
        { location: "hanoi", _id: MinKey },
        { location: "hanoi", _id: MaxKey },
        "hanoi"
    );
    
    // HCM
    sh.addTagRange(
        "rental_db.vehicles",
        { location: "hcm", _id: MinKey },
        { location: "hcm", _id: MaxKey },
        "hcm"
    );
    
    // Danang
    sh.addTagRange(
        "rental_db.vehicles",
        { location: "danang", _id: MinKey },
        { location: "danang", _id: MaxKey },
        "danang"
    );
    
    print("✅ Vehicles geographic zones configured");
} catch (e) {
    if (e.message.includes("already sharded")) {
        print("ℹ️  Vehicles collection already sharded");
    } else {
        print("⚠️  Vehicles error: " + e);
    }
}

// 3. BOOKINGS Collection - Hash Sharding
print("\n3️⃣  Sharding 'bookings' collection (Hash on user_id)...");
try {
    sh.shardCollection("rental_db.bookings", { user_id: "hashed" });
    print("✅ Bookings collection sharded");
    
    sh.addShardTag("shard3ReplSet", "bookings_shard");
    sh.addTagRange(
        "rental_db.bookings",
        { user_id: MinKey },
        { user_id: MaxKey },
        "bookings_shard"
    );
    print("✅ Bookings tagged to shard3");
} catch (e) {
    if (e.message.includes("already sharded")) {
        print("ℹ️  Bookings collection already sharded");
    } else {
        print("⚠️  Bookings error: " + e);
    }
}

// 4. PAYMENTS Collection - Range Sharding
print("\n4️⃣  Sharding 'payments' collection (Range on booking_id)...");
try {
    sh.shardCollection("rental_db.payments", { booking_id: 1, _id: 1 });
    print("✅ Payments collection sharded");
    
    sh.addShardTag("shard4ReplSet", "payments_shard");
    sh.addTagRange(
        "rental_db.payments",
        { booking_id: MinKey, _id: MinKey },
        { booking_id: MaxKey, _id: MaxKey },
        "payments_shard"
    );
    print("✅ Payments tagged to shard4");
} catch (e) {
    if (e.message.includes("already sharded")) {
        print("ℹ️  Payments collection already sharded");
    } else {
        print("⚠️  Payments error: " + e);
    }
}

// ==================== VERIFY CONFIGURATION ====================
print("\n\n📋 SHARDING STATUS:");
print("=".repeat(80));
sh.status();

print("\n\n🎯 SHARDING SUMMARY:");
print("├─ Shard 1: Users (Hash Sharding on _id)");
print("├─ Shard 2a: Vehicles Hanoi (Geographic on location)");
print("├─ Shard 2b: Vehicles HCM (Geographic on location)");
print("├─ Shard 2c: Vehicles Danang (Geographic on location)");
print("├─ Shard 3: Bookings (Hash Sharding on user_id)");
print("└─ Shard 4: Payments (Range Sharding on booking_id)");

print("\n✅ Step 3 completed successfully!");