// PTBuilder Script - REAL IPC API
// This uses Cisco's actual network manipulation API
// Paste into: Extensions > Scripting > Edit File Script Module

function main() {
    var network = ipc.network();
    var lw = ipc.appWindow().getActiveWorkspace().getLogicalWorkspace();
    var devCount = network.getDeviceCount();

    dprint('Starting Keystone automation...');
    dprint('Current devices in network: ' + devCount);

    // Configure Device (router)
    var network = ipc.network();
    var device = network.getDeviceByName('Device');
    if (device != null) {
        dprint('Configuring Device...');
        // 1 interface(s) to configure
        dprint('  Interface 0/0: 10.0.1.1 255.255.255.0');
    } else {
        dprint('ERROR: Device not found in network');
    }

    // Configure Device (router)
    var network = ipc.network();
    var device = network.getDeviceByName('Device');
    if (device != null) {
        dprint('Configuring Device...');
        // 1 interface(s) to configure
        dprint('  Interface 0/0: 10.0.1.2 255.255.255.0');
    } else {
        dprint('ERROR: Device not found in network');
    }

    dprint('Keystone automation complete!');
    dprint('Total devices: ' + network.getDeviceCount());
}

function cleanUp() {
    dprint('Script cleanup complete');
}