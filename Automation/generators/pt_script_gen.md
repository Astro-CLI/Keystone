# PT Script Generator — Option C

**Generate Packet Tracer JavaScript scripts that actually work.**

Instead of reverse-engineering the `.pkt` binary format (Option B, which Packet Tracer rejects), this tool generates JavaScript scripts that run **inside** Packet Tracer using its official IPC scripting API. No format reverse-engineering, no rejected files.

---

## Status

| Approach | Method | Works? |
|----------|--------|--------|
| **Option A** — Topology Composer | Generate CLI commands to copy-paste | ✅ Yes |
| **Option B** — PT File Builder | Write `.pkt` binary files externally | ❌ No (PT rejects them) |
| **Option C** — PT Script Gen | Generate JS for PT's scripting engine | ✅ Yes |

`pt_script_gen.py` is the **Option C** generator.

---

## Quick Start

```bash
# Generate a script from a YAML topology
python3 tools/pt_script_gen.py --file examples/my_topology.yaml --output output/my_lab.js

# Print to stdout instead
python3 tools/pt_script_gen.py --file examples/my_topology.yaml
```

Then in Packet Tracer:

1. Place **one seed device per type** required by the topology (e.g., one 2911 router, one 2960 switch) anywhere on the canvas
2. **Extensions → Scripting → Edit File Script Module**
3. Load `my_lab.js` and click **Run**
4. Watch the console: devices appear and get configured automatically
5. Manually cable the connections printed in the console
6. Delete the original seed device(s)
7. **File → Save As → my_lab.pkt**

---

## Why This Works

Packet Tracer exposes a JavaScript IPC API through its scripting module:

```javascript
ipc.network()                         // access topology
ipc.appWindow().getActiveFile()       // access the .pkt file
activeFile.duplicateDevice(seed)      // create a new device (only way to add devices)
device.moveToLocationCentered(x, y)  // position on canvas
device.getCommandLine()               // access CLI
cli.enterCommand("hostname R1")       // send IOS commands
```

The generator uses only confirmed-working API calls. Known-broken calls (like `addDevice()`, `addLink()`, `device.setName()`) are intentionally avoided.

---

## How to Use

### Step 1 — Define Your Topology

Use the same YAML format as `topology_composer.py`:

```yaml
devices:
  - hostname: R1-CORE
    type: router
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.1
        mask: 255.255.255.0
        description: "Link to R2"
    ospf:
      process_id: 1
      router_id: 1.1.1.1
      networks:
        - network: 10.0.1.0
          wildcard: 0.0.0.255
          area: 0

  - hostname: R2-EDGE
    type: router
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.2
        mask: 255.255.255.0
        description: "Link to R1"

connections:
  - from_device: R1-CORE
    from_interface: GigabitEthernet0/0/0
    to_device: R2-EDGE
    to_interface: GigabitEthernet0/0/0
```

JSON and XML input is also supported — format is auto-detected by file extension.

### Step 2 — Generate the Script

```bash
python3 tools/pt_script_gen.py --file examples/my_topology.yaml --output output/my_lab.js
```

Output:
```
OK  Script written to: output/my_lab.js
    Devices   : 2
    Connections: 1

Before running in PT, place these seed devices on the canvas:
   - One 2911  (router)

Then in Packet Tracer:
   Extensions -> Scripting -> Edit File Script Module
   Load: output/my_lab.js  ->  Click Run
```

### Step 3 — Run in Packet Tracer

1. Open Packet Tracer 8.2.2 or newer
2. Drag a **2911** from the device list onto the canvas (this is your seed device)
3. **Extensions → Scripting → Edit File Script Module**
4. Load `my_lab.js`
5. Click **Run**

Console output:
```
=== KEYSTONE TOPOLOGY BUILDER ===
Seed devices on canvas: 1
[1/4] Locating seed devices...
  OK  Found seed: 2911 (Router0)
[2/4] Creating devices...
  +  R1-CORE at (120, 120)
  +  R2-EDGE at (340, 120)
[3/4] Connections to cable manually:
  R1-CORE:GigabitEthernet0/0/0  <-->  R2-EDGE:GigabitEthernet0/0/0
[4/4] Configuring devices (this may take a moment)...
  >> R1-CORE
  OK  Router1
  >> R2-EDGE
  OK  Router2

=== TOPOLOGY COMPLETE ===
  Devices created : 2
  Connections     : 1 (see above for cabling)

Next steps:
  1. Cable the connections listed above
  2. Delete the original seed device(s)
  3. File -> Save As -> your_lab.pkt
```

---

## Supported Topology Options

```yaml
devices:
  - hostname: DEVICE-NAME         # Required: sets IOS hostname
    type: router                  # router | switch | pc | server | firewall | hub | cloud

    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.1
        mask: 255.255.255.0
        description: "Optional"
        vlan: 10                  # For VLAN interfaces (optional)

    ospf:
      process_id: 1
      router_id: 1.1.1.1
      networks:
        - network: 10.0.1.0
          wildcard: 0.0.0.255
          area: 0

    bgp:
      asn: 65001
      router_id: 1.1.1.1
      neighbors:
        - ip: 10.0.1.2
          asn: 65002
          description: "Optional"
      networks:
        - network: 10.0.0.0
          mask: 255.255.0.0

    eigrp:
      asn: 100
      router_id: 1.1.1.1          # Optional
      networks:
        - network: 10.0.1.0
          wildcard: 0.0.0.255

    dhcp:
      pools:
        - name: LAN-POOL
          network: 10.0.3.0
          mask: 255.255.255.0
          gateway: 10.0.3.1
          dns: "8.8.8.8"
      excluded:
        - start: 10.0.3.1
          end: 10.0.3.10

    hsrp:
      groups:
        - vlan: 10
          group_id: 1
          priority: 110
          virtual_ip: 10.0.10.1

    nat:
      inside_interfaces:
        - GigabitEthernet0/0/0
      outside_interfaces:
        - GigabitEthernet0/0/1
      static:
        - inside_ip: 10.0.3.50
          outside_ip: 203.0.113.100
      dynamic:
        - name: NATPOOL
          start_ip: 203.0.113.200
          end_ip: 203.0.113.220

    static_routes:
      - destination: 0.0.0.0
        mask: 0.0.0.0
        next_hop: 10.0.1.1

    ssh:
      enabled: true

    acls:
      - number: 100
        rules:
          - action: permit
            protocol: ip
            source: 10.0.1.0
            destination: any

connections:
  - from_device: R1
    from_interface: GigabitEthernet0/0/0
    to_device: R2
    to_interface: GigabitEthernet0/0/0
```

---

## Device Type Mapping

| `type` value | PT model |
|---|---|
| `router` | 2911 |
| `switch` or `switch-2960` | 2960 |
| `switch-3750` | 3750 |
| `pc` | PC-PT |
| `server` | Server-PT |
| `firewall` or `asa` | ASAv |
| `hub` | Hub-PT |
| `cloud` | Cloud-PT |

---

## Known Limitations

### Connections require manual cabling

The PT scripting API does not expose a way to programmatically add cables between devices. The generated script prints the connection list to the console so you can cable them manually in the PT GUI.

### Device names in PT GUI don't change

`device.setName()` is broken in PT's API (returns undefined). Device names in the PT canvas will be whatever PT auto-assigns (e.g., `Router0`, `Router1`). The IOS `hostname` command is still applied correctly via CLI, so the routing/switching configuration is unaffected.

### Seed devices required

The only way to create a new device via the scripting API is to duplicate an existing one. You must manually place one seed device per device type on the canvas before running the script.

### CLI timing

The script uses `java.lang.Thread.sleep()` between commands for stability. On slower machines, increase the sleep values in the generated script if commands are being dropped.

---

## Troubleshooting

**Script runs but devices don't appear**

- Make sure you're using *Edit File Script Module* (not *Builder Code Editor*)
- Confirm at least one seed device is on the canvas

**ERR Missing seed: 2911**

- Place a 2911 router on the canvas and re-run the script

**WARN No CLI available for RouterX**

- The device may still be booting. Try adding a `java.lang.Thread.sleep(2000)` before the `configureDevice()` call in the generated script

**Commands seem to be ignored**

- Increase the sleep values (100 ms → 200 ms) between `enterCommand()` calls

---

## See Also

- `tools/pt_script_gen.py` — The generator script
- `tools/topology_composer.py` — Option A: generate copy-paste CLI commands
- `examples/` — Example topology files
- `docs/OPTION_C_COMPLETE_DOCUMENTATION.md` — Full PT scripting API reference
- `docs/README_OPTION_C.md` — Option C overview
