// ==================== INIT SHARD REPLICA SETS ====================
// Script này khởi tạo tất cả replica sets cho các shards

print('🔧 Initializing Shard 1 - Users...');
try {
    db = connect('mongo-shard1:27021/admin');
    rs.initiate({
        _id: 'shard1ReplSet',
        members: [{ _id: 0, host: 'mongo-shard1:27021' }]
    });
    print('✅ Shard 1 (Users) initialized');
} catch(e) {
    print('⚠️ Shard 1 already initialized or error:', e);
}

sleep(3000);

print('🔧 Initializing Shard 2 - Vehicles...');
try {
    db = connect('mongo-shard2:27022/admin');
    rs.initiate({
        _id: 'shard2ReplSet',
        members: [{ _id: 0, host: 'mongo-shard2:27022' }]
    });
    print('✅ Shard 2 (Vehicles) initialized');
} catch(e) {
    print('⚠️ Shard 2 already initialized or error:', e);
}

sleep(3000);

// ==================== BOOKING SHARDS (GEOGRAPHIC) ====================

print('🌍 Initializing Shard 3A - Bookings HANOI (North Region)...');
try {
    db = connect('mongo-shard3a-hanoi:27025/admin');
    rs.initiate({
        _id: 'shard3aReplSet',
        members: [{ _id: 0, host: 'mongo-shard3a-hanoi:27025' }]
    });
    print('✅ Shard 3A (Bookings HANOI) initialized');
} catch(e) {
    print('⚠️ Shard 3A already initialized or error:', e);
}

sleep(3000);

print('🌍 Initializing Shard 3B - Bookings HO CHI MINH (South Region)...');
try {
    db = connect('mongo-shard3b-hcm:27026/admin');
    rs.initiate({
        _id: 'shard3bReplSet',
        members: [{ _id: 0, host: 'mongo-shard3b-hcm:27026' }]
    });
    print('✅ Shard 3B (Bookings HCM) initialized');
} catch(e) {
    print('⚠️ Shard 3B already initialized or error:', e);
}

sleep(3000);

print('🌍 Initializing Shard 3C - Bookings DA NANG (Central Region)...');
try {
    db = connect('mongo-shard3c-danang:27027/admin');
    rs.initiate({
        _id: 'shard3cReplSet',
        members: [{ _id: 0, host: 'mongo-shard3c-danang:27027' }]
    });
    print('✅ Shard 3C (Bookings DANANG) initialized');
} catch(e) {
    print('⚠️ Shard 3C already initialized or error:', e);
}

sleep(3000);

print('🔧 Initializing Shard 4 - Payments...');
try {
    db = connect('mongo-shard4:27024/admin');
    rs.initiate({
        _id: 'shard4ReplSet',
        members: [{ _id: 0, host: 'mongo-shard4:27024' }]
    });
    print('✅ Shard 4 (Payments) initialized');
} catch(e) {
    print('⚠️ Shard 4 already initialized or error:', e);
}

print('');
print('✅ All shard replica sets initialized!');
print('📊 Summary:');
print('  - Shard 1: Users (Vertical Sharding)');
print('  - Shard 2: Vehicles (Vertical Sharding)');
print('  - Shard 3A: Bookings HANOI - North Region (Geographic Sharding)');
print('  - Shard 3B: Bookings HCM - South Region (Geographic Sharding)');
print('  - Shard 3C: Bookings DANANG - Central Region (Geographic Sharding)');
print('  - Shard 4: Payments (Vertical Sharding)');
