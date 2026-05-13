# 🔧 Tools Overview

Keystone tools are core utilities that transform, generate, and build network topologies.

---

## 📝 **topology_composer.py** — YAML → CLI Commands

**Does:** Converts YAML/JSON/XML topology definitions into CLI commands ready to inject

**Runs on:** Your computer (command-line)

**Input:** YAML/JSON/XML topology file (e.g., `configs_topology.yaml`)

**Output:** Text file with CLI commands (e.g., `commands.txt`)

**Usage:**

```bash
# Generate CLI from YAML
python3 topology_composer.py \
  --file configs_topology.yaml \
  --output commands.txt

# Or JSON
python3 topology_composer.py \
  --file configs_topology.json \
  --output commands.txt

# Or XML
python3 topology_composer.py \
  --file configs_topology.xml \
  --output commands.txt
```

**Output example:**

```
! Configuration for Router1
enable
configure terminal
hostname Router1
!
interface GigabitEthernet0/0
 ip address 10.0.1.1 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 1.1.1.1
 network 10.0.1.0 0.0.0.255 area 0
!
ip ssh version 2
end
```

**Use when:**
- You've modified a YAML topology and want CLI commands
- You need to inject commands into live devices via PT scripting
- You're building a CI/CD pipeline that generates configs

---

## 🏗️ **yaml_to_mainjs.py** — YAML → Runnable main.js

**Does:** Converts YAML/JSON/XML topology into a self-contained Packet Tracer script

**Runs on:** Your computer (command-line)

**Input:** YAML/JSON/XML topology file

**Output:** `main.js` ready to paste into Packet Tracer

**Usage:**

```bash
# Generate main.js
python3 yaml_to_mainjs.py \
  examples/simple_topology.yaml \
  --output generated_main.js

# Then in Packet Tracer:
# Extensions → Scripting → Edit File Script Module
# Paste generated_main.js
# Click Run
```

**Advanced options:**

```bash
# Spawn devices only (no config)
python3 yaml_to_mainjs.py file.yaml --no-config

# Skip link plan output
python3 yaml_to_mainjs.py file.yaml --no-link-plan

# Custom layout
python3 yaml_to_mainjs.py file.yaml \
  --start-x 100 \
  --start-y 100 \
  --spacing-x 150 \
  --spacing-y 150 \
  --columns 3
```

**Generated script does:**
1. Spawns devices (duplicates from seed templates)
2. Positions them on canvas
3. Injects CLI configs via CommandLine API
4. Prints manual link plan

**Requirements:**
- Packet Tracer must have seed devices (one router template, one switch template, etc.)
- Must paste into an open `.pkt` file

**Use when:**
- You want to turn a YAML definition into a runnable PT script
- You need automated device creation in Packet Tracer
- You're building labs for students

---

## 📦 **pt_file_builder.py** — YAML → .pkt Files

**Does:** Creates binary `.pkt` files from topology definitions

**Runs on:** Your computer (command-line)

**Input:** YAML/JSON/XML topology file

**Output:** Binary `.pkt` file (ready to open in Packet Tracer)

**Usage:**

```bash
# Command-line
python3 pt_file_builder.py \
  --topology examples/simple_topology.yaml \
  --output my_lab.pkt

# Or in Python
from tools.pt_file_builder import PktFileBuilder

builder = PktFileBuilder('my_topology.yaml')
builder.build('output/my_lab.pkt')
```

**Features:**
- Auto-detects YAML/JSON/XML input
- Generates proper `.pkt` binary format
- Embeds device configs and topology structure
- Ready to open directly in Packet Tracer

**Use when:**
- You want to distribute pre-built labs as `.pkt` files
- You're doing batch lab generation (100s of variants)
- You need standalone topologies (no PT scripting required)

**Advantages:**
- No need to paste scripts into PT
- Students just open the file
- Works with any PT version (once file exists)
- Suitable for automation/CI-CD

---

## 🔍 **pt_file_inspector.py** — Inspect .pkt File Contents

**Does:** Opens a `.pkt` file and shows its structure/devices/configs

**Runs on:** Your computer (command-line)

**Input:** Binary `.pkt` file

**Output:** Text report of contents

**Usage:**

```bash
# Inspect a .pkt file
python3 pt_file_inspector.py my_lab.pkt

# Output:
# ═══ PT FILE STRUCTURE ═══
# File: my_lab.pkt
# Version: 8.3.2
# Total devices: 3
# 
# ═══ DEVICES ═══
# [1] Router1 (2911)
# [2] Router2 (2911)
# [3] Switch1 (2960)
```

**Use when:**
- You want to verify a `.pkt` file contents
- You need to debug generated `.pkt` files
- You're inspecting someone else's lab file

---

## 🔤 **format_parser.py** — Multi-Format Support

**Does:** Automatically detects and parses YAML/JSON/XML files

**Runs on:** Your computer (Python import or command-line)

**Input:** YAML/JSON/XML file (auto-detected by extension or content)

**Output:** Parsed Python dictionary

**Usage (as Python module):**

```python
from tools.format_parser import parse_file

# Auto-detects format by extension
topology = parse_file('my_topology.yaml')

# Or specify format
topology = parse_file('my_file.txt', format='yaml')

# Access data
for device in topology['devices']:
    print(device['hostname'])
```

**Usage (command-line):**

```bash
# Show parsed contents
python3 format_parser.py my_topology.yaml

# Convert to different format
python3 format_parser.py my_topology.yaml --output json
```

**Supported formats:**
- YAML (`.yaml`, `.yml`)
- JSON (`.json`)
- XML (`.xml`)

**Use when:**
- You're writing Python code that needs topology data
- You need to auto-convert between formats
- You're unsure what format a file is

---

## 🧪 **pt_file_builder_tests.py** — Test Suite

**Does:** Verifies that all Keystone tools work correctly

**Runs on:** Your computer (command-line)

**Usage:**

```bash
python3 pt_file_builder_tests.py
```

**Output:**

```
======================================================================
PACKET TRACER .pkt FILE BUILDER - TEST SUITE
======================================================================

[TEST 1] Encryption Algorithm
  ✓ Header matches XML length
  ✓ Encrypted data has valid structure
  ✓ Round-trip encryption/decryption

[TEST 2] XML Generation
  ✓ XML declaration present
  ✓ PT version correct

[... 30+ more tests ...]

TEST SUMMARY
============
Total Tests: 33
Passed: 33
Failed: 0
Success Rate: 100.0%

✓ All tests passed!
```

**Use when:**
- Setting up Keystone for the first time
- Verifying your Python environment is correct
- Debugging tool issues

---

## 🔄 Tool Workflow Chain

Typical tool usage:

```
┌──────────────────────────────┐
│ YAML Topology File           │
│ (manually written or from    │
│  pt_config_parser.py)        │
└──────────────┬───────────────┘
               │
        ┌──────┴──────┬──────────────┬──────────────┐
        │             │              │              │
        ↓             ↓              ↓              ↓
   ┌─────────┐  ┌──────────┐  ┌─────────────┐  ┌────────────┐
   │ yaml_to │  │topology  │  │ pt_file_    │  │ format_    │
   │ mainjs  │  │composer  │  │ builder     │  │ parser     │
   └────┬────┘  └────┬─────┘  └──────┬──────┘  └────────────┘
        │             │               │
        ↓             ↓               ↓
   ┌─────────┐  ┌──────────┐  ┌─────────────┐
   │main.js  │  │commands  │  │.pkt file    │
   │(paste   │  │.txt      │  │(ready to    │
   │in PT)   │  │(copy to  │  │open)        │
   │         │  │devices)  │  │             │
   └─────────┘  └──────────┘  └─────────────┘
```

---

## 📊 Tool Comparison

| Tool | Input | Output | Runs | Use Case |
|------|-------|--------|------|----------|
| `topology_composer` | YAML/JSON/XML | CLI commands | Computer | CLI injection |
| `yaml_to_mainjs` | YAML/JSON/XML | main.js | Computer | PT scripting |
| `pt_file_builder` | YAML/JSON/XML | .pkt file | Computer | Batch creation |
| `pt_file_inspector` | .pkt file | Report | Computer | Debugging |
| `format_parser` | Any format | Python dict | Computer/Code | Format conversion |
| `pt_file_builder_tests` | — | Test report | Computer | Verification |

---

## 📁 File Locations

```
Automation/
├── tools/
│   ├── topology_composer.py
│   ├── yaml_to_mainjs.py
│   ├── pt_file_builder.py
│   ├── pt_file_builder_enhanced.py    (advanced version)
│   ├── pt_file_builder_tests.py       (test suite)
│   ├── pt_file_inspector.py
│   ├── pt_scriptable_builder.py       (experimental)
│   ├── format_parser.py
│   └── README.md                      ← You are here
```

---

## 🆘 Troubleshooting

**python3 not found:**
- Install Python 3.7+ on your system

**YAML parsing error:**
- Check indentation (spaces, not tabs)
- Check quote syntax
- See `examples/simple_topology.yaml` for reference

**pt_file_builder fails:**
- Ensure input topology has required fields (hostname, type, interfaces)
- Run `pt_file_builder_tests.py` to verify setup

**yaml_to_mainjs generates incomplete main.js:**
- Verify YAML has all required device sections
- Try `--no-config` to spawn devices first, then add configs

---

## 📚 Learn More

- **Getting Started:** [docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md)
- **All Workflows:** [docs/WORKFLOWS.md](../docs/WORKFLOWS.md)
- **API Reference:** [docs/PT_SCRIPTING_API.md](../docs/PT_SCRIPTING_API.md)
- **Scripts:** [scripts/README.md](../scripts/README.md)
- **Generators:** [docs/GENERATORS_GUIDE.md](../docs/GENERATORS_GUIDE.md)

---

**Next:** Pick a tool and workflow from [docs/WORKFLOWS.md](../docs/WORKFLOWS.md).
