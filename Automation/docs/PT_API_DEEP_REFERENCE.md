# Packet Tracer Scripting API Reference

> This reference applies to all Keystone interfaces: Python GUI (`KeystoneGUI.py`), browser SPA (`orchestrator.html`), and CLI tools. The PT scripting API is consumed by `main.js` for deployment and by `tools/yaml_to_mainjs.py` for script generation.

This document summarizes the Packet Tracer scripting surface currently observed in Keystone testing. It combines:

- methods documented in the existing Keystone docs
- methods verified by runtime probing in Packet Tracer 8.2.2 and 9.0.0
- practical usage patterns that worked in real tests

## 1. Runtime model

Packet Tracer scripts run as JavaScript modules loaded through:

```text
Extensions -> Scripting -> Edit File Script Module
```

Expected entry points:

```javascript
function main() { }
function cleanUp() { }
```

Important runtime notes:

- `java` is not available in the tested runtime
- `Packages` is not available in the tested runtime
- `dprint()` is the primary logging mechanism
- `ipc` is available and is the main gateway into Packet Tracer objects
- `ipc.network()` is read-only for topology discovery
- device creation is done through `ipc.appWindow().getActiveFile().duplicateDevice(...)`

## 2. Canonical object chain

```javascript
var appWindow = ipc.appWindow();
var activeFile = appWindow.getActiveFile();
var network = ipc.network();
```

Recommended access pattern:

1. Get `appWindow`
2. Get `activeFile`
3. Get `network`
4. Read or duplicate devices
5. Position new devices with `moveToLocationCentered()`

## 3. Global helpers

These are present in the PT runtime, but they are not the main topology API.

| Name | Purpose |
|---|---|
| `$createHttpServer()` | Internal HTTP helper |
| `$createTcpServer()` | Internal TCP helper |
| `$createTcpSocket()` | Internal TCP socket helper |
| `$createUdpSocket()` | Internal UDP socket helper |
| `$createWebSocket()` | Internal WebSocket helper |
| `dprint()` | Console logging |
| `setTimeout()` / `setInterval()` | Script timers |
| `setSimulationTimeout()` / `setSimulationInterval()` | Simulation timers |
| `guid()` | UUID generation helper |

Most of the other global names exposed by the probe are internal PT runtime objects or JavaScript built-ins. They are not stable API targets.

## 4. `ipc` object

`ipc` is the gateway object returned by the runtime.

### Common accessors

| Method | Purpose | Notes |
|---|---|---|
| `ipc.network()` | Returns the current `Network` object | Main topology entry point |
| `ipc.appWindow()` | Returns the main application window | Use this to reach `activeFile` |

## 5. `appWindow` object

Observed as `ipc.appWindow()`.

### File and workspace access

| Method | Purpose | Usage |
|---|---|---|
| `getActiveFile()` | Returns the currently open `.pkt` file object | `var activeFile = ipc.appWindow().getActiveFile();` |
| `getActiveWorkspace()` | Returns the active UI workspace | Useful for UI-level inspection |
| `getNetworkComponentBox()` | Returns the component palette / network box | UI exploration |
| `getWebViewManager()` | Returns the web view manager | Advanced / internal |
| `getPLSwitch()` | Returns the PL switch object | Internal / advanced |
| `getRSSwitch()` | Returns the RS switch object | Internal / advanced |
| `getUserCreatedPDU()` | Returns user-created PDU object | Simulation-related |

### File operations observed in probe output

These are exposed on the application/window side of the runtime:

| Method | Purpose |
|---|---|
| `fileNew()` | Create a new file |
| `fileOpen()` | Open a file |
| `fileOpenFromBytes()` | Open from bytes |
| `fileOpenFromURL()` | Open from URL |
| `fileSave()` | Save |
| `fileSaveAs()` | Save as |
| `fileSaveAsAsync()` | Async save as |
| `fileSaveAsNoPrompt()` | Save without prompt |
| `fileSaveAsPkz()` | Save in PKZ form |
| `fileSaveAsPkzAsync()` | Async PKZ save |
| `fileSaveAsync()` | Async save |
| `fileSaveToBytes()` | Serialize to bytes |
| `fileSaveToBytesAsync()` | Async byte serialization |
| `fileActivityWizard()` | Activity wizard support |
| `promptFileOpenFolder()` | File picker / open-folder prompt |

### Window helpers observed

| Method | Purpose |
|---|---|
| `setWindowTitle()` | Set the application title |
| `setWindowGeometry()` | Set the window size/position |
| `getWidth()` / `getHeight()` | Window dimensions |
| `getX()` / `getY()` | Window position |
| `setVisible()` | Show or hide a UI element |

## 6. `Network` object

Returned by `ipc.network()`.

### Verified methods

| Method | Purpose | Usage |
|---|---|---|
| `getClassName()` | Object class name | Debugging |
| `getDeviceCount()` | Number of devices | Loop over devices |
| `getDeviceAt(index)` | Get device by index | Main way to enumerate devices |
| `getDevice(name)` | Get device by name | Name-based lookup |
| `getLinkCount()` | Number of links | Enumerate links |
| `getLinkAt(index)` | Get link by index | Inspect connections |
| `getTotalDeviceAttributeValue(key)` | Aggregate attribute value | Advanced analysis |
| `registerEvent(...)` | Register event | Advanced |
| `registerObjectEvent(...)` | Register object event | Advanced |
| `unregisterEvent(...)` | Remove event | Advanced |
| `unregisterObjectEvent(...)` | Remove object event | Advanced |

### Usage example

```javascript
var network = ipc.network();
var count = network.getDeviceCount();

for (var i = 0; i < count; i++) {
    var device = network.getDeviceAt(i);
    dprint(device.getName());
}
```

### Important limitations

- `network.addDevice()` does not exist
- `network.addLink()` does not exist
- topology changes should happen through `activeFile`

## 7. `activeFile` object

Returned by `ipc.appWindow().getActiveFile()`.

### Verified methods

| Method | Purpose | Usage |
|---|---|---|
| `duplicateDevice(sourceDevice)` | Duplicate a template device | Main creation path |
| `getMainNetwork()` | Returns the main network | Alternate access to topology |
| `getMainSimulation()` | Returns the main simulation | Simulation-level access |
| `addScript(name, code)` | Store script code in the file | Script persistence |
| `getScript(name)` | Retrieve stored script | Script persistence |
| `removeScript(name)` | Delete stored script | Script persistence |
| `addScriptDataStore(key, value)` | Save key/value data into the file | Persistent metadata |
| `getScriptDataStore(key)` | Read persisted value | Persistent metadata |
| `getScriptDataStoreIDs()` | List stored keys | Persistent metadata |
| `removeScriptDataStore(key)` | Delete persisted value | Persistent metadata |
| `getVersion()` | PT version | Debugging |
| `getSavedFilename()` | Current file name | Debugging |
| `getNetworkDescription()` | File description | Metadata |
| `setNetworkDescription(text)` | Update file description | Metadata |
| `isActivityFile()` | Activity vs regular file | Debugging |
| `getOptions()` | File options | Advanced |

### Device creation pattern

```javascript
var appWindow = ipc.appWindow();
var activeFile = appWindow.getActiveFile();
var network = ipc.network();
var template = network.getDeviceAt(0);

activeFile.duplicateDevice(template);

var newDevice = network.getDeviceAt(network.getDeviceCount() - 1);
newDevice.moveToLocationCentered(100, 100);
```

### Why this works

`duplicateDevice()` is the only proven creation path. New devices are usually retrieved from the network immediately after duplication.

## 8. `Device` object

Returned by `network.getDeviceAt(index)`, `network.getDevice(name)`, and related APIs.

### Core information methods

| Method | Purpose |
|---|---|
| `getName()` | Device name |
| `getType()` | Numeric device type code |
| `getClassName()` | Class name |
| `getModel()` | Model string |
| `getSerialNumber()` | Serial number |
| `getObjectUuid()` | UUID |

### Location methods

| Method | Purpose |
|---|---|
| `getXCoordinate()` | Corner X in logical space |
| `getYCoordinate()` | Corner Y in logical space |
| `getCenterXCoordinate()` | Center X |
| `getCenterYCoordinate()` | Center Y |
| `getAreaLeftX()` | Bounding box left |
| `getAreaTopY()` | Bounding box top |
| `getXPhysicalWS()` | Physical workspace X |
| `getYPhysicalWS()` | Physical workspace Y |
| `moveToLocation(x, y)` | Move by corner |
| `moveToLocationCentered(x, y)` | Move by center (recommended) |
| `moveByInPhysicalWS(dx, dy)` | Move in physical workspace |
| `moveToLocInPhysicalWS(x, y)` | Move in physical workspace |

### Power / runtime methods

| Method | Purpose |
|---|---|
| `getPower()` | Power state |
| `setPower(bool)` | Turn device on/off |
| `getUpTime()` | Uptime |
| `setTime(value)` | Set device time |

### Configuration / UI methods

| Method | Purpose |
|---|---|
| `getPortCount()` | Number of ports |
| `getPort(name)` | Get a port by name |
| `getPortAt(index)` | Get a port by index |
| `getPorts()` | Get all ports |
| `getUsbPortCount()` | USB port count |
| `getUsbPortAt(index)` | Get USB port by index |
| `getCommandLine()` | CLI object |
| `getDescriptor()` | Device descriptor |
| `getProcess()` | Device process object |
| `getRootModule()` | Root hardware module |
| `addModule(name)` | Add hardware module |
| `removeModule(name)` | Remove hardware module |
| `addUserDesktopApp(path)` | Add desktop app |
| `removeUserDesktopApp(name)` | Remove desktop app |
| `setCustomInterface(name)` | Change custom interface |
| `setCustomLogicalImage(path)` | Change logical icon |
| `setCustomPhysicalImage(path)` | Change physical icon |
| `addCustomVar(key, value)` | Store custom data |
| `removeCustomVar(key)` | Remove custom data |
| `hasCustomVar(key)` | Test custom data |
| `getCustomVarStr(key)` | Read custom data |
| `serializeToXml()` | Serialize device state |
| `playSound(path)` | Play sound |
| `stopSound()` | Stop sound |
| `stopSounds()` | Stop all sounds |
| `runProject()` | Run embedded project |
| `stopProject()` | Stop embedded project |
| `runCodeInProject()` | Run code in embedded project |

### Important limitations

- `setName()` is unreliable / effectively broken in current tests
- use auto-generated names or store your own naming metadata

## 9. `Port` object

Returned by `device.getPortAt(index)` or `device.getPort(name)`.

### Useful methods

| Method | Purpose |
|---|---|
| `getName()` | Port name |
| `getPortNameNumber()` | Port number text |
| `getType()` | Port type |
| `getOwnerDevice()` | Owning device |
| `getLink()` | Connected link |
| `getRemotePortName()` | Remote port name |
| `isPortUp()` | Link status |
| `isProtocolUp()` | Protocol status |
| `isPowerOn()` | Power state |
| `isEthernetPort()` | Ethernet test |
| `isWirelessPort()` | Wireless test |
| `getIpAddress()` | IPv4 address |
| `getSubnetMask()` | IPv4 mask |
| `getIpv6Address()` | IPv6 address |
| `getIpv6Addresses()` | IPv6 addresses |
| `getMacAddress()` | MAC address |
| `getBandwidth()` | Bandwidth |
| `setBandwidth(value)` | Set bandwidth |
| `setDescription(text)` | Set description |
| `setIpSubnetMask(mask)` | Set IPv4 mask |
| `setDefaultGateway(ip)` | Set default gateway |
| `setDhcpClientFlag(bool)` | Enable DHCP client |
| `setIpv6Enabled(bool)` | Enable IPv6 |

### Advanced protocol-related methods

The port object exposes many routing and interface knobs, including OSPF, EIGRP, NAT, ACL, and keepalive fields. These are useful for deep inspection and may be relevant for automation if PT accepts them in your topology.

Examples observed:

- `setOspfCost(...)`
- `setOspfHelloInterval(...)`
- `setOspfDeadInterval(...)`
- `setOspfPriority(...)`
- `setRipPassive(...)`
- `setRipSplitHorizon(...)`
- `setNatMode(...)`

## 10. `CommandLine` object

Returned by `device.getCommandLine()`.

### Purpose

The CLI object is the most useful path for device configuration injection.

### Common methods

| Method | Purpose |
|---|---|
| `enterCommand(text)` | Send a command |
| `enterChar(ch)` | Send a character |
| `flush()` | Flush buffered output |
| `getOutput()` | Read accumulated CLI output |
| `getCommandInput()` | Current command input |
| `getCurrentHistory()` | Current history buffer |
| `getConfigHistory()` | Config history |
| `getUserHistory()` | User history |
| `getPrompt()` | Current prompt text |
| `getMode()` | Current CLI mode |
| `getSpeed()` | Terminal speed |
| `getTelnetClientCount()` | Telnet client count |
| `getTelnetClientAt(index)` | Telnet client |

### Usage example

```javascript
var cmdLine = device.getCommandLine();
cmdLine.enterCommand("enable");
cmdLine.enterCommand("configure terminal");
cmdLine.enterCommand("hostname Router1");
```

### Notes

- setup dialogs may need to be answered with `no`
- short delays may be needed between commands
- `java.lang.Thread.sleep()` is not available in the tested runtime
- use PT-specific timers or synchronous flows instead

## 11. `Descriptor` object

Returned by `device.getDescriptor()`.

### Purpose

This object describes the device model and supported hardware.

### Useful methods

| Method | Purpose |
|---|---|
| `getClassName()` | Class name |
| `getModel()` | Model string |
| `getType()` | Type |
| `getRootModule()` | Root module |
| `getSupportedModuleTypeCount()` | Number of supported module types |
| `getSupportedModuleTypeAt(index)` | Supported module type |
| `getSpecifiedModelCount()` | Number of specified models |
| `getSpecifiedModelAt(index)` | Specific model |
| `getRequiredScriptModuleCount()` | Number of required modules |
| `getRequiredScriptModuleAt(index)` | Required script module |
| `isModelSupported(model)` | Model compatibility |
| `isModuleTypeSupported(type)` | Module compatibility |
| `isExistSpecifiedModel(model)` | Existence test |

### Why it matters

Descriptor data is the closest thing to a device capability map. If PT ever exposes a native spawn or template builder path, this is a likely place for it.

## 12. `Process` object

Returned by `device.getProcess()`.

### Observed behavior

The process object is much smaller than the device/port objects.

Typical method surface:

- `getClassName()`
- `getObjectUuid()`
- `getOwnerDevice()`
- `registerEvent(...)`
- `registerDelegate(...)`
- `unregisterEvent(...)`
- `unregisterDelegate(...)`

## 13. `Workspace` and UI helpers

`ipc.appWindow().getActiveWorkspace()` is available, but the exact public method surface should be probed per PT version.

Useful UI-related methods observed in runtime output:

- `getMainViewAreaWidth()`
- `getMainViewAreaHeight()`
- `getToolBar()`
- `getLogicalToolbar()`
- `getPhysicalToolbar()`
- `getSimulationToolbar()`
- `getRealtimeToolbar()`
- `getMenuBar()`
- `getDialogManager()`

These are mainly for UI inspection and internal tooling.

## 14. High-Level Automation API (PTBuilder)

Keystone integrates with the **PTBuilder** extension to provide a clean, high-level JavaScript API for network creation. These functions are the recommended path for all Keystone topology generation.

### Topology Creation

| Function | Signature | Purpose |
|---|---|---|
| `addDevice` | `(name, model, x, y)` | Spawns a device at coordinates and sets its hostname. |
| `addModule` | `(name, model, slot)` | Power-cycles device and installs a hardware module (e.g. HWIC-2T). |
| `addLink` | `(d1, p1, d2, p2, type)` | Creates a physical connection (straight/cross/serial). |

### Device Configuration

| Function | Signature | Purpose |
|---|---|---|
| `configurePcIp` | `(name, dhcp, ip, mask, gw, dns)` | Sets IP parameters for PCs/End devices. |
| `configureIosDevice` | `(name, commands)` | Injects bulk CLI commands into a Router or Switch. |

### Verified Device Types

| Keyword | PT Model | Note |
|---|---|---|
| `router` | `2911` | Standard ISR G2 |
| `switch` | `2960-24TT` | Standard L2 Catalyst |
| `pc` | `PC-PT` | Generic End Device |
| `server` | `Server-PT` | Generic Server |
| `asa` | `5506-X` | Security Appliance |

## 15. Proven Automation Recipe

The following pattern is used for the **7-Step Granular Workflow** in Keystone:

```javascript
// STEP 1: Core Mesh
addDevice("R1", "2911", 400, 100);
addDevice("R2", "2911", 200, 300);
addLink("R1", "GigabitEthernet0/0", "R2", "GigabitEthernet0/0", "straight");

// STEP 2: Modules
addModule("R1", "HWIC-2T", "0");

// ... subsequent steps for distribution, access, and CLI injection
```

## 16. Known Limits and Best Practices

1. **Ordering Matters:** Always `addDevice` before calling `addModule` or `addLink` for that device.
2. **Module Timing:** `addModule` performs a power-cycle. When using CLI injection, wait for the device to finish "booting" if not using `skipBoot()` logic inside the helper.
3. **Port Naming:** Use full port names (e.g., `GigabitEthernet0/0`) or use the Keystone `normalize_port()` helper in the generator to ensure compatibility.
4. **CLI Injection:** For complex configurations, ensure `no`, `enable`, and `conf t` are the first commands sent to clear the initial setup dialog.

