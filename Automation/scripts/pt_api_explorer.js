// Keystone PT API Explorer
// Paste this into Packet Tracer as main.js to enumerate the scripting surface.

var MAX_ITEMS = 200;

function main()
{
    banner();
    probeRuntime();
    probeGlobals();

    var network = getNetwork();
    if (network != null) {
        inspectNetwork(network);
    } else {
        section("NETWORK");
        log("No network object returned by ipc.network().");
    }

    var activeFile = getActiveFile();
    if (activeFile != null) {
        inspectActiveFile(activeFile);
    }

    section("SUMMARY");
    log("Discovery only. No configuration changes were made.");
}

function cleanUp()
{
    log("");
    log("Cleanup complete.");
}

function banner()
{
    log("╔══════════════════════════════════════════════════════╗");
    log("║            KEYSTONE PT API EXPLORER                 ║");
    log("╚══════════════════════════════════════════════════════╝");
    log("");
    log("Read-only inventory of the Packet Tracer scripting surface.");
    log("This script lists objects, methods, and safe runtime probes.");
    log("");
}

function section(title)
{
    log("");
    log("═══ " + title + " ═══");
}

function log(text)
{
    dprint(String(text));
}

function getNetwork()
{
    try {
        if (typeof ipc !== "undefined" && ipc != null && typeof ipc.network === "function") {
            return ipc.network();
        }
    } catch (e) {
        log("Failed to read network object: " + e.message);
    }
    return null;
}

function getActiveFile()
{
    try {
        if (typeof ipc !== "undefined" && ipc != null && typeof ipc.activeFile === "function") {
            return ipc.activeFile();
        }
    } catch (e) {
        log("Failed to read activeFile via ipc: " + e.message);
    }

    try {
        if (typeof activeFile !== "undefined" && activeFile != null) {
            return activeFile;
        }
    } catch (e2) {
        log("Failed to read activeFile global: " + e2.message);
    }

    return null;
}

function probeRuntime()
{
    section("RUNTIME / SYNTAX PROBES");
    var tests = [
        ["function call", function () { return (function (n) { return n + 1; })(1) === 2; }],
        ["object literal", function () { var o = { a: 1, b: 2 }; return o.a + o.b === 3; }],
        ["array push", function () { var a = []; a.push(1); return a.length === 1; }],
        ["for..in", function () { var c = 0, o = { a: 1, b: 2 }; for (var k in o) { c++; } return c === 2; }],
        ["try/catch", function () { try { throw new Error("x"); } catch (e) { return true; } }],
        ["regex", function () { return /pkt/i.test("PKT"); }],
        ["Date", function () { return typeof Date !== "undefined"; }],
        ["JSON", function () { return typeof JSON !== "undefined"; }],
        ["Java interop", function () { return typeof java !== "undefined"; }],
        ["Packages", function () { return typeof Packages !== "undefined"; }],
        ["Object.keys", function () { return typeof Object.keys === "function"; }],
        ["Array.isArray", function () { return typeof Array.isArray === "function"; }]
    ];

    for (var i = 0; i < tests.length; i++) {
        var name = tests[i][0];
        try {
            var ok = tests[i][1]();
            log("  " + (ok ? "✓" : "✗") + " " + name);
        } catch (e) {
            log("  ✗ " + name + " -> " + e.message);
        }
    }
}

function probeGlobals()
{
    section("GLOBAL SYMBOLS");
    var symbols = [
        ["ipc", function () { return typeof ipc !== "undefined"; }],
        ["java", function () { return typeof java !== "undefined"; }],
        ["Packages", function () { return typeof Packages !== "undefined"; }],
        ["JSON", function () { return typeof JSON !== "undefined"; }],
        ["Object", function () { return typeof Object !== "undefined"; }],
        ["Array", function () { return typeof Array !== "undefined"; }],
        ["String", function () { return typeof String !== "undefined"; }],
        ["Number", function () { return typeof Number !== "undefined"; }],
        ["Boolean", function () { return typeof Boolean !== "undefined"; }],
        ["Date", function () { return typeof Date !== "undefined"; }],
        ["RegExp", function () { return typeof RegExp !== "undefined"; }],
        ["Function", function () { return typeof Function !== "undefined"; }],
        ["Error", function () { return typeof Error !== "undefined"; }]
    ];

    for (var i = 0; i < symbols.length; i++) {
        var name = symbols[i][0];
        var status = "missing";
        try {
            status = symbols[i][1]() ? "present" : "missing";
        } catch (e) {
            status = "error: " + e.message;
        }
        log("  " + name + ": " + status);
    }

    section("GLOBAL ENUMERATION");
    dumpFunctions("global object", this);
}

function inspectNetwork(network)
{
    section("NETWORK OBJECT");
    dumpObjectInfo("network", network);

    try {
        if (typeof network.getDeviceCount === "function") {
            log("Device count: " + network.getDeviceCount());
        }
    } catch (e) {
        log("Device count error: " + e.message);
    }

    try {
        if (typeof network.getLinkCount === "function") {
            log("Link count: " + network.getLinkCount());
        }
    } catch (e2) {
        log("Link count error: " + e2.message);
    }

    dumpFunctions("network methods", network);

    var deviceCount = safeNumber(function () { return network.getDeviceCount(); }, 0);
    if (deviceCount <= 0) {
        return;
    }

    section("DEVICES");
    for (var i = 0; i < deviceCount && i < MAX_ITEMS; i++) {
        var device = null;
        try {
            device = network.getDeviceAt(i);
        } catch (e3) {
            log("  [" + i + "] error: " + e3.message);
            continue;
        }
        if (device == null) {
            log("  [" + i + "] <null>");
            continue;
        }
        inspectDevice(device, i);
    }

    tryInspectFirstLink(network);
}

function inspectDevice(device, index)
{
    section("DEVICE " + index);
    dumpObjectInfo("device[" + index + "]", device);
    dumpFunctions("device[" + index + "] methods", device);

    var name = safeString(function () { return device.getName(); }, "<no name>");
    var model = safeString(function () { return device.getModel(); }, "<no model>");
    var type = safeString(function () {
        if (typeof device.getType === "function") {
            return device.getType();
        }
        return "<no type>";
    }, "<no type>");
    var ports = safeString(function () { return device.getPortCount(); }, "<no ports>");

    log("  name: " + name);
    log("  model: " + model);
    log("  type: " + type);
    log("  ports: " + ports);

    tryInspectDescriptor(device);
    tryInspectCommandLine(device);
    tryInspectProcess(device);
    tryInspectPorts(device);
}

function tryInspectDescriptor(device)
{
    var descriptor = null;
    try {
        if (typeof device.getDescriptor === "function") {
            descriptor = device.getDescriptor();
        }
    } catch (e) {
        log("  descriptor error: " + e.message);
    }

    if (descriptor == null) {
        return;
    }

    section("DEVICE DESCRIPTOR");
    dumpObjectInfo("descriptor", descriptor);
    dumpFunctions("descriptor methods", descriptor);
}

function tryInspectCommandLine(device)
{
    var cmdLine = null;
    try {
        if (typeof device.getCommandLine === "function") {
            cmdLine = device.getCommandLine();
        }
    } catch (e) {
        log("  command line error: " + e.message);
    }

    if (cmdLine == null) {
        return;
    }

    section("COMMAND LINE");
    dumpObjectInfo("commandLine", cmdLine);
    dumpFunctions("commandLine methods", cmdLine);

    safeLogGetter("prompt", function () { return cmdLine.getPrompt(); });
    safeLogGetter("mode", function () { return cmdLine.getMode(); });
    safeLogGetter("speed", function () { return cmdLine.getSpeed(); });
}

function tryInspectProcess(device)
{
    var process = null;
    try {
        if (typeof device.getProcess === "function") {
            process = device.getProcess();
        }
    } catch (e) {
        log("  process error: " + e.message);
    }

    if (process == null) {
        return;
    }

    section("PROCESS");
    dumpObjectInfo("process", process);
    dumpFunctions("process methods", process);
}

function tryInspectPorts(device)
{
    var count = safeNumber(function () { return device.getPortCount(); }, 0);
    if (count <= 0) {
        return;
    }

    section("PORTS");
    for (var i = 0; i < count && i < 3; i++) {
        var port = null;
        try {
            port = device.getPortAt(i);
        } catch (e) {
            log("  port[" + i + "] error: " + e.message);
            continue;
        }
        if (port == null) {
            log("  port[" + i + "]: <null>");
            continue;
        }
        log("  port[" + i + "]:");
        dumpObjectInfo("port[" + i + "]", port);
        dumpFunctions("port[" + i + "] methods", port);
    }
}

function tryInspectFirstLink(network)
{
    var linkCount = safeNumber(function () { return network.getLinkCount(); }, 0);
    if (linkCount <= 0) {
        return;
    }

    var link = null;
    try {
        link = network.getLinkAt(0);
    } catch (e) {
        log("Link[0] error: " + e.message);
        return;
    }

    if (link == null) {
        return;
    }

    section("LINK[0]");
    dumpObjectInfo("link[0]", link);
    dumpFunctions("link[0] methods", link);
}

function inspectActiveFile(activeFile)
{
    section("ACTIVE FILE");
    dumpObjectInfo("activeFile", activeFile);
    dumpFunctions("activeFile methods", activeFile);

    safeLogGetter("version", function () { return activeFile.getVersion(); });
    safeLogGetter("saved filename", function () { return activeFile.getSavedFilename(); });
    safeLogGetter("activity file", function () { return activeFile.isActivityFile(); });
}

function dumpObjectInfo(label, obj)
{
    var className = safeString(function () {
        if (obj != null && typeof obj.getClassName === "function") {
            return obj.getClassName();
        }
        return "<unknown>";
    }, "<unknown>");

    var uuid = safeString(function () {
        if (obj != null && typeof obj.getObjectUuid === "function") {
            return obj.getObjectUuid();
        }
        return "<unavailable>";
    }, "<unavailable>");

    log("  " + label + ":");
    log("    class: " + className);
    log("    uuid: " + uuid);
}

function dumpFunctions(label, obj)
{
    var methods = collectFunctions(obj);
    log("  " + label + " (" + methods.length + "):");
    if (methods.length === 0) {
        log("    <none>");
        return;
    }

    for (var i = 0; i < methods.length && i < MAX_ITEMS; i++) {
        log("    " + methods[i] + "()");
    }
    if (methods.length > MAX_ITEMS) {
        log("    ... truncated at " + MAX_ITEMS + " items");
    }
}

function collectFunctions(obj)
{
    var out = [];
    if (obj == null) {
        return out;
    }

    for (var k in obj) {
        try {
            if (typeof obj[k] === "function") {
                out.push(k);
            }
        } catch (e) {
            // Ignore inaccessible members.
        }
    }

    out.sort();

    var unique = [];
    for (var i = 0; i < out.length; i++) {
        if (i === 0 || out[i] !== out[i - 1]) {
            unique.push(out[i]);
        }
    }
    return unique;
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
        return fallback + " (" + e.message + ")";
    }
}

function safeNumber(fn, fallback)
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

function safeLogGetter(label, fn)
{
    try {
        log("  " + label + ": " + String(fn()));
    } catch (e) {
        log("  " + label + ": <error: " + e.message + ">");
    }
}
