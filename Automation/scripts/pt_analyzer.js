// Keystone PT Topology Analyzer
// Reads all devices and their configs from an open topology
// Output can be copied and used to recreate/modify topologies

function main()
{
    dprint("╔════════════════════════════════════════════════════════╗");
    dprint("║         KEYSTONE - PT TOPOLOGY ANALYZER v1.0          ║");
    dprint("╚════════════════════════════════════════════════════════╝\n");
    
    try {
        var network = ipc.network();
        var deviceCount = network.getDeviceCount();
        
        dprint("═══ TOPOLOGY SUMMARY ═══");
        dprint("Total devices: " + deviceCount);
        dprint("");
        
        if (deviceCount === 0) {
            dprint("⚠️  No devices found in topology!");
            return;
        }
        
        // Phase 1: Device Enumeration
        dprint("═══ PHASE 1: DEVICE ENUMERATION ═══\n");
        
        var devices = [];
        for (var i = 0; i < deviceCount; i++) {
            var device = network.getDeviceAt(i);
            var name = device.getName();
            var model = device.getModel();
            var type = device.getDescriptor().getType();
            var portCount = device.getPortCount();
            
            devices.push({
                index: i,
                name: name,
                model: model,
                type: type,
                ports: portCount,
                device: device
            });
            
            dprint("[" + (i + 1) + "] " + name);
            dprint("    Model: " + model);
            dprint("    Type: " + type);
            dprint("    Ports: " + portCount);
            dprint("");
        }
        
        // Phase 2: Configuration Extraction
        dprint("\n═══ PHASE 2: CONFIGURATION EXTRACTION ═══\n");
        
        var configs = [];
        
        for (var i = 0; i < devices.length; i++) {
            var device = devices[i].device;
            var deviceName = devices[i].name;
            
            dprint("┌─ Device " + (i + 1) + ": " + deviceName + " ─┐");
            
            try {
                var cmdLine = device.getCommandLine();
                
                if (cmdLine == null) {
                    dprint("⚠️  No CLI available");
                    dprint("└──────────────────┘\n");
                    continue;
                }
                
                // Skip setup dialog if present
                var output = cmdLine.getOutput();
                if (output.indexOf("Would you like to enter the initial configuration dialog") > -1) {
                    dprint("  ➜ Skipping setup dialog...");
                    cmdLine.enterCommand("no");
                    java.lang.Thread.sleep(300);
                }
                
                // Get running config
                dprint("  ➜ Extracting running configuration...");
                cmdLine.enterCommand("enable");
                java.lang.Thread.sleep(100);
                
                cmdLine.enterCommand("terminal length 0");
                java.lang.Thread.sleep(100);
                
                cmdLine.enterCommand("show running-config");
                java.lang.Thread.sleep(500);
                
                var config = cmdLine.getOutput();
                
                // Extract just the config part (remove boot messages)
                var configStart = config.indexOf("Building configuration");
                if (configStart === -1) {
                    configStart = config.indexOf("Current configuration");
                }
                if (configStart === -1) {
                    // Try to find first "!" character which usually starts config
                    configStart = config.indexOf("!");
                }
                
                var cleanConfig = configStart > -1 ? config.substring(configStart) : config;
                
                configs.push({
                    device: deviceName,
                    model: devices[i].model,
                    config: cleanConfig,
                    size: cleanConfig.length
                });
                
                dprint("  ✓ Retrieved " + cleanConfig.length + " bytes");
                dprint("└──────────────────┘\n");
                
            } catch(e) {
                dprint("  ✗ Error: " + e.message);
                dprint("└──────────────────┘\n");
            }
        }
        
        // Phase 3: Output Formatted Report
        dprint("\n╔════════════════════════════════════════════════════════╗");
        dprint("║              EXTRACTED CONFIGURATIONS                ║");
        dprint("╚════════════════════════════════════════════════════════╝\n");
        
        for (var i = 0; i < configs.length; i++) {
            var cfg = configs[i];
            dprint("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            dprint("DEVICE: " + cfg.device);
            dprint("MODEL: " + cfg.model);
            dprint("SIZE: " + cfg.size + " bytes");
            dprint("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
            dprint(cfg.config);
            dprint("\n");
        }
        
        // Phase 4: Summary Statistics
        dprint("\n╔════════════════════════════════════════════════════════╗");
        dprint("║                  SUMMARY STATISTICS                  ║");
        dprint("╚════════════════════════════════════════════════════════╝\n");
        
        var totalConfigSize = 0;
        for (var i = 0; i < configs.length; i++) {
            totalConfigSize += configs[i].size;
        }
        
        dprint("Total devices analyzed: " + configs.length);
        dprint("Total config size: " + totalConfigSize + " bytes");
        dprint("Average per device: " + Math.round(totalConfigSize / configs.length) + " bytes");
        dprint("");
        dprint("✨ Configuration extraction complete!");
        dprint("📋 Copy the configurations above and send them to recreate this topology.");
        
    } catch(e) {
        dprint("\n❌ FATAL ERROR: " + e.message);
        dprint(e.stack);
    }
}

function cleanUp()
{
    dprint("\n🧹 Analyzer cleanup complete.");
}
