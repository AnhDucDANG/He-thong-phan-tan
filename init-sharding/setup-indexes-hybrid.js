// ==================== SETUP INDEXES FOR HYBRID SHARDING ====================
// Script này tạo indexes tối ưu cho collections trong hybrid sharding architecture

print('📇 Creating optimized indexes for hybrid sharding...');

db = db.getSiblingDB('rental');

// ==================== USERS COLLECTION (Vertical Shard 1) ====================

print('');
print('👤 Creating indexes for users collection...');

try {
    db.users.createIndex({ email: 1 }, { unique: true });
    print('  ✅ Unique index on email');
} catch(e) {
    print('  ⚠️ Email index error:', e);
}

try {
    db.users.createIndex({ username: 1 }, { unique: true });
    print('  ✅ Unique index on username');
} catch(e) {
    print('  ⚠️ Username index error:', e);
}

try {
    db.users.createIndex({ created_at: -1 });
    print('  ✅ Index on created_at');
} catch(e) {
    print('  ⚠️ Created_at index error:', e);
}

try {
    db.users.createIndex({ role: 1 });
    print('  ✅ Index on role');
} catch(e) {
    print('  ⚠️ Role index error:', e);
}

// ==================== VEHICLES COLLECTION (Vertical Shard 2) ====================

print('');
print('🚗 Creating indexes for vehicles collection...');

try {
    db.vehicles.createIndex({ status: 1 });
    print('  ✅ Index on status');
} catch(e) {
    print('  ⚠️ Status index error:', e);
}

try {
    db.vehicles.createIndex({ type: 1 });
    print('  ✅ Index on type');
} catch(e) {
    print('  ⚠️ Type index error:', e);
}

try {
    db.vehicles.createIndex({ price_per_day: 1 });
    print('  ✅ Index on price_per_day');
} catch(e) {
    print('  ⚠️ Price index error:', e);
}

try {
    db.vehicles.createIndex({ brand: 1, model: 1 });
    print('  ✅ Compound index on brand and model');
} catch(e) {
    print('  ⚠️ Brand/model index error:', e);
}

try {
    db.vehicles.createIndex({ location: '2dsphere' });
    print('  ✅ Geospatial index on location');
} catch(e) {
    print('  ⚠️ Location index error:', e);
}

// ==================== BOOKINGS COLLECTION (Horizontal Geographic Shards 3A/3B/3C) ====================

print('');
print('📅 Creating indexes for bookings collection (Geographic Sharding)...');

// Shard key index (automatic but verify)
try {
    db.bookings.createIndex({ pickup_location: 1, _id: 1 });
    print('  ✅ Compound index on pickup_location and _id (shard key)');
} catch(e) {
    print('  ⚠️ Shard key index error:', e);
}

// Query optimization indexes
try {
    db.bookings.createIndex({ user_id: 1, start_date: -1 });
    print('  ✅ Compound index on user_id and start_date');
} catch(e) {
    print('  ⚠️ User/date index error:', e);
}

try {
    db.bookings.createIndex({ vehicle_id: 1, status: 1 });
    print('  ✅ Compound index on vehicle_id and status');
} catch(e) {
    print('  ⚠️ Vehicle/status index error:', e);
}

try {
    db.bookings.createIndex({ status: 1 });
    print('  ✅ Index on status');
} catch(e) {
    print('  ⚠️ Status index error:', e);
}

try {
    db.bookings.createIndex({ start_date: 1, end_date: 1 });
    print('  ✅ Compound index on start_date and end_date');
} catch(e) {
    print('  ⚠️ Date range index error:', e);
}

try {
    db.bookings.createIndex({ pickup_location: 1, start_date: 1 });
    print('  ✅ Compound index on pickup_location and start_date (zone routing)');
} catch(e) {
    print('  ⚠️ Zone routing index error:', e);
}

try {
    db.bookings.createIndex({ dropoff_location: 1 });
    print('  ✅ Index on dropoff_location');
} catch(e) {
    print('  ⚠️ Dropoff location index error:', e);
}

try {
    db.bookings.createIndex({ created_at: -1 });
    print('  ✅ Index on created_at');
} catch(e) {
    print('  ⚠️ Created_at index error:', e);
}

// ==================== PAYMENTS COLLECTION (Vertical Shard 4) ====================

print('');
print('💳 Creating indexes for payments collection...');

try {
    db.payments.createIndex({ booking_id: 1 }, { unique: true });
    print('  ✅ Unique index on booking_id');
} catch(e) {
    print('  ⚠️ Booking_id index error:', e);
}

try {
    db.payments.createIndex({ user_id: 1, created_at: -1 });
    print('  ✅ Compound index on user_id and created_at');
} catch(e) {
    print('  ⚠️ User/date index error:', e);
}

try {
    db.payments.createIndex({ status: 1 });
    print('  ✅ Index on status');
} catch(e) {
    print('  ⚠️ Status index error:', e);
}

try {
    db.payments.createIndex({ payment_method: 1 });
    print('  ✅ Index on payment_method');
} catch(e) {
    print('  ⚠️ Payment method index error:', e);
}

try {
    db.payments.createIndex({ transaction_id: 1 }, { unique: true, sparse: true });
    print('  ✅ Unique sparse index on transaction_id');
} catch(e) {
    print('  ⚠️ Transaction_id index error:', e);
}

// ==================== VERIFY INDEXES ====================

print('');
print('🔍 Verifying indexes...');

print('');
print('📋 Users collection indexes:');
db.users.getIndexes().forEach(function(idx) {
    print('  - ' + idx.name + ':', JSON.stringify(idx.key));
});

print('');
print('📋 Vehicles collection indexes:');
db.vehicles.getIndexes().forEach(function(idx) {
    print('  - ' + idx.name + ':', JSON.stringify(idx.key));
});

print('');
print('📋 Bookings collection indexes:');
db.bookings.getIndexes().forEach(function(idx) {
    print('  - ' + idx.name + ':', JSON.stringify(idx.key));
});

print('');
print('📋 Payments collection indexes:');
db.payments.getIndexes().forEach(function(idx) {
    print('  - ' + idx.name + ':', JSON.stringify(idx.key));
});

// ==================== SUMMARY ====================

print('');
print('✅ All indexes created successfully!');
print('');
print('📊 Index Strategy Summary:');
print('');
print('  1. USERS (Vertical Shard):');
print('     - Unique: email, username');
print('     - Query: created_at, role');
print('');
print('  2. VEHICLES (Vertical Shard):');
print('     - Query: status, type, price_per_day');
print('     - Compound: brand + model');
print('     - Geospatial: location (2dsphere)');
print('');
print('  3. BOOKINGS (Geographic Horizontal Shards):');
print('     - Shard Key: pickup_location + _id');
print('     - Zone Routing: pickup_location + start_date');
print('     - User Queries: user_id + start_date');
print('     - Vehicle Queries: vehicle_id + status');
print('     - Date Range: start_date + end_date');
print('');
print('  4. PAYMENTS (Vertical Shard):');
print('     - Unique: booking_id, transaction_id');
print('     - Query: user_id + created_at, status, payment_method');
print('');
print('⚡ Performance Tips:');
print('  - Queries with pickup_location will route to correct geographic shard');
print('  - Compound indexes optimize common query patterns');
print('  - Geospatial index enables proximity searches for vehicles');
print('  - Sparse indexes save space for optional fields');
