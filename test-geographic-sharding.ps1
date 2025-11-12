Write-Host "🧪 Testing Geographic Sharding for Vehicles" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host ""

$testScript = @"
print('📝 Inserting test vehicles...\n');

use rental_db;

// Hanoi vehicles
db.vehicles.insertMany([
  {
    brand: 'Toyota',
    model: 'Camry',
    year: 2023,
    license_plate: 'HN-001',
    vehicle_type: 'car',
    location: 'hanoi',
    price_per_day: 500000,
    status: 'available',
    created_at: new Date()
  },
  {
    brand: 'Honda',
    model: 'City',
    year: 2023,
    license_plate: 'HN-002',
    vehicle_type: 'car',
    location: 'hanoi',
    price_per_day: 400000,
    status: 'available',
    created_at: new Date()
  }
]);

// HCM vehicles
db.vehicles.insertMany([
  {
    brand: 'Toyota',
    model: 'Vios',
    year: 2023,
    license_plate: 'HCM-001',
    vehicle_type: 'car',
    location: 'hcm',
    price_per_day: 450000,
    status: 'available',
    created_at: new Date()
  },
  {
    brand: 'Mazda',
    model: 'CX5',
    year: 2023,
    license_plate: 'HCM-002',
    vehicle_type: 'car',
    location: 'hcm',
    price_per_day: 600000,
    status: 'available',
    created_at: new Date()
  }
]);

// Danang vehicles
db.vehicles.insertMany([
  {
    brand: 'Ford',
    model: 'Ranger',
    year: 2023,
    license_plate: 'DN-001',
    vehicle_type: 'truck',
    location: 'danang',
    price_per_day: 700000,
    status: 'available',
    created_at: new Date()
  }
]);

print('✅ Test vehicles inserted\n');

print('📊 Vehicle distribution by location:\n');
print('Hanoi: ' + db.vehicles.countDocuments({location: 'hanoi'}));
print('HCM: ' + db.vehicles.countDocuments({location: 'hcm'}));
print('Danang: ' + db.vehicles.countDocuments({location: 'danang'}));

print('\n🔍 Testing query routing...');
print('\nQuery for Hanoi vehicles:');
var explain = db.vehicles.find({location: 'hanoi'}).explain('executionStats');
print('Shards queried: ' + Object.keys(explain.executionStats.executionStages.shards || {}).length);
"@

docker exec -i mongos-router mongosh --quiet rental_db --eval $testScript

Write-Host "`n✅ Test completed!" -ForegroundColor Green
Write-Host "Run .\check-sharding-status.ps1 to see data distribution" -ForegroundColor Yellow