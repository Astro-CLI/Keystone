// Keystone - CLI INJECTION v2
// Skip setup dialog, then configure

function main()
{
    dprint("=== CLI INJECTION TEST V2 ===");
    
    try {
        var network = ipc.network();
        var device = network.getDeviceAt(0);
        
        dprint("Device: " + device.getName());
        
        // Get CommandLine
        var cmdLine = device.getCommandLine();
        if (cmdLine == null) {
            dprint("ERROR: No command line!");
            return;
        }
        
        dprint("\n--- SKIPPING SETUP DIALOG ---");
        
        // Answer NO to setup dialog
        cmdLine.enterCommand("no");
        
        // Give device time to process
        java.lang.Thread.sleep(500);
        
        dprint("\n--- SENDING CONFIGURATION ---");
        
        // Now send config commands
        cmdLine.enterCommand("enable");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("configure terminal");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("hostname KEYSTONE-R1");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("interface GigabitEthernet0/0");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("ip address 10.0.0.1 255.255.255.0");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("description Link-to-R2");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("no shutdown");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("exit");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("router ospf 1");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("network 10.0.0.0 0.0.0.255 area 0");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("exit");
        java.lang.Thread.sleep(100);
        
        cmdLine.enterCommand("end");
        java.lang.Thread.sleep(200);
        
        // Read final output
        dprint("\n--- FINAL CLI STATE ---");
        var output = cmdLine.getOutput();
        dprint("Output (last 1000 chars):\n" + output.substring(Math.max(0, output.length - 1000)));
        
        var mode = cmdLine.getMode();
        dprint("\nMode: " + mode);
        
        var prompt = cmdLine.getPrompt();
        dprint("Prompt: " + prompt);
        
        // Verify config applied
        dprint("\n--- VERIFYING CONFIGURATION ---");
        cmdLine.enterCommand("show running-config interface GigabitEthernet0/0");
        java.lang.Thread.sleep(200);
        
        var output2 = cmdLine.getOutput();
        dprint("Interface config (last 500 chars):\n" + output2.substring(Math.max(0, output2.length - 500)));
        
        dprint("\n=== SUCCESS! CLI INJECTION WORKING! ===");
        
    } catch(e) {
        dprint("ERROR: " + e.message);
        dprint(e.stack);
    }
}

function cleanUp()
{
}
