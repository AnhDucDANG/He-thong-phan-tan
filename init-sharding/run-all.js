print("\n");
print("╔═══════════════════════════════════════════════════════════════╗");
print("║   MongoDB Sharded Cluster Initialization Script              ║");
print("║   Rental System - Distributed Database Setup                 ║");
print("╚═══════════════════════════════════════════════════════════════╝");
print("\n");

const startTime = new Date();

try {
    // Step 1: Initialize Config Server
    print("🚀 STEP 1/4: Initializing Config Server");
    load("/scripts/init-config.js");
    print("\n" + "=".repeat(80) + "\n");
    sleep(5000);
    
    // Step 2: Initialize Shards
    print("🚀 STEP 2/4: Initializing All Shards");
    load("/scripts/init-shards.js");
    print("\n" + "=".repeat(80) + "\n");
    sleep(10000);
    
    // Step 3: Add Shards and Configure
    print("🚀 STEP 3/4: Adding Shards to Cluster");
    load("/scripts/add-shards.js");
    print("\n" + "=".repeat(80) + "\n");
    sleep(5000);
    
    // Step 4: Create Indexes
    print("🚀 STEP 4/4: Creating Indexes");
    load("/scripts/setup-indexes.js");
    print("\n" + "=".repeat(80) + "\n");
    
    const endTime = new Date();
    const duration = (endTime - startTime) / 1000;
    
    print("\n");
    print("╔═══════════════════════════════════════════════════════════════╗");
    print("║                   ✅ SUCCESS                                  ║");
    print("║   All initialization steps completed successfully!           ║");
    print("║                                                               ║");
    print(`║   Duration: ${duration.toFixed(2)} seconds                              ║`);
    print("╚═══════════════════════════════════════════════════════════════╝");
    print("\n");
    
    print("📊 Next Steps:");
    print("  1. Test API: http://localhost:8000/health");
    print("  2. Check sharding: docker exec -it mongos-router mongosh --eval 'sh.status()'");
    print("  3. Insert test data via Postman");
    print("\n");
    
} catch (e) {
    print("\n");
    print("╔═══════════════════════════════════════════════════════════════╗");
    print("║                   ❌ FAILED                                   ║");
    print("║   Initialization failed!                                      ║");
    print("╚═══════════════════════════════════════════════════════════════╝");
    print("\nError: " + e);
    print("\nCheck logs with: docker logs mongo-init-sharding");
    throw e;
}