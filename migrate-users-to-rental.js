// ==================== MIGRATE USERS FROM rental_db TO rental ====================
// Script này di chuyển tất cả users từ database rental_db sang database rental
// để đồng nhất với sharding configuration

print('🔄 Starting user data migration...');
print('');

// Connect to source database
var sourceDb = db.getSiblingDB('rental_db');
var targetDb = db.getSiblingDB('rental');

// Check if rental_db exists and has users
var sourceUsers = sourceDb.users.countDocuments();
print('📊 Found ' + sourceUsers + ' users in rental_db.users');

if (sourceUsers === 0) {
    print('⚠️ No users found in rental_db. Nothing to migrate.');
    print('✅ Migration completed (nothing to do).');
    quit(0);
}

// Check if target already has users
var targetUsers = targetDb.users.countDocuments();
print('📊 Current users in rental.users: ' + targetUsers);

if (targetUsers > 0) {
    print('');
    print('⚠️ WARNING: rental.users already has ' + targetUsers + ' documents!');
    print('');
    print('Options:');
    print('1. If you want to merge: Continue with this script');
    print('2. If you want to replace: Delete rental.users first');
    print('');
    print('Proceeding with merge...');
}

// Get all users from source
print('');
print('📦 Fetching users from rental_db...');
var users = sourceDb.users.find().toArray();

print('✅ Fetched ' + users.length + ' users');

// Insert users into target database
print('');
print('💾 Inserting users into rental.users...');

var insertedCount = 0;
var skippedCount = 0;
var errors = [];

users.forEach(function(user) {
    try {
        // Check if user already exists in target (by _id or email)
        var existingUser = targetDb.users.findOne({
            $or: [
                { _id: user._id },
                { email: user.email }
            ]
        });
        
        if (existingUser) {
            print('  ⚠️ Skipping duplicate user: ' + user.username + ' (' + user.email + ')');
            skippedCount++;
        } else {
            targetDb.users.insertOne(user);
            print('  ✅ Migrated: ' + user.username + ' (' + user.email + ')');
            insertedCount++;
        }
    } catch (e) {
        print('  ❌ Error migrating ' + user.username + ': ' + e.message);
        errors.push({ user: user.username, error: e.message });
    }
});

// Summary
print('');
print('═══════════════════════════════════════════════════════');
print('📊 MIGRATION SUMMARY');
print('═══════════════════════════════════════════════════════');
print('Total users processed: ' + users.length);
print('✅ Successfully migrated: ' + insertedCount);
print('⚠️ Skipped (duplicates): ' + skippedCount);
print('❌ Errors: ' + errors.length);

if (errors.length > 0) {
    print('');
    print('Error details:');
    errors.forEach(function(err) {
        print('  - ' + err.user + ': ' + err.error);
    });
}

// Verify migration
print('');
print('🔍 Verifying migration...');
var finalCount = targetDb.users.countDocuments();
print('📊 Total users in rental.users: ' + finalCount);

// Show sample users
print('');
print('📋 Sample users in rental.users:');
targetDb.users.find().limit(5).forEach(function(user) {
    print('  - ' + user.username + ' (' + user.email + ') - ' + user.role);
});

print('');
print('═══════════════════════════════════════════════════════');
print('✅ Migration completed successfully!');
print('═══════════════════════════════════════════════════════');
print('');
print('📝 Next steps:');
print('1. Verify data in rental.users collection');
print('2. Update all services to use MONGO_DB=rental');
print('3. Restart services with new configuration');
print('4. (Optional) Delete rental_db database after verification');
print('');
print('⚠️ To delete rental_db (after verification):');
print('   db.getSiblingDB("rental_db").dropDatabase()');
