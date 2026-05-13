# 📋 Scripts Overview

Keystone scripts are small, focused utilities that run inside or outside Packet Tracer.

---

## 🟦 **pt_analyzer.js** — Extract Topology & Configs

**Runs in:** Packet Tracer (via Extensions → Scripting)

**Does:** Extracts all devices, interfaces, running configs from a live `.pkt` file

**Output format:** Formatted text (copy-paste into `configs.txt`)

**Usage:**

```bash
# In Packet Tracer:
# 1. Extensions → Scripting → Edit File Script Module
# 2. Paste pt_analyzer.js
# 3. Click Run
# 4. Copy output to configs.txt
```

**Then parse:**

```bash
python3 pt_config_parser.py configs.txt --yaml
```

**Use when:**
- You need to extract a complete topology from an existing lab
- You want to modify configs and rebuild

---

## 🟨 **pt_yaml_exporter.js** — Export as Copyable YAML

**Runs in:** Packet Tracer (via Extensions → Scripting)

**Does:** Exports the live topology as YAML directly in the debug console

**Output format:** YAML block (ready to copy-paste)

**Usage:**

```bash
# In Packet Tracer:
# 1. Extensions → Scripting → Edit File Script Module
# 2. Paste pt_yaml_exporter.js
# 3. Click Run
# 4. Copy the YAML from debug console
# 5. Save as topology.yaml
```

**Use when:**
- You want the fastest path to export a topology
- You don't want intermediate files
- You're collaborating with teammates

---

## 🟧 **pt_api_explorer.js** — Discover Runtime APIs

**Runs in:** Packet Tracer (via Extensions → Scripting)

**Does:** Probes the PT runtime to discover all available functions, objects, methods

**Output:** Detailed report of what's available (or not)

**Usage:**

```bash
# In Packet Tracer:
# 1. Extensions → Scripting → Edit File Script Module
# 2. Paste pt_api_explorer.js
# 3. Click Run
# 4. Review console output
```

**Shows:**
- Syntax support (functions, objects, JSON)
- Global symbols available
- Network/Device/Port methods
- What's missing (Java, Packages, etc.)

**Use when:**
- Debugging scripting errors
- Verifying PT version capabilities
- Understanding what's possible in your PT build

---

## 🟩 **pt_hidden_api_probe.js** — Deep Runtime Probe

**Runs in:** Packet Tracer (via Extensions → Scripting)

**Does:** Recursively walks globals, prototypes, and safe methods to find everything

**Output:** Comprehensive inventory of PT runtime surface

**Usage:**

```bash
# In Packet Tracer:
# 1. Extensions → Scripting → Edit File Script Module
# 2. Paste pt_hidden_api_probe.js
# 3. Click Run
# 4. Review extensive console output
```

**Use when:**
- You need to find an undocumented API
- Researching what's actually available
- Building comprehensive API documentation

---

## 🐍 **pt_config_parser.py** — Parse Configs to Structured Format

**Runs on:** Your computer (command-line)

**Does:** Converts raw Cisco configs to YAML/JSON/XML

**Input:** Text output from `pt_analyzer.js` (in `configs.txt`)

**Output:** Structured YAML/JSON/XML (`configs_topology.yaml`)

**Usage:**

```bash
# Parse to YAML (recommended)
python3 pt_config_parser.py configs.txt --yaml

# Parse to JSON
python3 pt_config_parser.py configs.txt --json

# Parse to XML
python3 pt_config_parser.py configs.txt --xml
```

**Input file format:**

```
DEVICE: Router1
MODEL: 2911
━━━━━━━━━━━━━━━━━

Building configuration...

hostname Router1
!
interface GigabitEthernet0/0
 ip address 10.0.1.1 255.255.255.0
 no shutdown
!
router ospf 1
 network 10.0.1.0 0.0.0.255 area 0
!
end

[... more devices ...]
```

**Output file format (YAML):**

```yaml
devices:
  - hostname: Router1
    type: router
    model: 2911
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.1.1
        mask: 255.255.255.0
    routing:
      ospf:
        process_id: 1
        networks:
          - network: 10.0.1.0
            wildcard: 0.0.0.255
            area: 0
```

**Use when:**
- You've extracted a topology with `pt_analyzer.js`
- You need a structured, editable version of the configs

---

## 🔄 Script Workflow

Typical usage chain:

```
┌─────────────────────────────┐
│ pt_analyzer.js (in PT)      │ ← Extract
└──────────────┬──────────────┘
               ↓ (copy output to configs.txt)
┌─────────────────────────────┐
│ pt_config_parser.py         │ ← Parse
└──────────────┬──────────────┘
               ↓ (generates configs_topology.yaml)
┌─────────────────────────────┐
│ Edit YAML in text editor    │ ← Modify
└──────────────┬──────────────┘
               ↓ (save modified YAML)
┌─────────────────────────────┐
│ topology_composer.py        │ ← Generate
│ or yaml_to_mainjs.py        │   (in tools/)
└─────────────────────────────┘
```

---

## 📁 File Locations

```
Automation/
├── scripts/
│   ├── pt_analyzer.js
│   ├── pt_yaml_exporter.js
│   ├── pt_api_explorer.js
│   ├── pt_hidden_api_probe.js
│   ├── pt_config_parser.py
│   ├── real_api_test.js            (experimental/debug)
│   ├── test_debug.js               (experimental/debug)
│   ├── magic_script.js             (experimental/debug)
│   └── README.md                   ← You are here
```

---

## ✅ Quick Reference

| Need | Script | Runs In | Time |
|------|--------|---------|------|
| Extract topology | `pt_analyzer.js` | PT | 2 min |
| Export as YAML | `pt_yaml_exporter.js` | PT | 1 min |
| Discover APIs | `pt_api_explorer.js` | PT | 2 min |
| Deep API search | `pt_hidden_api_probe.js` | PT | 5 min |
| Parse configs | `pt_config_parser.py` | Computer | 1 min |

---

## 🔍 What Each Script Outputs

### pt_analyzer.js

```
╔════════════════════════════════════════════════════════╗
║         KEYSTONE - PT TOPOLOGY ANALYZER v1.0          ║
╚════════════════════════════════════════════════════════╝

═══ TOPOLOGY SUMMARY ═══
Total devices: 3

═══ PHASE 1: DEVICE ENUMERATION ═══
[1] Router1 (Model: 2911, Ports: 3)
[2] Router2 (Model: 2911, Ports: 3)
[3] Switch1 (Model: 2960, Ports: 24)

═══ PHASE 2: CONFIGURATION EXTRACTION ═══
[Running config for each device...]
```

### pt_yaml_exporter.js

```yaml
devices:
  - hostname: Router1
    model: 2911
    type: router
    position: {x: 100, y: 100}
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.1.1
        mask: 255.255.255.0
```

### pt_api_explorer.js

```
═══ RUNTIME / SYNTAX PROBES ═══
  ✓ function call
  ✓ object literal
  ✗ Java interop

═══ GLOBAL SYMBOLS ═══
  ipc: present
  JSON: present
  [70+ more items...]
```

### pt_config_parser.py

```
════════════════════════════════════════════════════════
PARSED CONFIGURATION SUMMARY
════════════════════════════════════════════════════════

Hostname: Router1
Interfaces configured: 3
Routing Protocols: OSPF, BGP
Services: DHCP, NAT, SSH

✅ Generated: configs_topology.yaml
```

---

## 🆘 Troubleshooting

**pt_analyzer.js won't run:**
- Ensure you have PT 6.2+ (Extensions menu required)
- Try a simple topology first to test

**pt_config_parser.py gives errors:**
- Verify Python 3.7+ is installed
- Ensure you're running from `Automation/` directory
- Check `configs.txt` format matches `pt_analyzer.js` output

**YAML output looks wrong:**
- Check the device has a running config
- Some devices (like PCs) may not have parseable configs

---

## 📚 Learn More

- **Getting Started:** [docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md)
- **All Workflows:** [docs/WORKFLOWS.md](../docs/WORKFLOWS.md)
- **API Reference:** [docs/PT_SCRIPTING_API.md](../docs/PT_SCRIPTING_API.md)
- **Tools:** [tools/README.md](../tools/README.md)

---

**Next:** Use these scripts with the tools in `tools/README.md` to complete your workflow.
