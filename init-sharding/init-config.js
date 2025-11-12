print("🔧 Step 1: Initializing Config Server Replica Set...");
print("=" .repeat(80));

// Connect to config server
const conn = new Mongo("mongo-config:27019");
const db = conn.getDB("admin");

function waitForConfigServer() {
    const maxRetries = 30;
    let retries = 0;
    
    while (retries < maxRetries) {
        try {
            db.adminCommand({ ping: 1 });
            print("✅ Config server is reachable");
            return true;
        } catch (e) {
            retries++;
            print(`⏳ Waiting for config server... (${retries}/${maxRetries})`);
            sleep(2000);
        }
    }
    
    throw new Error("❌ Config server not reachable after " + maxRetries + " attempts");
}

function initConfigReplSet() {
    try {
        const config = {
            _id: "configReplSet",
            configsvr: true,
            members: [
                { _id: 0, host: "mongo-config:27019" }
            ]
        };
        
        const result = rs.initiate(config);
        
        if (result.ok === 1) {
            print("✅ Config replica set initiated successfully");
        } else {
            print("⚠️  Initiate result: " + JSON.stringify(result));
        }
        
    } catch (e) {
        if (e.codeName === 'AlreadyInitialized') {
            print("ℹ️  Config replica set already initialized");
        } else {
            print("❌ Error initiating config replica set: " + e);
            throw e;
        }
    }
}

function waitForPrimary() {
    print("\n⏳ Waiting for config server to become PRIMARY...");
    const maxWait = 60;
    let waited = 0;
    
    while (waited < maxWait) {
        try {
            const status = rs.status();
            const primary = status.members.find(m => m.stateStr === "PRIMARY");
            
            if (primary) {
                print("✅ Config server is now PRIMARY");
                print("   Host: " + primary.name);
                return true;
            }
            
            sleep(1000);
            waited++;
            
            if (waited % 5 === 0) {
                print(`   Still waiting... (${waited}s/${maxWait}s)`);
            }
            
        } catch (e) {
            sleep(1000);
            waited++;
        }
    }
    
    throw new Error("❌ Config server did not become PRIMARY in time");
}

// Main execution
try {
    waitForConfigServer();
    initConfigReplSet();
    sleep(3000); // Give it time to start election
    waitForPrimary();
    
    print("\n📊 Final Config Server Status:");
    printjson(rs.status().members[0]);
    
    print("\n✅ Step 1 completed successfully!");
    
} catch (e) {
    print("\n❌ Step 1 failed: " + e);
    throw e;
}