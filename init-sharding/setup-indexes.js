print('🔧 Creating Indexes...');

const db = connect('mongodb://mongos:27017/rental_db');

// ==================== USERS COLLECTION ====================
print('\n👥 Creating indexes for users collection...');
try {
    // Unique index for email
    db.users.createIndex({ email: 1 }, { unique: true });
    print('✅ Index created: email (unique)');

    // Unique index for username
    db.users.createIndex({ username: 1 }, { unique: true });
    print('✅ Index created: username (unique)');

    // Index for role queries
    db.users.createIndex({ role: 1 });
    print('✅ Index created: role');

    // Index for active users
    db.users.createIndex({ is_active: 1 });
    print('✅ Index created: is_active');

    // Compound index for email verification
    db.users.createIndex({ email: 1, is_verified: 1 });
    print('✅ Index created: email + is_verified');
    
} catch (error) {
    print('❌ Error creating users indexes:', error.message);
}

// ==================== VEHICLES COLLECTION ====================
print('\n🚗 Creating indexes for vehicles collection...');
try {
    // Unique index for vehicle_id (also shard key)
    db.vehicles.createIndex({ vehicle_id: 1 }, { unique: true });
    print('✅ Index created: vehicle_id (unique)');

    // Index for owner queries
    db.vehicles.createIndex({ owner_id: 1 });
    print('✅ Index created: owner_id');

    // Index for location (for queries)
    db.vehicles.createIndex({ location: 1 });
    print('✅ Index created: location');

    // Compound index for available vehicles
    db.vehicles.createIndex({ status: 1, is_verified: 1 });
    print('✅ Index created: status + is_verified');

    // Compound index for location-based searches
    db.vehicles.createIndex({ location: 1, status: 1 });
    print('✅ Index created: location + status');

    // Index for price range queries
    db.vehicles.createIndex({ price_per_day: 1 });
    print('✅ Index created: price_per_day');

    // Compound index for filtered searches
    db.vehicles.createIndex({ 
        location: 1, 
        status: 1, 
        seats: 1, 
        fuel_type: 1 
    });
    print('✅ Index created: location + status + seats + fuel_type');

    // Text index for search
    db.vehicles.createIndex({ 
        brand: 'text', 
        model: 'text' 
    });
    print('✅ Index created: text search (brand, model)');
    
} catch (error) {
    print('❌ Error creating vehicles indexes:', error.message);
}

// ==================== BOOKINGS COLLECTION ====================
print('\n📅 Creating indexes for bookings collection...');
try {
    // Unique index for booking_id
    db.bookings.createIndex({ booking_id: 1 }, { unique: true });
    print('✅ Index created: booking_id (unique)');

    // Index for user bookings
    db.bookings.createIndex({ user_id: 1 });
    print('✅ Index created: user_id');

    // Index for vehicle bookings
    db.bookings.createIndex({ vehicle_id: 1 });
    print('✅ Index created: vehicle_id');

    // Index for booking status
    db.bookings.createIndex({ status: 1 });
    print('✅ Index created: status');

    // Compound index for user's active bookings
    db.bookings.createIndex({ user_id: 1, status: 1 });
    print('✅ Index created: user_id + status');

    // Compound index for vehicle availability
    db.bookings.createIndex({ vehicle_id: 1, status: 1 });
    print('✅ Index created: vehicle_id + status');

    // Index for date range queries
    db.bookings.createIndex({ start_date: 1, end_date: 1 });
    print('✅ Index created: start_date + end_date');

    // Compound index for availability checks
    db.bookings.createIndex({ 
        vehicle_id: 1, 
        start_date: 1, 
        end_date: 1,
        status: 1
    });
    print('✅ Index created: vehicle_id + dates + status');
    
} catch (error) {
    print('❌ Error creating bookings indexes:', error.message);
}

// ==================== PAYMENTS COLLECTION ====================
print('\n💳 Creating indexes for payments collection...');
try {
    // Unique index for payment_id
    db.payments.createIndex({ payment_id: 1 }, { unique: true });
    print('✅ Index created: payment_id (unique)');

    // Index for booking payments
    db.payments.createIndex({ booking_id: 1 });
    print('✅ Index created: booking_id');

    // Index for user payments
    db.payments.createIndex({ user_id: 1 });
    print('✅ Index created: user_id');

    // Index for payment status
    db.payments.createIndex({ status: 1 });
    print('✅ Index created: status');

    // Compound index for user payment history
    db.payments.createIndex({ user_id: 1, created_at: -1 });
    print('✅ Index created: user_id + created_at (desc)');

    // Index for payment method analytics
    db.payments.createIndex({ payment_method: 1 });
    print('✅ Index created: payment_method');
    
} catch (error) {
    print('❌ Error creating payments indexes:', error.message);
}

print('\n✅ All indexes created successfully!');

// Display collection stats
print('\n📊 Collection Statistics:');
try {
    print('\n👥 Users:');
    printjson(db.users.stats());
    
    print('\n🚗 Vehicles:');
    printjson(db.vehicles.stats());
    
    print('\n📅 Bookings:');
    printjson(db.bookings.stats());
    
    print('\n💳 Payments:');
    printjson(db.payments.stats());
} catch (error) {
    print('⚠️ Could not display stats:', error.message);
}