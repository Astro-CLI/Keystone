# Keystone Network Automation Suite

**Extract. Parse. Modify. Rebuild. Deploy.** — Complete network automation for Packet Tracer.

This suite lets you extract running configs from any Packet Tracer topology, edit them as YAML, and rebuild the entire topology automatically. Use the **Python GUI** (`KeystoneGUI.py`) for a point-and-click experience or the **browser SPA** (`orchestrator.html`) for web-based access.

---

## Quick Start

**Choose your interface:**

### GUI (Recommended for New Users)
```bash
# Launch the Python desktop GUI
python3 KeystoneGUI.py

# Or open the browser-based SPA
#   open orchestrator.html
```

### CLI (For Scripting & Automation)
```bash
# 1. Extract a topology from Packet Tracer
#    (Run pt_analyzer.js inside PT via Extensions -> Scripting)

# 2. Parse the output to YAML
python3 scripts/pt_config_parser.py configs.txt --yaml

# 3. Edit the YAML (change IPs, hostnames, protocols, VLANs)
nano configs_topology.yaml

# 4. Generate CLI commands and PT-Builder script
python3 tools/topology_composer.py --file configs_topology.yaml

# 5. Deploy back to Packet Tracer
#    (Run main.js via Extensions -> Scripting)
```

---

## Documentation Map

| Need | Read This |
|------|-----------|
| **Getting started** | `docs/GETTING_STARTED.md` |
| **Generator reference (13 tools)** | `docs/GENERATORS_GUIDE.md` |
| **All workflows** | `docs/WORKFLOWS.md` |
| **Packet Tracer API** | `docs/PT_API_DEEP_REFERENCE.md` |
| **Troubleshooting** | `docs/TROUBLESHOOTING_GUIDE.md` |
| **Format comparisons** | `docs/FORMAT_COMPARISON.md` |

---

## Directory Structure

```
Automation/
├── README.md                      <- You are here
├── KeystoneGUI.py                 <- Python desktop GUI (PyQt6)
├── orchestrator.html              <- Browser-based SPA
├── main.js                        <- PT entry point (deployment)
├── docs/
│   ├── GETTING_STARTED.md         <- Start here!
│   ├── GENERATORS_GUIDE.md        <- All 13 generators
│   ├── WORKFLOWS.md               <- All use patterns
│   ├── PT_API_DEEP_REFERENCE.md   <- PT scripting API reference
│   ├── TROUBLESHOOTING_GUIDE.md   <- Common issues
│   └── FORMAT_COMPARISON.md       <- Format comparisons
├── web/                           <- SPA components
│   ├── app.css                    <- Cyber-obsidian design system
│   ├── tool_engine.js             <- JS generator engine (13 tools)
│   └── tool.html                  <- Individual tool SPA shell
├── generators/                    <- 13 protocol generators
│   ├── ospf_pathmaker.py          <- OSPF routing
│   ├── bgp_conductor.py           <- BGP routing
│   ├── eigrp_catalyst.py          <- EIGRP routing
│   ├── static_anchor.py           <- Static routes
│   ├── dhcp_allocator.py          <- DHCP pools
│   ├── nat_portal.py              <- NAT translations
│   ├── hsrp_sentinel.py           <- HSRP failover
│   ├── ssh_locksmith.py           <- SSH security
│   ├── vlan_weaver.py             <- VLAN + SVI configuration
│   ├── asa_shield.py              <- ASA firewall
│   ├── ip_architect.py            <- IP addressing
│   ├── cidr_architect.py          <- CIDR calculations
│   └── full_topology.py           <- Multi-layer topology composer
├── tools/                         <- Core utilities
│   ├── topology_composer.py       <- YAML -> CLI commands
│   ├── yaml_to_mainjs.py          <- YAML -> runnable main.js
│   ├── pt_file_builder.py         <- Create .pkt files from YAML
│   ├── pt_file_inspector.py       <- Inspect .pkt file contents
│   ├── pt_builder_gen.py          <- PT-Builder script generator
│   ├── format_parser.py           <- Multi-format (YAML/JSON/XML)
│   └── pt_file_builder_tests.py   <- 33-test Python/JS parity suite
├── scripts/                       <- Analysis & export scripts
│   ├── pt_analyzer.js             <- Extract configs from PT
│   ├── pt_yaml_exporter.js        <- Export topology as YAML
│   ├── pt_api_explorer.js         <- Discover PT runtime APIs
│   ├── pt_config_parser.py        <- Parse configs to structured format
│   └── pt_hidden_api_probe.js     <- Deep runtime probing
├── examples/                      <- Sample topologies
├── output/                        <- Generated files (local)
└── reference/                     <- Research & debugging
```

---

## Common Tasks

### Extract a Topology
```bash
# In Packet Tracer: Extensions -> Scripting -> Edit File Script Module
# Paste: scripts/pt_analyzer.js
# Click Run
# Copy output to configs.txt

python3 scripts/pt_config_parser.py configs.txt --yaml
```

### Modify a Topology
```bash
# Edit the generated YAML
nano configs_topology.yaml

# Then rebuild:
python3 tools/topology_composer.py --file configs_topology.yaml
```

### Generate Protocol Configs
```bash
# OSPF
python3 generators/ospf_pathmaker.py --topology examples/simple_topology.yaml

# BGP
python3 generators/bgp_conductor.py --topology examples/simple_topology.yaml

# Full multi-layer topology (OSPF + EIGRP + BGP + DHCP + NAT + HSRP + SSH)
python3 generators/full_topology.py --topology examples/simple_topology.yaml

# See all generators: docs/GENERATORS_GUIDE.md
```

### Generate PT-Builder Script (Python output matching JS)
```python
from tools.pt_builder_gen import generate_pt_builder_script
script = generate_pt_builder_script(topology, "output.pkt")
```

### Create .pkt Files Programmatically
```python
from tools.pt_file_builder import PktFileBuilder
builder = PktFileBuilder('topology.yaml')
builder.build('output.pkt')
```

### Use the Python GUI
```bash
python3 KeystoneGUI.py
```
- Top bar: Generate, Reset, Import/Export YAML
- Sidebar: Search + collapsible categories (Routing, Services, Network Design, Address Planning)
- Output tabs: CLI commands + PT-Builder script side by side
- Ctrl+Enter: Generate from current tool
- Status bar: Ready/Generated/Error feedback

---

## Features

- **Extract** -- Export running configs from live Packet Tracer topologies
- **Parse** -- Convert Cisco configs to readable YAML/JSON/XML
- **Modify** -- Edit anything: hostnames, IPs, protocols, VLANs
- **Generate** -- Auto-create CLI commands for 13 routing protocols
- **Build** -- Programmatically create `.pkt` files from YAML
- **Deploy** -- Inject configs instantly via PT scripting API
- **Dual Interface** -- Desktop GUI (PyQt6) + Browser SPA + CLI
- **PT-Builder Parity** -- Python output matches JS `tool_engine.js` exactly
- **IPv6** -- Full dual-stack support across all generators
- **Repeat** -- Cycle infinitely: extract -> edit -> rebuild -> deploy

---

## Learning Paths

### Beginner (30 min)
1. `docs/GETTING_STARTED.md` -- Overview
2. Launch `python3 KeystoneGUI.py` and try the Full Topology tool
3. Look at `examples/` folder

### Intermediate (1-2 hours)
1. `docs/GENERATORS_GUIDE.md` -- All 13 protocol generators
2. Try extracting and modifying a real PT topology
3. Generate CLI and PT-Builder output side by side

### Advanced (2-3 hours)
1. `docs/PT_API_DEEP_REFERENCE.md` -- Deep API reference
2. `docs/WORKFLOWS.md` -- Advanced workflows
3. Explore `web/tool_engine.js` and `tools/pt_builder_gen.py` source
4. Run `python3 tools/pt_file_builder_tests.py` to verify parity

---

## Pro Tips

- Start with `python3 KeystoneGUI.py` -- point and click
- YAML is 40% smaller than JSON/XML -- use it for configs
- All tools support auto-format detection (YAML/JSON/XML)
- Run `python3 tools/pt_file_builder_tests.py` to verify your setup
- Keep generated files in `output/` -- easy cleanup
- Python PT-Builder output is byte-identical to the JS SPA output
- Use Ctrl+Enter in the GUI to generate fast

---

## More Info

- **Quick Start:** `docs/GETTING_STARTED.md`
- **Generators (13):** `docs/GENERATORS_GUIDE.md`
- **Workflows:** `docs/WORKFLOWS.md`
- **API Reference:** `docs/PT_API_DEEP_REFERENCE.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING_GUIDE.md`
