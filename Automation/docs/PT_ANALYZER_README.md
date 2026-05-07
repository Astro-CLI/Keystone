# 🔍 Keystone PT Analyzer - Extract & Recreate Network Topologies

## Overview

The PT Analyzer is a two-part system that extracts running configurations from Packet Tracer topologies and converts them into modifiable automation files.

### Components

1. **`pt_analyzer.js`** — Runs inside Packet Tracer
   - Enumerates all devices in topology
   - Extracts running config from each device
   - Outputs in copy-paste format

2. **`pt_config_parser.py`** — Runs on your computer
   - Parses extracted Cisco configs
   - Generates YAML/JSON topology definitions
   - Ready for topology_composer to rebuild

---

## Workflow

```
┌──────────────────────────────────┐
│   Open existing PT topology      │
└──────────────────────────────────┘
                 ↓
┌──────────────────────────────────┐
│   Run pt_analyzer.js in PT       │ ← Extensions > Scripting > Edit File Script Module
│   (shows all configs)            │
└──────────────────────────────────┘
                 ↓
┌──────────────────────────────────┐
│   Copy config output             │
│   Paste into configs.txt          │
└──────────────────────────────────┘
                 ↓
┌──────────────────────────────────┐
│   Run pt_config_parser.py        │
│   python3 pt_config_parser.py \  │
│     configs.txt --yaml           │
└──────────────────────────────────┘
                 ↓
┌──────────────────────────────────┐
│   Edit generated YAML file       │
│   Change IPs, VLANs, hostnames   │
└──────────────────────────────────┘
                 ↓
┌──────────────────────────────────┐
│   Use topology_composer.py       │
│   Generate new configs           │
└──────────────────────────────────┘
                 ↓
┌──────────────────────────────────┐
│   Use CLI injection to build     │
│   the new topology               │
└──────────────────────────────────┘
```

---

## Step 1: Run Analyzer in Packet Tracer

### Steps:

1. Open your topology in Packet Tracer
2. Go to **Extensions → Scripting → Edit File Script Module**
3. Replace everything with the code from `pt_analyzer.js`
4. Click **Run**
5. Wait for completion

### Expected Output:

```
╔════════════════════════════════════════════════════════╗
║         KEYSTONE - PT TOPOLOGY ANALYZER v1.0          ║
╚════════════════════════════════════════════════════════╝

═══ TOPOLOGY SUMMARY ═══
Total devices: 3

═══ PHASE 1: DEVICE ENUMERATION ═══

[1] Router1
    Model: 2911
    Type: 0
    Ports: 3

[2] Router2
    Model: 2911
    Type: 0
    Ports: 3

[3] Switch1
    Model: 2960
    Type: 1
    Ports: 24

═══ PHASE 2: CONFIGURATION EXTRACTION ═══

┌─ Device 1: Router1 ─┐
  ➜ Extracting running configuration...
  ✓ Retrieved 1248 bytes
└──────────────────┘

...

╔════════════════════════════════════════════════════════╗
║              EXTRACTED CONFIGURATIONS                ║
╚════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEVICE: Router1
MODEL: 2911
SIZE: 1248 bytes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Building configuration...

Current configuration : 1248 bytes
!
version 15.1
service timestamps debug datetime msec
service timestamps log datetime msec
!
hostname Router1
!
interface GigabitEthernet0/0
 ip address 10.0.1.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
router ospf 1
 network 10.0.1.0 0.0.0.255 area 0
!
ip ssh version 2
!
end

[... more devices ...]
```

---

## Step 2: Copy Output to File

1. **Select all** the output (Ctrl+A)
2. **Copy** (Ctrl+C)
3. Create file: `my_topology_configs.txt`
4. **Paste** the entire output
5. Save

---

## Step 3: Parse with Python Script

```bash
cd /home/astro/Documents/GitHub/Keystone/Automation

# Parse to YAML (recommended)
python3 pt_config_parser.py my_topology_configs.txt --yaml

# Or parse to JSON
python3 pt_config_parser.py my_topology_configs.txt --json
```

### Output:

```
════════════════════════════════════════════════════════
PARSED CONFIGURATION SUMMARY
════════════════════════════════════════════════════════

Hostname: Router1
Interfaces configured: 3
  - GigabitEthernet0/0
    IP: 10.0.1.1/24
    Description: Link to Router2
  - GigabitEthernet0/1
    IP: 192.168.1.1/24
    Description: WAN Link

Routing Protocols:
  ✓ OSPF (PID: 1)
  ✓ BGP (ASN: 65001)

Services:
  ✓ DHCP (2 pools)
  ✓ NAT
  ✓ SSH

════════════════════════════════════════════════════════

✅ Generated: my_topology_configs_topology.yaml
```

---

## Step 4: Edit Generated YAML

The generated YAML is fully editable:

```yaml
# Auto-generated topology from PT config analysis
# Device: Router1
devices:
  - hostname: Router1          # ← Change this
    type: router
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.1.1           # ← Change this
        mask: 255.255.255.0    # ← Or this
        description: "Link to Router2"
    ospf:
      process_id: 1
      router_id: 1.1.1.1       # ← Or this
      networks:
        - network: 10.0.1.0
          wildcard: 0.0.0.255
          area: 0
```

### Common Modifications:

**Change hostname:**
```yaml
hostname: MyNewRouter          # ← New name
```

**Change IP addresses:**
```yaml
ip: 10.0.2.1                   # ← New IP
mask: 255.255.255.0
```

**Change OSPF router ID:**
```yaml
router_id: 10.0.2.1            # ← New RID
```

**Add VLAN:**
```yaml
interfaces:
  - name: VLAN10
    vlan: 10
    ip: 10.10.0.1
    mask: 255.255.255.0
```

---

## Step 5: Rebuild Topology

### Using topology_composer.py:

```bash
python3 topology_composer.py \
  --file my_topology_configs_topology.yaml \
  --output new_commands.txt
```

This generates CLI commands ready to paste into the devices.

---

## Step 6: Deploy with CLI Injection

Use main.js (updated version) to:

1. Spawn devices from template
2. Inject configs via CommandLine API
3. Verify they match original

```javascript
// Example: Spawn and configure
var device = activeFile.duplicateDevice(templateRouter);
device.moveToLocationCentered(100, 100);

var cmdLine = device.getCommandLine();
cmdLine.enterCommand("no");
java.lang.Thread.sleep(300);

cmdLine.enterCommand("enable");
cmdLine.enterCommand("configure terminal");
cmdLine.enterCommand("hostname NewRouterName");
// ... more commands
```

---

## What Gets Extracted

### ✅ Fully Supported

- **Hostnames** — `hostname`
- **Interface configs** — IP, mask, description, shutdown
- **OSPF** — Process ID, router ID, networks, areas
- **BGP** — ASN, neighbors, networks
- **DHCP** — Pools, excluded ranges, gateways, DNS
- **NAT** — Inside/outside interfaces, static/dynamic rules
- **SSH** — Enable/disable, version
- **Static routes** — Destination, mask, next hop

### ⚠️ Partially Supported

- **EIGRP** — Basic parsing, needs testing
- **HSRP** — Detected but needs validation
- **ACLs** — Detected but structure needs work
- **VLANs** — Detected but needs enhancement

### ❌ Not Yet Supported

- Advanced QoS policies
- Prefix lists and route maps
- Complex security zones
- Custom modules
- Audio/visual configs

---

## Example: Full Workflow

### Original Topology
```yaml
# Extracted from PT using analyzer
hostname: ISP-GATEWAY
interfaces:
  - name: GigabitEthernet0/0
    ip: 203.0.113.1
    mask: 255.255.255.0
```

### Modified for New Deployment
```yaml
# Edit the extracted file
hostname: BRANCH-GATEWAY   # ← Changed
interfaces:
  - name: GigabitEthernet0/0
    ip: 192.168.1.1        # ← Changed
    mask: 255.255.255.0
```

### Result
When rebuilt with topology_composer + CLI injection, you get an identical topology with new parameters—no manual config entry required!

---

## Troubleshooting

### No configs extracted?
- ✓ Check device has CLI available (not all device types do)
- ✓ Verify Extensions → Scripting is enabled
- ✓ Make sure devices are powered on

### Parser throws errors?
- ✓ Make sure config text is copied completely
- ✓ Check file encoding is UTF-8
- ✓ Verify no special characters in paths

### Generated YAML has errors?
- ✓ Run: `python3 -m yaml <file.yaml>` to validate
- ✓ Check indentation (YAML is whitespace-sensitive)
- ✓ Verify all quotes are matched

### CLI injection doesn't work?
- ✓ Device might still be in setup dialog—add `no` first
- ✓ Use proper thread sleep times (100-300ms)
- ✓ Check command spelling against your IOS version

---

## Performance Notes

- **Small topology (3-5 devices)**: ~15-30 seconds
- **Medium topology (10-15 devices)**: ~1-2 minutes
- **Large topology (30+ devices)**: ~3-5 minutes

Each device requires:
- CLI connection
- Setup dialog skip
- `show running-config` execution
- Output capture

---

## Future Enhancements

- [ ] Support multi-context configurations
- [ ] Extract device-specific module configs
- [ ] Automatic VLAN detection and mapping
- [ ] Dry-run before applying configs
- [ ] Config diff tool
- [ ] Backup original before modifications
- [ ] Parallel device processing

---

## License

Part of Keystone network automation suite. Use freely for network labs and testing.

