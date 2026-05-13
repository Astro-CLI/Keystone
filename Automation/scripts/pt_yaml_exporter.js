// Keystone PT YAML Exporter
// Paste this into Packet Tracer as main.js.
//
// It scans the currently open topology and prints YAML syntax directly
// to the debug console so you can copy the output into a .yaml file.
//
// Output includes:
// - devices
// - positions
// - ports
// - startup_config blocks when available
// - best-effort connections

var MAX_PORTS_PER_DEVICE = 24;
var MAX_COMMAND_OUTPUT = 9000;

function main()
{
    banner();

    try {
        var network = ipc.network();
        var appWindow = ipc.appWindow();
        var activeFile = appWindow.getActiveFile();

        if (network == null) {
            dprint("ERROR: network object is null");
            return;
        }

        var deviceCount = safeCount(function () { return network.getDeviceCount(); }, 0);
        var linkCount = safeCount(function () { return network.getLinkCount(); }, 0);

        dprint("# Keystone Packet Tracer YAML Export");
        dprint("# Source file: " + safeString(function () { return activeFile.getSavedFilename(); }, "unknown"));
        dprint("# Devices: " + deviceCount);
        dprint("# Links: " + linkCount);
        dprint("devices:");

        var devices = snapshotDevices(network);
        for (var i = 0; i < devices.length; i++) {
            emitDeviceYaml(devices[i], "  ");
        }

        if (devices.length > 0) {
            var connections = snapshotConnections(devices);
            if (connections.length > 0) {
                dprint("connections:");
                for (var j = 0; j < connections.length; j++) {
                    emitConnectionYaml(connections[j], "  ");
                }
            }
        }

        dprint("");
        dprint("# End of YAML export");
        dprint("# If you want a cleaner topology-only version, remove startup_config blocks.");
    } catch (e) {
        dprint("ERROR: " + e.message);
        if (e && e.stack) {
            dprint(e.stack);
        }
    }
}

function cleanUp()
{
    dprint("YAML export cleanup complete");
}

function banner()
{
    dprint("╔══════════════════════════════════════════════════════╗");
    dprint("║            KEYSTONE PT YAML EXPORTER               ║");
    dprint("╚══════════════════════════════════════════════════════╝");
    dprint("");
}

function snapshotDevices(network)
{
    var out = [];
    var count = safeCount(function () { return network.getDeviceCount(); }, 0);

    for (var i = 0; i < count; i++) {
        var device = null;
        try {
            device = network.getDeviceAt(i);
        } catch (e) {
            continue;
        }
        if (device == null) {
            continue;
        }
        out.push(buildDeviceRecord(device, i));
    }

    return out;
}

function buildDeviceRecord(device, index)
{
    var record = {
        name: safeString(function () { return device.getName(); }, "Device" + index),
        model: safeString(function () { return device.getModel(); }, "unknown"),
        type: inferType(safeString(function () { return device.getModel(); }, ""), safeString(function () { return device.getName(); }, "")),
        position: {
            x: safeNumber(function () { return device.getXCoordinate(); }, 0),
            y: safeNumber(function () { return device.getYCoordinate(); }, 0)
        },
        ports: snapshotPorts(device)
    };

    var description = safeString(function () {
        return getPropertyValue(device, "description");
    }, "");
    if (description) {
        record.description = description;
    }

    var startupConfig = getStartupConfig(device);
    if (startupConfig) {
        record.startup_config = startupConfig;
    }

    return record;
}

function snapshotPorts(device)
{
    var ports = [];
    var count = safeCount(function () { return device.getPortCount(); }, 0);
    var limit = Math.min(count, MAX_PORTS_PER_DEVICE);

    for (var i = 0; i < limit; i++) {
        var port = null;
        try {
            port = device.getPortAt(i);
        } catch (e) {
            continue;
        }
        if (port == null) {
            continue;
        }
        ports.push(buildPortRecord(port));
    }

    return ports;
}

function buildPortRecord(port)
{
    var record = {
        name: safeString(function () { return port.getName(); }, ""),
        type: safeString(function () { return port.getType(); }, ""),
        up: safeBool(function () { return port.isPortUp(); }),
        protocol_up: safeBool(function () { return port.isProtocolUp(); }),
        power_on: safeBool(function () { return port.isPowerOn(); })
    };

    var remotePort = safeString(function () { return port.getRemotePortName(); }, "");
    if (remotePort) {
        record.remote_port = remotePort;
    }

    var ip = safeString(function () { return port.getIpAddress(); }, "");
    if (ip) {
        record.ip = ip;
    }

    var mask = safeString(function () { return port.getSubnetMask(); }, "");
    if (mask) {
        record.mask = mask;
    }

    var mac = safeString(function () { return port.getMacAddress(); }, "");
    if (mac) {
        record.mac = mac;
    }

    var owner = safeObject(function () { return port.getOwnerDevice(); });
    if (owner != null) {
        record.owner = safeString(function () { return owner.getName(); }, "");
    }

    return record;
}

function snapshotConnections(devices)
{
    var out = [];
    var seen = {};

    for (var i = 0; i < devices.length; i++) {
        var device = devices[i];
        for (var p = 0; p < device.ports.length; p++) {
            var port = device.ports[p];
            if (!port.remote_port && !port.up && !port.protocol_up) {
                continue;
            }

            var key = device.name + "|" + port.name + "|" + (port.remote_port || "");
            if (seen[key]) {
                continue;
            }
            seen[key] = true;

            out.push({
                source: device.name + ":" + port.name,
                target_port: port.remote_port || "",
                source_ip: port.ip || "",
                source_mac: port.mac || "",
                note: port.remote_port ? "linked" : "unresolved"
            });
        }
    }

    return out;
}

function emitDeviceYaml(device, indent)
{
    dprint(indent + "- name: " + yamlScalar(device.name));
    dprint(indent + "  type: " + yamlScalar(device.type));
    dprint(indent + "  model: " + yamlScalar(device.model));

    if (device.description) {
        dprint(indent + "  description: " + yamlScalar(device.description));
    }

    if (device.position) {
        dprint(indent + "  position:");
        dprint(indent + "    x: " + device.position.x);
        dprint(indent + "    y: " + device.position.y);
    }

    dprint(indent + "  ports:");
    for (var i = 0; i < device.ports.length; i++) {
        emitPortYaml(device.ports[i], indent + "    ");
    }

    if (device.startup_config) {
        dprint(indent + "  startup_config: |-" );
        emitBlock(device.startup_config, indent + "    ");
    }
}

function emitPortYaml(port, indent)
{
    dprint(indent + "- name: " + yamlScalar(port.name));
    dprint(indent + "  type: " + yamlScalar(port.type));
    dprint(indent + "  up: " + boolScalar(port.up));
    dprint(indent + "  protocol_up: " + boolScalar(port.protocol_up));
    dprint(indent + "  power_on: " + boolScalar(port.power_on));

    if (port.remote_port) {
        dprint(indent + "  remote_port: " + yamlScalar(port.remote_port));
    }
    if (port.ip) {
        dprint(indent + "  ip: " + yamlScalar(port.ip));
    }
    if (port.mask) {
        dprint(indent + "  mask: " + yamlScalar(port.mask));
    }
    if (port.mac) {
        dprint(indent + "  mac: " + yamlScalar(port.mac));
    }
    if (port.owner) {
        dprint(indent + "  owner: " + yamlScalar(port.owner));
    }
}

function emitConnectionYaml(conn, indent)
{
    dprint(indent + "- source: " + yamlScalar(conn.source));
    dprint(indent + "  target_port: " + yamlScalar(conn.target_port));
    if (conn.source_ip) {
        dprint(indent + "  source_ip: " + yamlScalar(conn.source_ip));
    }
    if (conn.source_mac) {
        dprint(indent + "  source_mac: " + yamlScalar(conn.source_mac));
    }
    dprint(indent + "  note: " + yamlScalar(conn.note));
}

function emitBlock(text, indent)
{
    var lines = String(text).split(/\r?\n/);
    for (var i = 0; i < lines.length; i++) {
        dprint(indent + lines[i]);
    }
}

function getStartupConfig(device)
{
    var cmdLine = null;
    try {
        cmdLine = device.getCommandLine();
    } catch (e) {
        return "";
    }

    if (cmdLine == null) {
        return "";
    }

    try {
        var output = "";
        try {
            output = String(cmdLine.getOutput());
        } catch (e1) {
            output = "";
        }

        if (output.indexOf("Would you like to enter the initial configuration dialog") !== -1) {
            cmdLine.enterCommand("no");
            waitMs(300);
        }

        cmdLine.enterCommand("enable");
        waitMs(120);
        cmdLine.enterCommand("terminal length 0");
        waitMs(120);
        cmdLine.enterCommand("show running-config");
        waitMs(300);

        var raw = String(cmdLine.getOutput());
        return extractRunningConfig(raw);
    } catch (e2) {
        return "";
    }
}

function extractRunningConfig(output)
{
    var start = output.indexOf("Building configuration");
    if (start === -1) {
        start = output.indexOf("Current configuration");
    }
    if (start === -1) {
        start = output.indexOf("!");
    }
    if (start === -1) {
        return "";
    }

    var config = output.substring(start);
    return config.replace(/\r/g, "").trim();
}

function inferType(model, name)
{
    var text = String(model + " " + name).toLowerCase();
    if (text.indexOf("router") !== -1 || text.indexOf("2911") !== -1 || text.indexOf("1941") !== -1) {
        return "router";
    }
    if (text.indexOf("switch") !== -1 || text.indexOf("2960") !== -1 || text.indexOf("3750") !== -1 || text.indexOf("2950") !== -1) {
        return "switch";
    }
    if (text.indexOf("server") !== -1) {
        return "server";
    }
    if (text.indexOf("pc") !== -1) {
        return "pc";
    }
    if (text.indexOf("asa") !== -1 || text.indexOf("firewall") !== -1) {
        return "asa";
    }
    if (text.indexOf("cloud") !== -1) {
        return "cloud";
    }
    if (text.indexOf("hub") !== -1) {
        return "hub";
    }
    if (text.indexOf("printer") !== -1) {
        return "printer";
    }
    if (text.indexOf("phone") !== -1) {
        return "phone";
    }
    if (text.indexOf("wireless") !== -1 || text.indexOf("access point") !== -1) {
        return "wireless";
    }
    return "router";
}

function yamlScalar(value)
{
    if (value == null) {
        return "null";
    }

    var str = String(value);
    return "'" + str.replace(/'/g, "''") + "'";
}

function boolScalar(value)
{
    return value ? "true" : "false";
}

function safeString(fn, fallback)
{
    try {
        var value = fn();
        if (value == null) {
            return fallback;
        }
        return String(value);
    } catch (e) {
        return fallback;
    }
}

function safeObject(fn)
{
    try {
        return fn();
    } catch (e) {
        return null;
    }
}

function safeNumber(fn, fallback)
{
    try {
        var value = fn();
        var num = parseFloat(value);
        if (isNaN(num)) {
            return fallback;
        }
        return num;
    } catch (e) {
        return fallback;
    }
}

function safeBool(fn)
{
    try {
        return !!fn();
    } catch (e) {
        return false;
    }
}

function safeCount(fn, fallback)
{
    try {
        var value = fn();
        var num = parseInt(value, 10);
        if (isNaN(num)) {
            return fallback;
        }
        return num;
    } catch (e) {
        return fallback;
    }
}

function getPropertyValue(obj, propName)
{
    try {
        if (obj != null && typeof obj[propName] !== "undefined") {
            return obj[propName];
        }
    } catch (e) {
        return "";
    }
    return "";
}

function waitMs(ms)
{
    var start = new Date().getTime();
    while ((new Date().getTime() - start) < ms) { }
}
