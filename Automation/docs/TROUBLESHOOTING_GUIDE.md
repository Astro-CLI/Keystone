# Troubleshooting Guide

## Python GUI Issues

### "ModuleNotFoundError: No module named 'PyQt6'"

**Cause:** PyQt6 is not installed.

**Solution:**
```bash
pip install PyQt6
# Or on some systems:
pip3 install PyQt6
```

### "ModuleNotFoundError: No module named 'yaml'"

**Cause:** PyYAML is not installed.

**Solution:**
```bash
pip install pyyaml
```

### GUI shows "Unknown property" warnings in terminal

**Cause:** Qt's internal Fusion stylesheet triggers harmless "Unknown property" warnings for CSS properties it doesn't implement (e.g., `filter`, `overflow`).

**Solution:** These are **normal and harmless**. The GUI suppresses them automatically via `qInstallMessageHandler`. If you see them, your GUI is working correctly.

### GUI has overlapping elements or wrong spacing

**Cause:** Using CSS `margin` on widgets inside a `QSplitter`, or stacking widgets with `show()`/`hide()` instead of `QStackedWidget`.

**Solution:** Ensure the GUI uses `QStackedWidget` for tabbed content and layout `setContentsMargins()` instead of CSS `margin` on splitter children. If you see overlaps, check that margins are not set directly on splitter pane widgets.

### "generate_pt_builder_script() not found"

**Cause:** Running an old version of the codebase before `pt_builder_gen.py` was created.

**Solution:** Ensure you have `tools/pt_builder_gen.py` from the latest commit. This file contains `generate_pt_builder_script()` which produces PT-Builder output matching the JS SPA.

### Sidebar search doesn't filter generators

**Cause:** The search function may not be connected if running a modified or incomplete build.

**Solution:** Verify `KeystoneGUI.py` has the `_filter_tools()` method and that `search.textChanged` is connected to it. Default build should work on first run.

---

## Script Execution Issues

### "No output" - Script runs but console is silent

**Causes:**
1. Script never entered main()
2. Console window not visible
3. dprint() failing silently

**Solutions:**

```javascript
// Solution 1: Ensure main() exists and is called
function main() {
    dprint("If you see this, script runs!");
}

function cleanUp() { }

// Solution 2: Make first line of main() a dprint
function main() {
    dprint("=== SCRIPT START ===");  // If missing = script didn't run
    // rest of code
}
```

**Verify console is open:**
- Extensions → Scripting → Edit File Script Module
- Console output should appear below the code editor

---

### "ReferenceError: addDevice is not defined"

**Cause:** Trying to call `addDevice()` directly (it doesn't exist)

**WRONG:**
```javascript
addDevice("Router1", "2911", 100, 100);  // ❌ ReferenceError
```

**RIGHT:**
```javascript
var activeFile = ipc.appWindow().getActiveFile();
var template = ipc.network().getDeviceAt(0);
activeFile.duplicateDevice(template);  // ✓ Correct method
```

---

## Object Access Issues

### "Cannot read property 'getDeviceCount' of null"

**Cause:** `ipc.network()` returned null (shouldn't happen but sometimes does)

**Solution:**

```javascript
function main() {
    var network = ipc.network();
    
    if (network == null) {
        dprint("ERROR: Network object is null!");
        dprint("Try: File → Save and reload the .pkt file");
        return;
    }
    
    dprint("Network OK: " + network.getDeviceCount() + " devices");
}
```

---

### "Cannot call method 'moveToLocationCentered' of undefined"

**Cause:** Device object is null

**Solution:**

```javascript
// WRONG - crashes if no device at index
var device = ipc.network().getDeviceAt(10);
device.moveToLocationCentered(100, 100);  // ❌ Crashes if undefined

// RIGHT - check first
var device = ipc.network().getDeviceAt(10);
if (device == null) {
    dprint("ERROR: Device at index 10 not found!");
    return;
}
device.moveToLocationCentered(100, 100);  // ✓ Safe
```

---

### "Cannot call method 'getName' of undefined"

**Cause:** `duplicateDevice()` returned undefined (duplication failed)

**Symptoms:**
- Device count increases but can't access new device
- Script crashes on `newDevice.getName()`

**Solution:**

```javascript
// WRONG - doesn't check if duplication worked
var newDevice = activeFile.duplicateDevice(template);
newDevice.moveToLocationCentered(100, 100);  // ❌ Crash if undefined

// RIGHT - access via network array instead
activeFile.duplicateDevice(template);
var newIndex = ipc.network().getDeviceCount() - 1;
var newDevice = ipc.network().getDeviceAt(newIndex);

if (newDevice == null) {
    dprint("ERROR: Duplication failed!");
    return;
}

newDevice.moveToLocationCentered(100, 100);  // ✓ Works
```

---

## Type/Data Issues

### "Property 'indexOf' of object 0 is not a function"

**Cause:** `getType()` returns a number, not a string

**WRONG:**
```javascript
var type = device.getType();
if (type.indexOf("2911") != -1) { }  // ❌ Error: 0 has no indexOf
```

**RIGHT:**
```javascript
// Option 1: Convert to string
var type = String(device.getType());
if (type.indexOf("2911") != -1) { }  // ✓ Works

// Option 2: Use getModel() instead (returns string)
if (device.getModel() == "2911") { }  // ✓ Better

// Option 3: Compare numbers
if (device.getType() === 0) { }  // 0 = Router
```

---

### "Unexpected token" in script

**Cause:** JavaScript syntax error

**Common mistakes:**

```javascript
// ❌ Missing semicolon
dprint("Hello")
dprint("World")

// ✓ With semicolon
dprint("Hello");
dprint("World");

// ❌ Missing closing brace
function main() {
    dprint("Start");
    // forgot closing }

// ✓ Complete
function main() {
    dprint("Start");
}

// ❌ String not closed
dprint("Hello);  // missing closing "

// ✓ Correct
dprint("Hello");
```

---

## Movement/Position Issues

### Devices not visible on canvas

**Causes:**
1. Coordinates out of visible range
2. Using `moveToLocation()` instead of `moveToLocationCentered()`
3. Negative coordinates

**Solutions:**

```javascript
// Check valid range
dprint("Valid X: 0-2000");
dprint("Valid Y: 0-1500");

// Use moveToLocationCentered for logical space
device.moveToLocationCentered(500, 300);  // ✓ Visible

// Don't use negative coordinates
device.moveToLocationCentered(-100, -100);  // ❌ Off screen

// Don't use extreme coordinates
device.moveToLocationCentered(10000, 10000);  // ❌ Way off
```

---

### Device position doesn't match requested position

**Cause:** Requested coordinates outside visible workspace

**Solution:**

```javascript
function main() {
    var device = ipc.network().getDeviceAt(0);
    
    // Request position
    var requestX = 100;
    var requestY = 100;
    
    device.moveToLocationCentered(requestX, requestY);
    
    // Check actual position
    var actualX = device.getXCoordinate();
    var actualY = device.getYCoordinate();
    
    dprint("Requested: (" + requestX + ", " + requestY + ")");
    dprint("Actual: (" + actualX + ", " + actualY + ")");
    
    if (actualX != requestX || actualY != requestY) {
        dprint("WARNING: Position clamped to visible area!");
    }
}
```

---

## Data Persistence Issues

### Script data not saved to .pkt file

**Cause:** Not using `addScriptDataStore()` correctly

**WRONG:**
```javascript
var data = "some value";  // ❌ Just variable, not persisted
```

**RIGHT:**
```javascript
var activeFile = ipc.appWindow().getActiveFile();
activeFile.addScriptDataStore("topology_version", "1.0");  // ✓ Persisted
```

---

### Cannot retrieve stored data

**Cause:** Key name mismatch or data not stored

**Solution:**

```javascript
var activeFile = ipc.appWindow().getActiveFile();

// Store data
activeFile.addScriptDataStore("my_key", "my_value");

// Retrieve it
var retrieved = activeFile.getScriptDataStore("my_key");
dprint("Retrieved: " + retrieved);  // Should print "my_value"

// List all keys
var keys = activeFile.getScriptDataStoreIDs();
dprint("All keys: " + keys);  // Debug: see what's stored
```

---

## Performance Issues

### Script runs very slowly

**Causes:**
1. Too many loops
2. Redundant network calls

**Solutions:**

```javascript
// ❌ SLOW - calls ipc.network() every loop iteration
for (var i = 0; i < ipc.network().getDeviceCount(); i++) {
    var device = ipc.network().getDeviceAt(i);  // Expensive call
}

// ✓ FAST - calls once, stores count
var network = ipc.network();
var count = network.getDeviceCount();
for (var i = 0; i < count; i++) {
    var device = network.getDeviceAt(i);
}
```

---

## Device Naming Issues

### setName() doesn't work

**Cause:** `setName()` is broken in PT 8.2.2/9.0.0

**Status:** Confirmed limitation - not fixable

**Workaround:**

```javascript
// Can't rename, but can track names
var activeFile = ipc.appWindow().getActiveFile();

// Store desired names in .pkt file
activeFile.addScriptDataStore("device_0_desired_name", "CoreRouter");
activeFile.addScriptDataStore("device_1_desired_name", "EdgeRouter");

// Later retrieve and display
var name = activeFile.getScriptDataStore("device_0_desired_name");
dprint("Device should be: " + name);

// Or just use auto-generated names
var device = ipc.network().getDeviceAt(0);
dprint("Device name: " + device.getName());  // "Router0(1)" etc
```

---

## Network/Link Issues

### Cannot create links between devices

**Cause:** No direct `addLink()` method exists

**Status:** Under investigation - may require port manipulation

**Current Workaround:** Manual link creation in PT GUI after script runs

---

## Debugging Techniques

### Debug Technique 1: Step-by-step output

```javascript
function main() {
    dprint("=== DEBUGGING START ===");
    
    dprint("[1] Getting network...");
    var network = ipc.network();
    dprint("[1] OK - Device count: " + network.getDeviceCount());
    
    dprint("[2] Getting activeFile...");
    var activeFile = ipc.appWindow().getActiveFile();
    dprint("[2] OK - Version: " + activeFile.getVersion());
    
    dprint("[3] Getting template device...");
    var template = network.getDeviceAt(0);
    dprint("[3] OK - Template: " + template.getName());
    
    dprint("[4] Duplicating device...");
    activeFile.duplicateDevice(template);
    dprint("[4] OK - New count: " + network.getDeviceCount());
    
    dprint("=== DEBUGGING END ===");
}
```

### Debug Technique 2: Variable inspection

```javascript
function main() {
    var device = ipc.network().getDeviceAt(0);
    
    dprint("=== DEVICE INSPECTION ===");
    dprint("Name: " + device.getName());
    dprint("Type: " + device.getType());
    dprint("Model: " + device.getModel());
    dprint("X: " + device.getXCoordinate());
    dprint("Y: " + device.getYCoordinate());
    dprint("Ports: " + device.getPortCount());
    dprint("Power: " + device.getPower());
    dprint("=== END ===");
}
```

### Debug Technique 3: Exception catching

```javascript
function main() {
    try {
        // Risky code here
        var network = ipc.network();
        var device = network.getDeviceAt(0);
        device.moveToLocationCentered(100, 100);
        
    } catch(e) {
        dprint("=== EXCEPTION CAUGHT ===");
        dprint("Error: " + e.message);
        dprint("Stack: " + e.stack);
        dprint("=== END ===");
    }
}
```

---

## PT-Builder Parity Issues

### Python PT-Builder output differs from JS output

**Cause:** `extract_device_configs()` or `generate_pt_builder_script()` may have filtering or formatting differences between the Python (`pt_builder_gen.py`) and JS (`tool_engine.js`) implementations.

**Solutions:**
1. Run the parity test suite:
   ```bash
   python3 tools/pt_file_builder_tests.py
   ```

2. Check that `extract_device_configs()` in `pt_builder_gen.py` does NOT filter lines:
   - All lines should be kept (blanks, `!` comments, topology summary)
   - Only lines matching device markers (`hostname`, `Building configuration...`) control device boundaries
   - No summary-detection stop logic

3. Check that PC IP detection operates at the **device level**, not the interface level:
   - `configurePcIp()` should only be called when `d.get('dhcp')` or `d.get('ip')` is set on the device dict
   - Interface-level `dhcp`/`ip`/`mask`/`gateway` should NOT trigger `configurePcIp()`

4. Check that the full topology template has exactly 12 devices and 12 links.

### Generated .pkt file doesn't open in Packet Tracer

**Cause:** PTBuilder generates a text-based script, not a binary `.pkt` file. You must run the script inside Packet Tracer's scripting environment.

**Solution:**
```bash
# 1. Generate the PT-Builder script
python3 tools/pt_builder_gen.py --topology topology.yaml --output build_script.js

# 2. In Packet Tracer: Extensions -> Scripting -> Edit File Script Module
# 3. Paste build_script.js
# 4. Click Run
```

---

## When All Else Fails

1. **Reload the .pkt file:**
   - File → Close
   - File → Open → Select your.pkt
   - Try script again

2. **Reset PT:**
   - Close Packet Tracer completely
   - Reopen and load your .pkt file

3. **Check PT version:**
   - Help → About Packet Tracer
   - Ensure 8.2.2+ or 9.0.0+

4. **Simplify your script:**
   - Start with just `dprint("Hello");`
   - Add one line at a time
   - Find which line breaks

5. **Report issues:**
   - Document error message exactly
   - Include script code
   - Note PT version

