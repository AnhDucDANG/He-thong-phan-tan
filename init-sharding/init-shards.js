print("🔧 Initializing Shard Replica Sets...");

print('\n📦 Initializing Shard 1 (Users)...');
try {
    const shard1Config = {
        _id: 'shard1ReplSet',
        members: [
            { _id: 0, host: 'mongo-shard1:27021' }
        ]
    };
    const conn1 = new Mongo('mongo-shard1:27021');
    const result1 = conn1.getDB('admin').runCommand({ replSetInitiate: shard1Config });
    
    if (result1.ok === 1) {
        print('✅ Shard 1 (Users) initialized successfully');
    } else {
        print('⚠️ Shard 1 response:', JSON.stringify(result1));
    }
} catch (error) {
    print('❌ Error initializing Shard 1:', error.message);
}

sleep(3000);

print('\n🚗 Initializing Shard 2 (Vehicles - All Locations)...');
try {
    const shard2Config = {
        _id: 'shard2ReplSet',
        members: [
            { _id: 0, host: 'mongo-shard2:27022' }
        ]
    };
    const conn2 = new Mongo('mongo-shard2:27022');
    const result2 = conn2.getDB('admin').runCommand({ replSetInitiate: shard2Config });
    
    if (result2.ok === 1) {
        print('✅ Shard 2 (Vehicles) initialized successfully');
    } else {
        print('⚠️ Shard 2 response:', JSON.stringify(result2));
    }
} catch (error) {
    print('❌ Error initializing Shard 2:', error.message);
}

sleep(3000);

print('\n📅 Initializing Shard 3 (Bookings)...');
try {
    const shard3Config = {
        _id: 'shard3ReplSet',
        members: [
            { _id: 0, host: 'mongo-shard3:27023' }
        ]
    };
    const conn3 = new Mongo('mongo-shard3:27023');
    const result3 = conn3.getDB('admin').runCommand({ replSetInitiate: shard3Config });
    
    if (result3.ok === 1) {
        print('✅ Shard 3 (Bookings) initialized successfully');
    } else {
        print('⚠️ Shard 3 response:', JSON.stringify(result3));
    }
} catch (error) {
    print('❌ Error initializing Shard 3:', error.message);
}

sleep(3000);

print('\n💳 Initializing Shard 4 (Payments)...');
try {
    const shard4Config = {
        _id: 'shard4ReplSet',
        members: [
            { _id: 0, host: 'mongo-shard4:27024' }
        ]
    };
    const conn4 = new Mongo('mongo-shard4:27024');
    const result4 = conn4.getDB('admin').runCommand({ replSetInitiate: shard4Config });
    
    if (result4.ok === 1) {
        print('✅ Shard 4 (Payments) initialized successfully');
    } else {
        print('⚠️ Shard 4 response:', JSON.stringify(result4));
    }
} catch (error) {
    print('❌ Error initializing Shard 4:', error.message);
}

print('\n✅ All shard replica sets initialized!');