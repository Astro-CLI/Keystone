// Keystone PT Hidden API Probe
// Paste this into Packet Tracer as main.js
// Goal: aggressively enumerate reachable scripting objects, prototype members,
// hidden/non-enumerable properties, and keyword-matching methods.

var MAX_NODES = 120;
var MAX_DEPTH = 3;
var MAX_PROPS = 250;
var MAX_CALLS = 80;

var KEYWORDS = [
    "add", "create", "spawn", "build", "builder", "duplicate", "clone",
    "device", "link", "port", "module", "model", "template", "topology",
    "network", "workspace", "window", "file", "script", "simulation",
    "active", "main", "descriptor", "root", "command", "cli", "console",
    "process", "event", "delegate", "register", "unregister", "remove",
    "set", "get", "open", "close", "save", "load", "copy", "paste",
    "connect", "attach", "route", "ospf", "bgp", "eigrp", "vlan", "dhcp",
    "nat", "asa", "ssh", "ip", "subnet", "interface", "port", "physical",
    "logical", "hidden", "internal"
];

var SAFE_CALL_KEYWORDS = [
    "get", "active", "main", "window", "workspace", "network", "file",
    "simulation", "descriptor", "commandline", "process", "port", "link",
    "device", "module", "root", "model", "template", "script"
];

function main()
{
    banner();
    probeRuntime();

    var roots = collectRoots();
    deepExplore(roots);

    section("SUMMARY");
    log("Nodes explored: " + stats.nodes);
    log("Keyword hits: " + stats.hits);
    log("Safe calls made: " + stats.calls);
    log("Discovery only. No configuration changes were made.");
}

function cleanUp()
{
    log("");
    log("Cleanup complete.");
}

var stats = {
    nodes: 0,
    hits: 0,
    calls: 0
};

function banner()
{
    log("╔══════════════════════════════════════════════════════╗");
    log("║         KEYSTONE PT HIDDEN API PROBE                ║");
    log("╚══════════════════════════════════════════════════════╝");
    log("");
    log("Recursive, read-only search for hidden PT scripting surface.");
    log("Walks globals, prototypes, and safe zero-arg getters.");
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

function probeRuntime()
{
    section("RUNTIME PROBES");
    var tests = [
        ["Object.getOwnPropertyNames", function () { return typeof Object.getOwnPropertyNames === "function"; }],
        ["Object.getPrototypeOf", function () { return typeof Object.getPrototypeOf === "function"; }],
        ["Array.isArray", function () { return typeof Array.isArray === "function"; }],
        ["JSON", function () { return typeof JSON !== "undefined"; }],
        ["java", function () { return typeof java !== "undefined"; }],
        ["Packages", function () { return typeof Packages !== "undefined"; }]
    ];

    for (var i = 0; i < tests.length; i++) {
        try {
            log("  " + (tests[i][1]() ? "✓" : "✗") + " " + tests[i][0]);
        } catch (e) {
            log("  ✗ " + tests[i][0] + " -> " + e.message);
        }
    }
}

function collectRoots()
{
    section("ROOT OBJECTS");
    var roots = [];

    addRoot(roots, "global", this);

    if (typeof ipc !== "undefined" && ipc != null) {
        addRoot(roots, "ipc", ipc);
        var network = tryAddInvoke(roots, "ipc.network()", ipc, "network");
        var appWindow = tryAddInvoke(roots, "ipc.appWindow()", ipc, "appWindow");
        var activeFile = tryAddInvoke(roots, "ipc.activeFile()", ipc, "activeFile");
        var workspace = tryAddInvoke(roots, "ipc.workspace()", ipc, "workspace");

        if (appWindow != null) {
            tryAddInvoke(roots, "appWindow.getActiveFile()", appWindow, "getActiveFile");
            tryAddInvoke(roots, "appWindow.getActiveWorkspace()", appWindow, "getActiveWorkspace");
            tryAddInvoke(roots, "appWindow.getNetworkComponentBox()", appWindow, "getNetworkComponentBox");
            tryAddInvoke(roots, "appWindow.getWebViewManager()", appWindow, "getWebViewManager");
            tryAddInvoke(roots, "appWindow.getPLSwitch()", appWindow, "getPLSwitch");
            tryAddInvoke(roots, "appWindow.getRSSwitch()", appWindow, "getRSSwitch");
            tryAddInvoke(roots, "appWindow.getUserCreatedPDU()", appWindow, "getUserCreatedPDU");
        }

        if (activeFile != null) {
            tryAddInvoke(roots, "activeFile.getMainNetwork()", activeFile, "getMainNetwork");
            tryAddInvoke(roots, "activeFile.getMainSimulation()", activeFile, "getMainSimulation");
        }

        if (workspace != null) {
            tryAddInvoke(roots, "workspace.getMainNetwork()", workspace, "getMainNetwork");
        }
    } else {
        log("  ipc: missing");
    }

    return roots;
}

function addRoot(roots, name, obj)
{
    if (obj == null) {
        return;
    }
    roots.push({
        name: name,
        obj: obj,
        depth: 0
    });
    log("  + " + name);
}

function tryAddInvoke(roots, label, obj, methodName)
{
    try {
        if (typeof obj[methodName] === "function" && obj[methodName].length === 0) {
            var value = obj[methodName]();
            if (value != null) {
                log("  + " + label + " => " + objectLabel(value));
                roots.push({
                    name: label,
                    obj: value,
                    depth: 0
                });
                stats.calls++;
                return value;
            }
        }
    } catch (e) {
        log("  ! " + label + " error: " + e.message);
    }
    return null;
}

function deepExplore(roots)
{
    var queue = roots.slice(0);
    var seen = [];

    while (queue.length > 0 && stats.nodes < MAX_NODES) {
        var item = queue.shift();
        if (item == null || item.obj == null) {
            continue;
        }
        if (containsRef(seen, item.obj)) {
            continue;
        }
        seen.push(item.obj);
        inspectNode(item, queue, seen);
    }
}

function inspectNode(item, queue, seen)
{
    stats.nodes++;

    var obj = item.obj;
    var name = item.name;
    var depth = item.depth;
    var className = safeString(function () {
        return (obj && typeof obj.getClassName === "function") ? obj.getClassName() : "<unknown>";
    }, "<unknown>");

    section("NODE " + stats.nodes);
    log("  path: " + name);
    log("  depth: " + depth);
    log("  class: " + className);
    log("  type: " + typeof obj);
    log("  own+enum props: " + safeCountProperties(obj));

    dumpKeywordHits(obj, name);
    dumpProperties(obj, name, depth, queue, seen);
    inspectPrototypeChain(obj, name, queue, seen, depth);
}

function dumpKeywordHits(obj, path)
{
    var names = collectNames(obj);
    var hits = findKeywordHits(names);

    if (hits.length === 0) {
        return;
    }

    section("KEYWORD HITS @ " + path);
    for (var i = 0; i < hits.length; i++) {
        log("  * " + hits[i]);
        stats.hits++;
    }
}

function dumpProperties(obj, path, depth, queue, seen)
{
    var names = collectNames(obj);
    if (names.length === 0) {
        return;
    }

    section("PROPERTIES @ " + path);
    var shown = 0;
    for (var i = 0; i < names.length && shown < MAX_PROPS; i++) {
        var prop = names[i];
        var value;
        try {
            value = obj[prop];
        } catch (e) {
            log("  " + prop + ": <error: " + e.message + ">");
            continue;
        }

        var kind = typeof value;
        var line = "  " + prop + " : " + kind;
        if (kind === "function") {
            line += " / arity " + safeArity(value);
        } else if (kind === "object") {
            line += " / " + objectLabel(value);
        } else {
            line += " / " + safePreview(value);
        }
        log(line);
        shown++;

        if (depth < MAX_DEPTH) {
            maybeEnqueue(queue, seen, path + "." + prop, value, depth + 1);
        }

        if (kind === "function") {
            maybeCallGetter(queue, seen, path + "." + prop, value, depth + 1, prop);
        }
    }

    if (names.length > MAX_PROPS) {
        log("  ... truncated at " + MAX_PROPS + " properties");
    }
}

function inspectPrototypeChain(obj, path, queue, seen, depth)
{
    if (typeof Object.getPrototypeOf !== "function") {
        return;
    }

    var current = obj;
    var level = 0;
    while (current != null && level < 4) {
        var proto = null;
        try {
            proto = Object.getPrototypeOf(current);
        } catch (e) {
            break;
        }

        if (proto == null) {
            break;
        }

        var protoPath = path + ".__proto__" + (level === 0 ? "" : level);
        if (!containsRef(seen, proto)) {
            seen.push(proto);
            queue.push({
                name: protoPath,
                obj: proto,
                depth: depth + 1
            });
        }

        section("PROTOTYPE " + protoPath);
        log("  class: " + safeString(function () {
            return (typeof proto.getClassName === "function") ? proto.getClassName() : "<unknown>";
        }, "<unknown>"));
        log("  own+enum props: " + safeCountProperties(proto));
        log("  keyword hits: " + joinHits(findKeywordHits(collectNames(proto))));

        current = proto;
        level++;
    }
}

function maybeEnqueue(queue, seen, path, value, depth)
{
    if (value == null) {
        return;
    }

    var type = typeof value;
    if (type !== "object" && type !== "function") {
        return;
    }

    if (containsRef(seen, value)) {
        return;
    }

    queue.push({
        name: path,
        obj: value,
        depth: depth
    });
}

function maybeCallGetter(queue, seen, path, fn, depth, propName)
{
    if (stats.calls >= MAX_CALLS) {
        return;
    }

    if (fn == null) {
        return;
    }

    var normalized = normalize(propName);
    if (!containsSafeKeyword(normalized)) {
        return;
    }

    if (safeArity(fn) !== 0) {
        return;
    }

    try {
        var value = fn();
        stats.calls++;
        if (value == null) {
            return;
        }

        log("  -> " + propName + "() => " + objectLabel(value));
        maybeEnqueue(queue, seen, path + "()", value, depth);
    } catch (e) {
        log("  -> " + propName + "() ! " + e.message);
    }
}

function collectNames(obj)
{
    var names = [];
    if (obj == null) {
        return names;
    }

    if (typeof Object.getOwnPropertyNames === "function") {
        try {
            var own = Object.getOwnPropertyNames(obj);
            mergeUnique(names, own);
        } catch (e) {
            // ignore
        }
    }

    try {
        for (var k in obj) {
            mergeUnique(names, [k]);
        }
    } catch (e2) {
        // ignore
    }

    names.sort();
    return names;
}

function mergeUnique(target, items)
{
    for (var i = 0; i < items.length; i++) {
        var item = String(items[i]);
        if (!containsString(target, item)) {
            target.push(item);
        }
    }
}

function containsString(arr, value)
{
    for (var i = 0; i < arr.length; i++) {
        if (arr[i] === value) {
            return true;
        }
    }
    return false;
}

function findKeywordHits(names)
{
    var hits = [];
    for (var i = 0; i < names.length; i++) {
        var name = names[i];
        var norm = normalize(name);
        for (var j = 0; j < KEYWORDS.length; j++) {
            var key = normalize(KEYWORDS[j]);
            if (norm.indexOf(key) !== -1 || key.indexOf(norm) !== -1) {
                hits.push(name + "  [~ " + KEYWORDS[j] + "]");
                break;
            }
        }
    }
    return hits;
}

function joinHits(hits)
{
    if (hits.length === 0) {
        return "<none>";
    }
    var out = "";
    for (var i = 0; i < hits.length; i++) {
        out += (i === 0 ? "" : ", ") + hits[i];
    }
    return out;
}

function containsSafeKeyword(normalizedName)
{
    for (var i = 0; i < SAFE_CALL_KEYWORDS.length; i++) {
        if (normalizedName.indexOf(normalize(SAFE_CALL_KEYWORDS[i])) !== -1) {
            return true;
        }
    }
    return false;
}

function normalize(text)
{
    return String(text).toLowerCase().replace(/[^a-z0-9]/g, "");
}

function safeArity(fn)
{
    try {
        return fn.length;
    } catch (e) {
        return -1;
    }
}

function safeCountProperties(obj)
{
    var names = collectNames(obj);
    return names.length;
}

function safePreview(value)
{
    try {
        if (value === null) {
            return "null";
        }
        if (typeof value === "undefined") {
            return "undefined";
        }
        var text = String(value);
        if (text.length > 80) {
            text = text.substring(0, 80) + "...";
        }
        return text;
    } catch (e) {
        return "<preview error>";
    }
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

function objectLabel(value)
{
    if (value == null) {
        return "null";
    }

    var type = typeof value;
    if (type !== "object" && type !== "function") {
        return type;
    }

    var label = type;
    try {
        if (typeof value.getClassName === "function") {
            label += ":" + value.getClassName();
        }
    } catch (e) {
        // ignore
    }

    try {
        if (typeof value.getName === "function") {
            label += "[" + value.getName() + "]";
        }
    } catch (e2) {
        // ignore
    }

    return label;
}

function containsRef(arr, obj)
{
    for (var i = 0; i < arr.length; i++) {
        if (arr[i] === obj) {
            return true;
        }
    }
    return false;
}
