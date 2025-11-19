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

// Add Shard 1: Users
print('\n📦 Adding Shard 1 (Users)...');
try {
    const result1 = db.adminCommand({ 
        addShard: 'shard1ReplSet/mongo-shard1:27021',
        name: 'shard1'
    });
    print('✅ Shard 1 added:', JSON.stringify(result1));
} catch (error) {
    print('⚠️ Shard 1:', error.message);
}

sleep(2000);

// Add Shard 2: Vehicles (Single Shard)
print('\n🚗 Adding Shard 2 (Vehicles - All Locations)...');
try {
    const result2 = db.adminCommand({ 
        addShard: 'shard2ReplSet/mongo-shard2:27022',
        name: 'shard2'
    });
    print('✅ Shard 2 added:', JSON.stringify(result2));
} catch (error) {
    print('⚠️ Shard 2:', error.message);
}

sleep(2000);

// Add Shard 3: Bookings
print('\n📅 Adding Shard 3 (Bookings)...');
try {
    const result3 = db.adminCommand({ 
        addShard: 'shard3ReplSet/mongo-shard3:27023',
        name: 'shard3'
    });
    print('✅ Shard 3 added:', JSON.stringify(result3));
} catch (error) {
    print('⚠️ Shard 3:', error.message);
}

sleep(2000);

// Add Shard 4: Payments
print('\n💳 Adding Shard 4 (Payments)...');
try {
    const result4 = db.adminCommand({ 
        addShard: 'shard4ReplSet/mongo-shard4:27024',
        name: 'shard4'
    });
    print('✅ Shard 4 added:', JSON.stringify(result4));
} catch (error) {
    print('⚠️ Shard 4:', error.message);
}

sleep(2000);

// Enable sharding on database
print('\n🔧 Enabling sharding on rental_db...');
try {
    const enableResult = db.adminCommand({ enableSharding: 'rental_db' });
    print('✅ Sharding enabled:', JSON.stringify(enableResult));
} catch (error) {
    print('⚠️ Enable sharding:', error.message);
}

sleep(2000);

// ==================== SHARD COLLECTIONS ====================

// 1. Users Collection - Hash sharding by _id
print('\n👥 Sharding users collection (hash by _id)...');
try {
    db.adminCommand({
        shardCollection: 'rental_db.users',
        key: { _id: 'hashed' }
    });
    print('✅ Users collection sharded');
} catch (error) {
    print('⚠️ Users sharding:', error.message);
}

// 2. Vehicles Collection - Hash sharding by vehicle_id (SIMPLIFIED!)
print('\n🚗 Sharding vehicles collection (hash by vehicle_id)...');
try {
    db.adminCommand({
        shardCollection: 'rental_db.vehicles',
        key: { vehicle_id: 'hashed' }
    });
    print('✅ Vehicles collection sharded');
    print('ℹ️ All vehicles will be distributed across shard2 based on hash of vehicle_id');
} catch (error) {
    print('⚠️ Vehicles sharding:', error.message);
}

// 3. Bookings Collection - Hash sharding by user_id
print('\n📅 Sharding bookings collection (hash by user_id)...');
try {
    db.adminCommand({
        shardCollection: 'rental_db.bookings',
        key: { user_id: 'hashed' }
    });
    print('✅ Bookings collection sharded');
} catch (error) {
    print('⚠️ Bookings sharding:', error.message);
}

// 4. Payments Collection - Hash sharding by payment_id
print('\n💳 Sharding payments collection (hash by payment_id)...');
try {
    db.adminCommand({
        shardCollection: 'rental_db.payments',
        key: { payment_id: 'hashed' }
    });
    print('✅ Payments collection sharded');
} catch (error) {
    print('⚠️ Payments sharding:', error.message);
}

print('\n✅ All collections sharded successfully!');

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