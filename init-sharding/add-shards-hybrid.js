// ==================== ADD SHARDS TO CLUSTER ====================
// Script này thêm tất cả shards vào MongoDB cluster với cấu hình hybrid

print('📌 Adding shards to cluster...');

db = db.getSiblingDB('admin');

// ==================== VERTICAL SHARDING (Functional) ====================

print('➕ Adding Shard 1 - Users Service...');
try {
    sh.addShard('shard1ReplSet/mongo-shard1:27021');
    print('✅ Shard 1 added successfully');
} catch(e) {
    print('⚠️ Shard 1 already added or error:', e);
}

print('➕ Adding Shard 2 - Vehicles Service...');
try {
    sh.addShard('shard2ReplSet/mongo-shard2:27022');
    print('✅ Shard 2 added successfully');
} catch(e) {
    print('⚠️ Shard 2 already added or error:', e);
}

// ==================== HORIZONTAL SHARDING (Geographic) ====================

print('🌏 Adding Shard 3A - Bookings HANOI (North Region)...');
try {
    sh.addShard('shard3aReplSet/mongo-shard3a-hanoi:27025');
    print('✅ Shard 3A (HANOI) added successfully');
} catch(e) {
    print('⚠️ Shard 3A already added or error:', e);
}

print('🌏 Adding Shard 3B - Bookings HO CHI MINH (South Region)...');
try {
    sh.addShard('shard3bReplSet/mongo-shard3b-hcm:27026');
    print('✅ Shard 3B (HCM) added successfully');
} catch(e) {
    print('⚠️ Shard 3B already added or error:', e);
}

print('🌏 Adding Shard 3C - Bookings DA NANG (Central Region)...');
try {
    sh.addShard('shard3cReplSet/mongo-shard3c-danang:27027');
    print('✅ Shard 3C (DANANG) added successfully');
} catch(e) {
    print('⚠️ Shard 3C already added or error:', e);
}

// ==================== VERTICAL SHARDING (Functional) ====================

print('➕ Adding Shard 4 - Payments Service...');
try {
    sh.addShard('shard4ReplSet/mongo-shard4:27024');
    print('✅ Shard 4 added successfully');
} catch(e) {
    print('⚠️ Shard 4 already added or error:', e);
}

sleep(2000);

// ==================== VERIFY SHARDS ====================

print('');
print('🔍 Verifying cluster configuration...');
var shards = db.adminCommand({ listShards: 1 });
print('📊 Total shards in cluster:', shards.shards.length);
print('');

shards.shards.forEach(function(shard) {
    print('  - ' + shard._id + ': ' + shard.host);
    if (shard.tags) {
        print('    Tags:', shard.tags);
    }
});

print('');
print('✅ All shards added to cluster!');
print('');
print('📋 Architecture Summary:');
print('  Hybrid Sharding Model:');
print('    1. VERTICAL (Functional): Users, Vehicles, Payments');
print('    2. HORIZONTAL (Geographic): Bookings split by region');
print('');
print('  Geographic Distribution:');
print('    - North Vietnam (HANOI): shard3aReplSet');
print('    - South Vietnam (HCM): shard3bReplSet');
print('    - Central Vietnam (DANANG): shard3cReplSet');
