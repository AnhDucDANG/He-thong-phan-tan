print("🔍 Setting up Indexes for Performance...");

db = db.getSiblingDB("rental_db");

// ==================== USERS COLLECTION ====================
print("\n1️⃣  Creating indexes for 'users' collection...");
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ role: 1 });
db.users.createIndex({ is_active: 1, is_deleted: 1 });
db.users.createIndex({ created_at: -1 });
print("✅ Users indexes created");

// ==================== VEHICLES COLLECTION ====================
print("\n2️⃣  Creating indexes for 'vehicles' collection...");
db.vehicles.createIndex({ location: 1, status: 1 });
db.vehicles.createIndex({ vehicle_type: 1 });
db.vehicles.createIndex({ status: 1 });
db.vehicles.createIndex({ price_per_day: 1 });
db.vehicles.createIndex({ owner_id: 1 });
db.vehicles.createIndex({ license_plate: 1 }, { unique: true });
db.vehicles.createIndex({ created_at: -1 });
db.vehicles.createIndex({ 
  brand: "text", 
  model: "text", 
  description: "text" 
}, { 
  name: "vehicle_text_search" 
});
print("✅ Vehicles indexes created");

// ==================== BOOKINGS COLLECTION ====================
print("\n3️⃣  Creating indexes for 'bookings' collection...");
db.bookings.createIndex({ user_id: 1, status: 1 });
db.bookings.createIndex({ vehicle_id: 1, status: 1 });
db.bookings.createIndex({ status: 1 });
db.bookings.createIndex({ start_date: 1, end_date: 1 });
db.bookings.createIndex({ created_at: -1 });
db.bookings.createIndex({ payment_status: 1 });
// Compound index for conflict checking
db.bookings.createIndex({ 
  vehicle_id: 1, 
  start_date: 1, 
  end_date: 1, 
  status: 1 
});
print("✅ Bookings indexes created");

// ==================== PAYMENTS COLLECTION ====================
print("\n4️⃣  Creating indexes for 'payments' collection...");
db.payments.createIndex({ booking_id: 1 });
db.payments.createIndex({ user_id: 1 });
db.payments.createIndex({ status: 1 });
db.payments.createIndex({ payment_method: 1 });
db.payments.createIndex({ created_at: -1 });
db.payments.createIndex({ transaction_id: 1 }, { unique: true, sparse: true });
print("✅ Payments indexes created");

// ==================== VERIFY INDEXES ====================
print("\n📊 Index Summary:");
print("\nUsers Collection:");
printjson(db.users.getIndexes());

print("\nVehicles Collection:");
printjson(db.vehicles.getIndexes());

print("\nBookings Collection:");
printjson(db.bookings.getIndexes());

print("\nPayments Collection:");
printjson(db.payments.getIndexes());

print("\n✅ All indexes created successfully!");