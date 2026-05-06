// Keystone - Router Spawner with Visual Verification

function main()
{
    dprint("=== KEYSTONE ROUTER SPAWNER ===");
    
    try {
        var activeFile = ipc.appWindow().getActiveFile();
        var network = ipc.network();
        
        dprint("Starting devices: " + network.getDeviceCount());
        
        var routerTemplate = network.getDeviceAt(0);
        dprint("Template: " + routerTemplate.getName());
        
        // Spawn 5 routers
        dprint("\n--- SPAWNING ROUTERS ---");
        
        for (var i = 0; i < 5; i++) {
            try {
                activeFile.duplicateDevice(routerTemplate);
                
                var newIndex = network.getDeviceCount() - 1;
                var newDevice = network.getDeviceAt(newIndex);
                var newName = newDevice.getName();
                
                // Try different movement functions
                var x = i * 200 + 50;
                var y = 50;
                
                // Try moveToLocationCentered instead
                newDevice.moveToLocationCentered(x, y);
                
                var finalX = newDevice.getXCoordinate();
                var finalY = newDevice.getYCoordinate();
                
                dprint("✓ Router spawned");
                dprint("  Name: " + newName);
                dprint("  Target: (" + x + ", " + y + ")");
                dprint("  Actual: (" + finalX + ", " + finalY + ")");
                
            } catch(e) {
                dprint("✗ Error: " + e.message);
            }
        }
        
        dprint("\n--- CHECKING CANVAS ---");
        dprint("Total devices now: " + network.getDeviceCount());
        
        // Force refresh by checking each device
        for (var i = 0; i < network.getDeviceCount(); i++) {
            var d = network.getDeviceAt(i);
            var x = d.getXCoordinate();
            var y = d.getYCoordinate();
            
            // Only show devices not at -1,-1
            if (x >= 0 || y >= 0) {
                dprint("  " + d.getName() + " at (" + x + ", " + y + ")");
            }
        }
        
        dprint("\n*** LOOK AT THE PACKET TRACER CANVAS ***");
        dprint("*** YOU SHOULD SEE ROUTERS IN A LINE ***");
        dprint("=== DONE ===");
        
    } catch(e) {
        dprint("ERROR: " + e.message);
    }
}

function cleanUp()
{
}
