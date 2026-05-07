# 📂 Keystone Automation - Directory Structure

## Overview

The `/Automation/` directory is now organized into logical subdirectories for better maintainability:

```
Automation/
├── scripts/              ← Quick analysis & extraction scripts
├── docs/                 ← All documentation
├── tools/                ← Core automation utilities
├── generators/           ← 12 specialized protocol generators
├── examples/             ← Sample topologies (YAML/JSON/XML)
├── templates/            ← Template files (empty, for future use)
├── output/               ← Generated files (.pkt, configs, commands)
├── reference/            ← Reference files & debugging info
├── main.js               ← Main PT scripting entry point
├── KeystoneBuilder.js    ← PT scripting helper
├── pt_debug.py           ← Debug utility
└── requirements.txt      ← Python dependencies
```

---

## 📁 Directory Guide

### `scripts/` — Quick Scripts & Analyzers
**Purpose**: Standalone scripts for extracting and analyzing

```
scripts/
├── pt_analyzer.js           ← Extract running configs from PT
├── pt_config_parser.py      ← Parse Cisco configs to YAML/JSON
├── magic_script.js          ← PT scripting utilities
├── real_api_test.js         ← API testing
└── test_debug.js            ← Debug helper
```

**When to use:**
- Run `pt_analyzer.js` inside Packet Tracer to extract device configs
- Run `pt_config_parser.py` to convert extracted configs to YAML

**Example usage:**
```bash
python3 scripts/pt_config_parser.py configs.txt --yaml
```

---

### `docs/` — Complete Documentation
**Purpose**: All user-facing documentation and guides

```
docs/
├── PT_ANALYZER_INDEX.md                    ← Start here
├── PT_ANALYZER_QUICKSTART.md               ← 5-minute guide
├── PT_ANALYZER_README.md                   ← Complete reference
├── PT_ANALYZER_SUMMARY.md                  ← Overview & examples
├── ANALYZER_ARCHITECTURE.txt               ← Visual diagrams
├── README_OPTION_C.md                      ← PT scripting guide
├── OPTION_C_COMPLETE_DOCUMENTATION.md      ← Full API reference
├── FORMAT_COMPARISON.md                    ← YAML vs JSON vs XML
├── API_QUICK_REFERENCE.md                  ← One-page reference
├── TROUBLESHOOTING_GUIDE.md                ← FAQ & troubleshooting
├── OPTION_B_STATUS.md                      ← Binary format research
├── README_PT_FILE_BUILDER.md               ← .pkt file generation
└── OPTION_C_PTBUILDER.md                   ← PTBuilder details
```

**Reading path:**
1. **New user?** → Start with `PT_ANALYZER_INDEX.md`
2. **Quick start?** → Read `PT_ANALYZER_QUICKSTART.md`
3. **Deep dive?** → Read `PT_ANALYZER_README.md`
4. **Visual learner?** → View `ANALYZER_ARCHITECTURE.txt`
5. **Stuck?** → Check `TROUBLESHOOTING_GUIDE.md`

---

### `tools/` — Core Automation Tools
**Purpose**: Reusable utilities for topology automation

```
tools/
├── topology_composer.py        ← Generate CLI from YAML topologies
├── format_parser.py            ← Auto-detect YAML/JSON/XML
├── pt_file_builder.py          ← Generate .pkt files (experimental)
├── pt_file_builder_enhanced.py ← Enhanced version
├── pt_file_builder_tests.py    ← Unit tests
├── pt_file_inspector.py        ← Analyze .pkt file format
├── pt_scriptable_builder.py    ← PT scripting generator v1
└── pt_scriptable_builder_real.py ← PT scripting generator v2
```

**When to use:**

- **topology_composer.py** — Convert YAML topology to CLI commands
  ```bash
  python3 tools/topology_composer.py --file examples/simple_topology.yaml
  ```

- **format_parser.py** — Used internally by other tools for multi-format support

- **pt_file_builder.py** — Experimental .pkt file generation (doesn't work with PT 8.2.2+)

**Dependencies:** Used by generators and main scripts

---

### `generators/` — Protocol-Specific Generators
**Purpose**: 12 specialized generators for different routing protocols

```
generators/
├── ospf_pathmaker.py           ← OSPF configuration
├── bgp_conductor.py            ← BGP configuration
├── eigrp_catalyst.py           ← EIGRP configuration
├── static_anchor.py            ← Static routing
├── asa_shield.py               ← Cisco ASA firewalls
├── nat_portal.py               ← NAT configuration
├── vlan_weaver.py              ← VLAN setup
├── dhcp_allocator.py           ← DHCP pools
├── hsrp_sentinel.py            ← HSRP redundancy
├── ssh_locksmith.py            ← SSH security
├── ip_architect.py             ← IP addressing
├── cidr_architect.py           ← CIDR calculations
├── [12 corresponding .md files] ← Documentation per generator
└── README.md                   ← Generator overview
```

**Pattern**: Each generator has two files:
- `name.py` — The Python script
- `name.md` — Documentation for that generator

**How to use:**
```bash
python3 generators/ospf_pathmaker.py --topology my_network.yaml
```

**Key feature**: All generators support multi-format input (YAML/JSON/XML)

---

### `examples/` — Sample Topologies & Data
**Purpose**: Ready-to-use example topologies in all 3 formats

```
examples/
├── simple_topology.{yaml,json,xml}
├── complex_topology.{yaml,json,xml}
├── example_topology.{yaml,json,xml}
├── small_office_topology.{yaml,json,xml}
├── sample_vlans.{yaml,json,xml}
└── sample_inventory.json
```

**Same data, three formats:**
- `*.yaml` — Human-readable (recommended)
- `*.json` — API-friendly
- `*.xml` — Enterprise-friendly

**Use these to:**
- Learn the topology format
- Test generators
- Test parsers
- Compare YAML/JSON/XML

**File size comparison:**
- YAML: 764 bytes (baseline)
- JSON: 1,085 bytes (+42%)
- XML: 1,110 bytes (+45%)

---

### `templates/` — Template Files
**Purpose**: Reserved for future template files

Currently empty. Future use:
- Device configuration templates
- Topology templates
- Custom configs

---

### `output/` — Generated Files
**Purpose**: Keep all generated output in one place

```
output/
├── *.pkt                    ← Generated Packet Tracer files
├── generated_config.txt     ← Generated configurations
├── generated_ospf.txt       ← OSPF-specific configs
├── commands.txt             ← CLI commands
└── [other outputs]
```

**Clean separation**: Keep output separate from inputs

**Why it matters:**
- Easy to clean up generated files (`rm output/*`)
- Won't accidentally commit test outputs
- Organized backup location

---

### `reference/` — Reference & Debug Files
**Purpose**: Research, reference materials, and debug output

```
reference/
├── Chapter4.txt              ← Research notes
├── WORKING_R1_CONFIG.txt     ← Reference configs
├── KeystoneBuilder.pts       ← PT scripting file
├── DEBUGGING_COMPLETE.txt    ← Debug logs
└── [investigation files]
```

**These are:**
- Investigation results
- Debugging output
- Historical reference
- Research notes

**Not needed** for day-to-day use

---

### `scripts/`, `main.js`, `KeystoneBuilder.js` — Root Level Scripts
**Purpose**: Main entry points for PT scripting

```
main.js                 ← Primary PT scripting module
KeystoneBuilder.js      ← PT scripting helper/builder
pt_debug.py             ← Local debugging utility
requirements.txt        ← Python dependencies
```

**main.js workflow:**
1. Load in PT: Extensions > Scripting > Edit File Script Module
2. Paste content
3. Click Run
4. View output in console

---

## 🔗 Common Workflows

### Workflow 1: Extract → Modify → Rebuild

```
1. Run scripts/pt_analyzer.js in PT
   └─ Extracts configs
   
2. Parse output with scripts/pt_config_parser.py
   └─ Creates examples/my_topology.yaml
   
3. Edit examples/my_topology.yaml
   └─ Change IPs, hostnames, etc.
   
4. Generate with tools/topology_composer.py
   └─ Creates output/commands.txt
   
5. Deploy with main.js to PT
   └─ New topology ready!
```

### Workflow 2: Generate Configs for Known Topology

```
1. Create YAML in examples/
   
2. Run generators/ospf_pathmaker.py
   └─ Creates output/ospf_config.txt
   
3. Inject via main.js
   └─ Devices configured!
```

### Workflow 3: Multi-Format Support

```
1. Have YAML in examples/simple_topology.yaml
   
2. tools/format_parser.py auto-detects and converts
   └─ Works with YAML, JSON, or XML
   
3. Used transparently by all tools
   └─ No manual conversion needed
```

---

## 📋 File Location Reference

| What you need | Where to find it |
|---------------|-----------------|
| Extract topology | `scripts/pt_analyzer.js` |
| Parse configs | `scripts/pt_config_parser.py` |
| OSPF generator | `generators/ospf_pathmaker.py` |
| BGP generator | `generators/bgp_conductor.py` |
| Example topologies | `examples/simple_topology.yaml` |
| Generate CLI commands | `tools/topology_composer.py` |
| Deploy to PT | `main.js` |
| Complete documentation | `docs/PT_ANALYZER_README.md` |
| Quick start guide | `docs/PT_ANALYZER_QUICKSTART.md` |
| Architecture diagrams | `docs/ANALYZER_ARCHITECTURE.txt` |
| Format comparison | `docs/FORMAT_COMPARISON.md` |
| Troubleshooting | `docs/TROUBLESHOOTING_GUIDE.md` |
| API reference | `docs/API_QUICK_REFERENCE.md` |
| Generated output | `output/` |
| Python dependencies | `requirements.txt` |

---

## ✨ Benefits of This Structure

| Benefit | How |
|---------|-----|
| **Easy to find files** | Organized by purpose, not alphabetically |
| **Scalable** | Adding new generators/tools is straightforward |
| **Clean separation** | Inputs, tools, outputs all separate |
| **Version control friendly** | Generated files in `output/` can be .gitignored |
| **Documentation co-located** | Docs live in `docs/`, generator docs in `generators/` |
| **Easy to share** | Can share specific directories (e.g., just `docs/`) |
| **Professional structure** | Follows standard Python project layout |
| **Backup friendly** | Can selectively backup important directories |

---

## 🛠️ Maintenance

### Adding New Generator
1. Create `generators/new_protocol_maker.py`
2. Create `generators/new_protocol_maker.md`
3. Add to `generators/README.md`
4. Update main docs

### Adding New Tool
1. Create `tools/new_tool.py`
2. Document in `docs/`
3. Link from main README

### Cleaning Up
```bash
# Remove all generated output
rm output/*

# Remove all compiled Python
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Show total size of each directory
du -sh */
```

### Backing Up
```bash
# Backup important directories
tar czf keystone-backup-$(date +%Y%m%d).tar.gz \
  docs/ examples/ generators/ tools/ scripts/ requirements.txt
```

---

## 📊 Directory Statistics

```
Total files:      95
Total size:       ~2 MB

Breakdown:
  docs/       13 files    (~400 KB)  - Documentation
  examples/   15 files    (~80 KB)   - Sample topologies
  generators/ 35 files    (~500 KB)  - Protocol generators
  tools/      8 files     (~200 KB)  - Automation tools
  scripts/    5 files     (~80 KB)   - Analysis scripts
  output/     10 files    (~600 KB)  - Generated files
  reference/  4 files     (~30 KB)   - Reference materials
  templates/  0 files     -          - (empty, reserved)
```

---

## 🚀 Getting Started

1. **Explore structure:**
   ```bash
   tree -L 2 -I '__pycache__'
   ```

2. **Read documentation:**
   - Start with `docs/PT_ANALYZER_INDEX.md`
   - Then `docs/PT_ANALYZER_QUICKSTART.md`

3. **Try an example:**
   ```bash
   python3 tools/topology_composer.py --file examples/simple_topology.yaml
   ```

4. **Explore generators:**
   ```bash
   ls generators/*.py
   ```

---

## Questions?

- **How do I...?** → Check `docs/TROUBLESHOOTING_GUIDE.md`
- **Where is...?** → This file! (You're reading it)
- **How does it work?** → See `docs/ANALYZER_ARCHITECTURE.txt`
- **Show me examples** → Visit `examples/`

**Welcome to organized automation!** ✨

