// Debug script to test what's available

console.log("=== KEYSTONE DEBUG ===");
console.log("Script is running!");

// Test 1: Check if functions exist
console.log("Checking available functions...");
console.log("addDevice exists?", typeof addDevice);
console.log("addLink exists?", typeof addLink);
console.log("getDevice exists?", typeof getDevice);

// Test 2: List available PT objects
console.log("Available objects:");
console.log("pt:", typeof pt);
console.log("network:", typeof network);
console.log("topology:", typeof topology);

// Test 3: Try alternative API calls
try {
    if (typeof pt !== 'undefined') {
        console.log("PT API found");
        console.log("pt.topology:", typeof pt.topology);
    }
} catch(e) {
    console.log("Error checking PT:", e.message);
}

console.log("=== END DEBUG ===");
