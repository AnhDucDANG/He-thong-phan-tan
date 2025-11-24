// ==================== SETUP GEOGRAPHIC ZONES ====================
// Script này cấu hình zones và gán shards vào từng vùng địa lý

print('🌍 Configuring geographic zones for booking shards...');

db = db.getSiblingDB('admin');

// ==================== DEFINE ZONES ====================

print('');
print('📍 Step 1: Adding shards to zones...');

// North Vietnam Zone - Hanoi
print('  ➕ Adding shard3aReplSet to ZONE_NORTH (Hanoi)...');
try {
    sh.addShardToZone('shard3aReplSet', 'ZONE_NORTH');
    print('    ✅ shard3aReplSet → ZONE_NORTH');
} catch(e) {
    print('    ⚠️ Error:', e);
}

// South Vietnam Zone - Ho Chi Minh
print('  ➕ Adding shard3bReplSet to ZONE_SOUTH (Ho Chi Minh)...');
try {
    sh.addShardToZone('shard3bReplSet', 'ZONE_SOUTH');
    print('    ✅ shard3bReplSet → ZONE_SOUTH');
} catch(e) {
    print('    ⚠️ Error:', e);
}

// Central Vietnam Zone - Da Nang
print('  ➕ Adding shard3cReplSet to ZONE_CENTRAL (Da Nang)...');
try {
    sh.addShardToZone('shard3cReplSet', 'ZONE_CENTRAL');
    print('    ✅ shard3cReplSet → ZONE_CENTRAL');
} catch(e) {
    print('    ⚠️ Error:', e);
}

// ==================== ENABLE SHARDING ON DATABASE ====================

print('');
print('📍 Step 2: Enabling sharding on rental database...');
try {
    sh.enableSharding('rental');
    print('  ✅ Sharding enabled on rental database');
} catch(e) {
    print('  ⚠️ Database already sharded or error:', e);
}

// ==================== SHARD COLLECTIONS ====================

print('');
print('📍 Step 3: Sharding collections...');

// Vertical sharding - Users
print('  📦 Sharding users collection (Vertical - to shard1)...');
try {
    db.adminCommand({
        shardCollection: 'rental.users',
        key: { _id: 'hashed' }
    });
    print('    ✅ users collection sharded');
    // Assign users to shard1 only
    sh.addShardToZone('shard1ReplSet', 'ZONE_USERS');
    sh.updateZoneKeyRange(
        'rental.users',
        { _id: MinKey },
        { _id: MaxKey },
        'ZONE_USERS'
    );
} catch(e) {
    print('    ⚠️ Error:', e);
}

// Vertical sharding - Vehicles
print('  📦 Sharding vehicles collection (Vertical - to shard2)...');
try {
    db.adminCommand({
        shardCollection: 'rental.vehicles',
        key: { _id: 'hashed' }
    });
    print('    ✅ vehicles collection sharded');
    // Assign vehicles to shard2 only
    sh.addShardToZone('shard2ReplSet', 'ZONE_VEHICLES');
    sh.updateZoneKeyRange(
        'rental.vehicles',
        { _id: MinKey },
        { _id: MaxKey },
        'ZONE_VEHICLES'
    );
} catch(e) {
    print('    ⚠️ Error:', e);
}

// Horizontal sharding - Bookings (Geographic)
print('  📦 Sharding bookings collection (Horizontal - Geographic)...');
try {
    db.adminCommand({
        shardCollection: 'rental.bookings',
        key: { pickup_location: 1, _id: 1 }
    });
    print('    ✅ bookings collection sharded with compound key');
} catch(e) {
    print('    ⚠️ Error:', e);
}

// Vertical sharding - Payments
print('  📦 Sharding payments collection (Vertical - to shard4)...');
try {
    db.adminCommand({
        shardCollection: 'rental.payments',
        key: { _id: 'hashed' }
    });
    print('    ✅ payments collection sharded');
    // Assign payments to shard4 only
    sh.addShardToZone('shard4ReplSet', 'ZONE_PAYMENTS');
    sh.updateZoneKeyRange(
        'rental.payments',
        { _id: MinKey },
        { _id: MaxKey },
        'ZONE_PAYMENTS'
    );
} catch(e) {
    print('    ⚠️ Error:', e);
}

// ==================== CONFIGURE ZONE RANGES FOR BOOKINGS ====================

print('');
print('📍 Step 4: Configuring geographic zone ranges for bookings...');

// North Vietnam - Hanoi, Hai Phong, Quang Ninh, etc.
print('  🗺️ ZONE_NORTH: Hanoi, Hai Phong, Quang Ninh...');
try {
    sh.updateZoneKeyRange(
        'rental.bookings',
        { pickup_location: 'HANOI', _id: MinKey },
        { pickup_location: 'HANOI', _id: MaxKey },
        'ZONE_NORTH'
    );
    sh.updateZoneKeyRange(
        'rental.bookings',
        { pickup_location: 'HAI_PHONG', _id: MinKey },
        { pickup_location: 'HAI_PHONG', _id: MaxKey },
        'ZONE_NORTH'
    );
    sh.updateZoneKeyRange(
        'rental.bookings',
        { pickup_location: 'QUANG_NINH', _id: MinKey },
        { pickup_location: 'QUANG_NINH', _id: MaxKey },
        'ZONE_NORTH'
    );
    print('    ✅ ZONE_NORTH configured');
} catch(e) {
    print('    ⚠️ Error:', e);
}

// South Vietnam - HCM, Vung Tau, Can Tho, etc.
print('  🗺️ ZONE_SOUTH: Ho Chi Minh, Vung Tau, Can Tho...');
try {
    sh.updateZoneKeyRange(
        'rental.bookings',
        { pickup_location: 'HO_CHI_MINH', _id: MinKey },
        { pickup_location: 'HO_CHI_MINH', _id: MaxKey },
        'ZONE_SOUTH'
    );
    sh.updateZoneKeyRange(
        'rental.bookings',
        { pickup_location: 'VUNG_TAU', _id: MinKey },
        { pickup_location: 'VUNG_TAU', _id: MaxKey },
        'ZONE_SOUTH'
    );
    sh.updateZoneKeyRange(
        'rental.bookings',
        { pickup_location: 'CAN_THO', _id: MinKey },
        { pickup_location: 'CAN_THO', _id: MaxKey },
        'ZONE_SOUTH'
    );
    print('    ✅ ZONE_SOUTH configured');
} catch(e) {
    print('    ⚠️ Error:', e);
}

// Central Vietnam - Da Nang, Hue, Nha Trang, etc.
print('  🗺️ ZONE_CENTRAL: Da Nang, Hue, Nha Trang...');
try {
    sh.updateZoneKeyRange(
        'rental.bookings',
        { pickup_location: 'DA_NANG', _id: MinKey },
        { pickup_location: 'DA_NANG', _id: MaxKey },
        'ZONE_CENTRAL'
    );
    sh.updateZoneKeyRange(
        'rental.bookings',
        { pickup_location: 'HUE', _id: MinKey },
        { pickup_location: 'HUE', _id: MaxKey },
        'ZONE_CENTRAL'
    );
    sh.updateZoneKeyRange(
        'rental.bookings',
        { pickup_location: 'NHA_TRANG', _id: MinKey },
        { pickup_location: 'NHA_TRANG', _id: MaxKey },
        'ZONE_CENTRAL'
    );
    print('    ✅ ZONE_CENTRAL configured');
} catch(e) {
    print('    ⚠️ Error:', e);
}

// ==================== VERIFY CONFIGURATION ====================

print('');
print('🔍 Verifying zone configuration...');

var config = db.getSiblingDB('config');

print('');
print('📋 Shards and their zones:');
config.shards.find().forEach(function(shard) {
    print('  - ' + shard._id + ':', shard.tags || 'No zone');
});

print('');
print('📋 Zone ranges for bookings collection:');
config.tags.find({ ns: 'rental.bookings' }).sort({ min: 1 }).forEach(function(tag) {
    print('  - Zone:', tag.tag);
    print('    Min:', JSON.stringify(tag.min));
    print('    Max:', JSON.stringify(tag.max));
});

print('');
print('✅ Geographic zones configured successfully!');
print('');
print('📊 Zone Summary:');
print('  🌏 ZONE_NORTH (Hanoi):');
print('     - Cities: Hanoi, Hai Phong, Quang Ninh');
print('     - Shard: shard3aReplSet (port 27025)');
print('');
print('  🌏 ZONE_SOUTH (Ho Chi Minh):');
print('     - Cities: Ho Chi Minh, Vung Tau, Can Tho');
print('     - Shard: shard3bReplSet (port 27026)');
print('');
print('  🌏 ZONE_CENTRAL (Da Nang):');
print('     - Cities: Da Nang, Hue, Nha Trang');
print('     - Shard: shard3cReplSet (port 27027)');
print('');
print('⚠️ NOTE: Booking service must include pickup_location field in all booking documents!');
