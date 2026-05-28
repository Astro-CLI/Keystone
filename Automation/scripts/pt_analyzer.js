// Keystone PT Topology Analyzer
// Reads all devices and their configs from an open topology
// Output can be copied and used to recreate/modify topologies
//
// How to use:
//   Extensions -> Scripting -> Edit File Script Module
//   Paste this code, click Run
//
// This script uses Java reflection to find the PT network object
// when ipc.network() is not available (PT 8.2.2 Script Module limitation).

function getNetwork()
{
    // Method 1: IPC (ExApp/PT Script Module with .pki declarations)
    try {
        if (typeof ipc !== "undefined" && typeof ipc.network === "function") {
            return ipc.network();
        }
    } catch(e) {}

    // Method 2: Global scope
    try { if (typeof network !== "undefined") return network; } catch(e) {}
    try { if (this && typeof this.network !== "undefined") return this.network; } catch(e) {}

    var visited = [];

    function isNetworkObj(obj)
    {
        if (!obj || typeof obj !== "object") return false;
        try {
            var m = obj.getDeviceCount;
            return typeof m === "function";
        } catch(e) { return false; }
    }

    function probeObject(obj, path)
    {
        if (!obj || typeof obj !== "object") return null;
        try {
            var id = java.lang.System.identityHashCode(obj);
            if (visited.indexOf(id) >= 0) return null;
            visited.push(id);
        } catch(e) { return null; }

        try {
            if (isNetworkObj(obj)) return obj;
        } catch(e) {}

        var cls = obj.getClass ? obj.getClass() : null;
        if (!cls) return null;
        var cn = cls.getName() || "";

        // Skip uninteresting classes
        if (cn.indexOf("java.") === 0 && cn.indexOf("javax.swing.") !== 0) return null;
        if (cn.indexOf("sun.") === 0) return null;

        // Try all declared methods on this object
        try {
            var methods = cls.getMethods();
            for (var mi = 0; mi < methods.length && mi < 200; mi++) {
                var m = methods[mi];
                var mn = m.getName();
                if (mn === "getClass" || mn === "toString" || mn === "hashCode" ||
                    mn === "equals" || mn === "notify" || mn === "wait" ||
                    mn === "notifyAll" || m.getParameterTypes().length > 0) continue;
                if (mn.indexOf("get") === 0 || mn.indexOf("is") === 0 || mn.indexOf("has") === 0) {
                    try {
                        m.setAccessible(true);
                        var val = m.invoke(obj);
                        if (val != null && val !== obj) {
                            var r = probeObject(val, path + "." + mn + "()");
                            if (r != null) return r;
                        }
                    } catch(e2) {}
                }
            }
        } catch(e) {}

        // Try all declared fields
        try {
            var fields = cls.getDeclaredFields();
            for (var fi = 0; fi < fields.length && fi < 100; fi++) {
                var f = fields[fi];
                var ft = f.getType();
                if (!ft || ft.isPrimitive() || ft === java.lang.String.class ||
                    ft === java.lang.Boolean.class || ft === java.lang.Number.class) continue;
                try {
                    f.setAccessible(true);
                    var val = f.get(obj);
                    if (val != null && val !== obj) {
                        var r = probeObject(val, path + "." + f.getName());
                        if (r != null) return r;
                    }
                } catch(e2) {}
            }
        } catch(e) {}

        // If this is a Container, scan children
        try {
            if (obj instanceof java.awt.Container) {
                var children = obj.getComponents();
                for (var ci = 0; ci < children.length; ci++) {
                    var r = probeObject(children[ci], path + ".children[" + ci + "]");
                    if (r != null) return r;
                }
            }
        } catch(e) {}

        return null;
    }

    // Method 3: Scan all AWT frames and their entire component tree
    try {
        var frames = java.awt.Frame.getFrames();
        for (var fi = 0; fi < frames.length; fi++) {
            var r = probeObject(frames[fi], "frame[" + fi + "]");
            if (r != null) return r;
        }
    } catch(e) {}

    // Method 4: Try known internal PT classes via static methods/fields
    try {
        var probeClasses = [
            "com.cisco.packettracer.PacketTracer",
            "com.cisco.packettracer.network.NetworkManager",
            "com.cisco.packettracer.NetworkManager",
            "com.cisco.packettracer.TopologyManager",
            "com.cisco.packettracer.CPD"
        ];
        for (var ci = 0; ci < probeClasses.length; ci++) {
            try {
                var clazz = java.lang.Class.forName(probeClasses[ci]);

                // Try static getInstance() -> probe result
                try {
                    var m = clazz.getMethod("getInstance");
                    var inst = m.invoke(null);
                    if (inst != null) {
                        var r = probeObject(inst, probeClasses[ci] + ".getInstance()");
                        if (r != null) return r;
                    }
                } catch(e2) {}

                // Try all static methods that return something
                try {
                    var methods = clazz.getMethods();
                    for (var mi = 0; mi < methods.length && mi < 100; mi++) {
                        var m = methods[mi];
                        if (m.getName() === "getClass" || m.getName() === "toString") continue;
                        var pt = m.getParameterTypes();
                        if (pt && pt.length > 0) continue;
                        try {
                            var val = m.invoke(null);
                            if (val != null) {
                                var r = probeObject(val, probeClasses[ci] + "." + m.getName() + "()");
                                if (r != null) return r;
                            }
                        } catch(e3) {}
                    }
                } catch(e2) {}

                // Try all static fields
                try {
                    var fields = clazz.getDeclaredFields();
                    for (var fi = 0; fi < fields.length && fi < 50; fi++) {
                        var f = fields[fi];
                        var ft = f.getType();
                        if (!ft || ft.isPrimitive() || ft === java.lang.String.class) continue;
                        try {
                            f.setAccessible(true);
                            var val = f.get(null);
                            if (val != null) {
                                var r = probeObject(val, probeClasses[ci] + "." + f.getName());
                                if (r != null) return r;
                            }
                        } catch(e3) {}
                    }
                } catch(e2) {}
            } catch(e2) {}
        }
    } catch(e) {}

    return null;
}

function main()
{
    dprint("╔════════════════════════════════════════════════════════╗");
    dprint("║         KEYSTONE - PT TOPOLOGY ANALYZER v1.0          ║");
    dprint("╚════════════════════════════════════════════════════════╝\n");
    
    try {
        var network = getNetwork();
        if (network == null) {
            dprint("\n❌ Cannot access network object.");
            dprint("");
            dprint("The Java reflection scan did not find the PT network object.");
            dprint("This may be due to PT 8.2.2's internal class structure.");
            dprint("");
            dprint("Workaround: Save your topology as a .pkt file, then use");
            dprint("the external 'ptexplorer.py' tool to convert it to XML and");
            dprint("extract the device configs. Or copy each device's running-config");
            dprint("manually from PT's CLI tab.");
            dprint("");
            return;
        }

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
            var type = "unknown";
            try { type = device.getDescriptor().getType(); } catch(e) {}
            var portCount = 0;
            try { portCount = device.getPortCount(); } catch(e) {}

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
                    dprint("  ⚠️  No CLI available");
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
        dprint("📋 Copy the configurations above and paste them into the Keystone web app.");
        dprint("    Select 'Extract from PT' tool, paste output, click GENERATE.");

    } catch(e) {
        dprint("\n❌ FATAL ERROR: " + e.message);
        try { dprint(e.stack); } catch(es) {}
    }
}

function cleanUp()
{
    dprint("\n🧹 Analyzer cleanup complete.");
}
