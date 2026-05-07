# PT Scripting API - Quick Reference Card

## Objects

```javascript
var activeFile = ipc.appWindow().getActiveFile();
var network = ipc.network();
var workspace = ipc.appWindow().getActiveWorkspace();
```

## Network Operations

```javascript
// READ ONLY
network.getDeviceCount()                    // → number
network.getDeviceAt(index)                  // → Device
network.getDevice(name)                     // → Device
network.getLinkCount()                      // → number
network.getLinkAt(index)                    // → Link

// CANNOT USE (don't exist):
// network.addDevice()    ❌
// network.addLink()      ❌
```

## Device Operations

```javascript
// CREATE (via activeFile)
activeFile.duplicateDevice(sourceDevice)    // → Device (new)

// POSITION
device.moveToLocationCentered(x, y)         // ✓ Recommended
device.moveToLocation(x, y)                 // Move by corner
device.getCenterXCoordinate()               // → x
device.getCenterYCoordinate()               // → y
device.getXCoordinate()                     // → x (corner)
device.getYCoordinate()                     // → y (corner)

// INFO
device.getName()                            // → "Router1"
device.getType()                            // → number (0=Router, etc)
device.getModel()                           // → "2911"
device.getSerialNumber()                    // → serial
device.getPortCount()                       // → number
device.getPort(name)                        // → Port ("0/0")
device.getPortAt(index)                     // → Port

// POWER
device.setPower(true/false)
device.getPower()                           // → true/false
device.getUpTime()                          // → seconds

// RENAME (BROKEN - don't use)
device.setName(name)                        // ❌ Doesn't work

// CUSTOM DATA
device.addCustomVar("key", "value")
device.getCustomVarStr("key")               // → "value"
device.removeCustomVar("key")
```

## File Operations

```javascript
var activeFile = ipc.appWindow().getActiveFile();

// DEVICE MANAGEMENT
activeFile.duplicateDevice(device)          // → Device (new)

// PERSISTENT STORAGE
activeFile.addScriptDataStore("key", "value")
activeFile.getScriptDataStore("key")        // → "value"
activeFile.removeScriptDataStore("key")
activeFile.getScriptDataStoreIDs()          // → [keys...]

// INFO
activeFile.getVersion()                     // → "8.2.2"
activeFile.getSavedFilename()               // → "lab.pkt"
activeFile.isActivityFile()                 // → true/false
```

## Logging

```javascript
dprint("message")                           // Console output
dprint("value: " + variable)                // String concatenation
dprint("value: " + String(obj))             // Safe conversion
```

## Error Handling

```javascript
try {
    // Code here
} catch(e) {
    dprint("ERROR: " + e.message);
}
```

## Pattern: Read All Devices

```javascript
for (var i = 0; i < ipc.network().getDeviceCount(); i++) {
    var device = ipc.network().getDeviceAt(i);
    dprint(device.getName());
}
```

## Pattern: Spawn N Devices

```javascript
var n = 5;
var template = ipc.network().getDeviceAt(0);
var activeFile = ipc.appWindow().getActiveFile();

for (var i = 0; i < n; i++) {
    activeFile.duplicateDevice(template);
    var device = ipc.network().getDeviceAt(ipc.network().getDeviceCount() - 1);
    device.moveToLocationCentered(i * 200, 100);
}
```

## Pattern: Save Data to .pkt

```javascript
var activeFile = ipc.appWindow().getActiveFile();
activeFile.addScriptDataStore("topology_name", "MyLab");
activeFile.addScriptDataStore("device_count", "7");
```

## Type Codes

```
getType() returns:
0 = Router
(other types to be documented)
```

## Coordinate System

- **Logical space:** Canvas coordinates (visible area ~0-2000 x, ~0-1500 y)
- **Physical space:** Different scale, use moveToLocationCentered() for logical
- Use positive coordinates in range 50-1500 for visible placement

## Common Mistakes

```javascript
// ❌ WRONG - gets undefined, crashes
var device = activeFile.duplicateDevice(template);
device.setName("Router1");  // setName broken!

// ✓ RIGHT
var device = activeFile.duplicateDevice(template);
dprint(device.getName());  // Just read the auto name

// ❌ WRONG - type is number not string
if (device.getType().indexOf("2911") != -1) { }

// ✓ RIGHT
var type = String(device.getType());
if (device.getModel() == "2911") { }

// ❌ WRONG - moves off screen
device.moveToLocationCentered(5000, 5000);

// ✓ RIGHT
device.moveToLocationCentered(500, 300);
```

