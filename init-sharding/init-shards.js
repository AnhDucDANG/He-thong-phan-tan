print("🔧 Initializing All Shard Replica Sets...");
print("=".repeat(80));

const shards = [
    { name: "shard1", replSetName: "shard1ReplSet", host: "mongo-shard1", port: 27021, description: "Users" },
    { name: "shard2a", replSetName: "shard2aReplSet", host: "mongo-shard2a", port: 27022, description: "Vehicles Hanoi" },
    { name: "shard2b", replSetName: "shard2bReplSet", host: "mongo-shard2b", port: 27023, description: "Vehicles HCM" },
    { name: "shard2c", replSetName: "shard2cReplSet", host: "mongo-shard2c", port: 27024, description: "Vehicles Danang" },
    { name: "shard3", replSetName: "shard3ReplSet", host: "mongo-shard3", port: 27025, description: "Bookings" },
    { name: "shard4", replSetName: "shard4ReplSet", host: "mongo-shard4", port: 27026, description: "Payments" }
];

function initShard(shard) {
    print(`\n📦 Initializing ${shard.name} (${shard.description})...`);
    print("-".repeat(60));
    
    try {
        const conn = new Mongo(`${shard.host}:${shard.port}`);
        const admin = conn.getDB("admin");
        
        // Check if already initialized
        try {
            const status = admin.runCommand({ replSetGetStatus: 1 });
            if (status.ok === 1) {
                print(`ℹ️  ${shard.name} already initialized`);
                return true;
            }
        } catch (e) {
            // Not initialized yet, continue
        }
        
        // Initialize replica set
        const config = {
            _id: shard.replSetName,
            members: [
                { _id: 0, host: `${shard.host}:${shard.port}` }
            ]
        };
        
        const result = admin.runCommand({ replSetInitiate: config });
        
        if (result.ok === 1) {
            print(`✅ ${shard.name} replica set initiated`);
            
            // Wait for PRIMARY
            print(`⏳ Waiting for ${shard.name} to become PRIMARY...`);
            let waited = 0;
            const maxWait = 30;
            
            while (waited < maxWait) {
                try {
                    const status = admin.runCommand({ replSetGetStatus: 1 });
                    if (status.members && status.members[0] && status.members[0].stateStr === "PRIMARY") {
                        print(`✅ ${shard.name} is now PRIMARY`);
                        return true;
                    }
                } catch (e) {
                    // Keep waiting
                }
                sleep(1000);
                waited++;
            }
            
            print(`⚠️  ${shard.name} took too long to become PRIMARY, but continuing...`);
            return true;
            
        } else {
            print(`❌ ${shard.name} initialization failed: ${JSON.stringify(result)}`);
            return false;
        }
        
    } catch (e) {
        if (e.message && e.message.includes("already initialized")) {
            print(`ℹ️  ${shard.name} already initialized`);
            return true;
        } else {
            print(`❌ Error initializing ${shard.name}: ${e}`);
            return false;
        }
    }
}

// Initialize all shards
let successCount = 0;
let failCount = 0;

shards.forEach(function(shard) {
    const success = initShard(shard);
    if (success) {
        successCount++;
    } else {
        failCount++;
    }
    sleep(3000); // Give time between initializations
});

print("\n" + "=".repeat(80));
print(`📊 Initialization Summary:`);
print(`   ✅ Successful: ${successCount}`);
print(`   ❌ Failed: ${failCount}`);
print(`   📦 Total: ${shards.length}`);

if (failCount > 0) {
    print("\n⚠️  Some shards failed, but continuing with cluster setup...");
}

print("\n✅ Shard initialization phase completed!");