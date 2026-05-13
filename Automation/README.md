# 🎯 Keystone Network Automation Suite

**Extract. Parse. Modify. Rebuild. Deploy.** — Complete network automation for Packet Tracer.

This suite lets you extract running configs from any Packet Tracer topology, edit them as YAML, and rebuild the entire topology automatically.

---

## ⚡ In 60 Seconds

```bash
# 1. Extract a topology from Packet Tracer
#    (Run pt_analyzer.js inside PT via Extensions → Scripting)

# 2. Parse the output to YAML
python3 scripts/pt_config_parser.py configs.txt --yaml

# 3. Edit the YAML (change IPs, hostnames, protocols, VLANs)
nano configs_topology.yaml

# 4. Generate CLI commands
python3 tools/topology_composer.py --file configs_topology.yaml

# 5. Deploy back to Packet Tracer
#    (Run main.js via Extensions → Scripting)
```

---

## 🚀 Quick Start

**Choose your path:**

### 🟢 For New Users (5 minutes)
→ Read: **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)**

### 🟡 For Experienced Users (2 minutes)
```bash
# Open your Packet Tracer topology, then:
# 1. Extensions → Scripting → Edit File Script Module
# 2. Paste: scripts/pt_analyzer.js
# 3. Click Run
# 4. Follow prompts
```

### 🔵 For Architects/Integrators
→ Read: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** and **[docs/INTEGRATION.md](docs/INTEGRATION.md)**

---

## 📚 Documentation Map

| Need | Read This |
|------|-----------|
| **Getting started** | `docs/GETTING_STARTED.md` |
| **Packet Tracer API** | `docs/PT_SCRIPTING_API.md` |
| **All workflows** | `docs/WORKFLOWS.md` |
| **Generator reference** | `docs/GENERATORS_GUIDE.md` |
| **Architecture & design** | `docs/ARCHITECTURE.md` |
| **Integration options** | `docs/INTEGRATION.md` |
| **Troubleshooting** | `docs/TROUBLESHOOTING.md` |
| **Format support** | `docs/FORMAT_SUPPORT.md` |

---

## 📂 Directory Structure

```
Automation/
├── README.md                      ← You are here
├── main.js                        ← PT entry point (deployment)
├── docs/
│   ├── GETTING_STARTED.md         ← Start here!
│   ├── ARCHITECTURE.md            ← Design & data flow
│   ├── PT_SCRIPTING_API.md        ← API reference
│   ├── WORKFLOWS.md               ← All use patterns
│   ├── GENERATORS_GUIDE.md        ← All 12 generators
│   ├── INTEGRATION.md             ← Integration patterns
│   ├── TROUBLESHOOTING.md         ← Common issues
│   └── FORMAT_SUPPORT.md          ← Format comparisons
├── scripts/                       ← Analysis & export scripts
│   ├── pt_analyzer.js
│   ├── pt_yaml_exporter.js
│   ├── pt_api_explorer.js
│   ├── pt_config_parser.py
│   └── README.md
├── tools/                         ← Core utilities
│   ├── topology_composer.py
│   ├── yaml_to_mainjs.py
│   ├── pt_file_builder.py
│   ├── pt_file_inspector.py
│   ├── format_parser.py
│   └── README.md
├── generators/                    ← 12 protocol generators
│   ├── ospf_pathmaker.py
│   ├── bgp_conductor.py
│   ├── eigrp_catalyst.py
│   ├── [9 more generators...]
│   └── README.md
├── examples/                      ← Sample topologies
├── output/                        ← Generated files (local)
└── reference/                     ← Research & debugging
```

---

## 🎯 Common Tasks

### Extract a Topology
```bash
# In Packet Tracer: Extensions → Scripting → Edit File Script Module
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

# See all generators: generators/README.md
```

### Create .pkt Files Programmatically
```python
from tools.pt_file_builder import PktFileBuilder
builder = PktFileBuilder('topology.yaml')
builder.build('output.pkt')
```

---

## ✨ Features

✅ **Extract** — Export running configs from live Packet Tracer topologies  
✅ **Parse** — Convert Cisco configs to readable YAML/JSON/XML  
✅ **Modify** — Edit anything: hostnames, IPs, protocols, VLANs  
✅ **Generate** — Auto-create CLI commands for 12 routing protocols  
✅ **Build** — Programmatically create `.pkt` files from YAML  
✅ **Deploy** — Inject configs instantly via PT scripting API  
✅ **Repeat** — Cycle infinitely: extract → edit → rebuild → deploy  

---

## 🎓 Learning Paths

### Beginner (30 min)
1. `docs/GETTING_STARTED.md` — Overview
2. Try extracting your first topology
3. Look at `examples/` folder

### Intermediate (1–2 hours)
1. `docs/ARCHITECTURE.md` — How it works
2. `docs/GENERATORS_GUIDE.md` — Protocol generators
3. Modify and rebuild a sample topology

### Advanced (2–3 hours)
1. `docs/PT_SCRIPTING_API.md` — Deep API reference
2. `docs/INTEGRATION.md` — Integration patterns
3. `docs/WORKFLOWS.md` — Advanced workflows
4. Explore `tools/` and `generators/` source code

---

## 🔧 What's Included

### Scripts (Analysis & Export)
- `pt_analyzer.js` — Extract all configs from a topology
- `pt_yaml_exporter.js` — Export topology as copyable YAML
- `pt_config_parser.py` — Parse configs to structured format
- `pt_api_explorer.js` — Discover PT runtime capabilities

### Tools (Core Utilities)
- `topology_composer.py` — YAML → CLI commands
- `yaml_to_mainjs.py` — YAML → runnable main.js
- `pt_file_builder.py` — Create `.pkt` files from YAML
- `pt_file_inspector.py` — Inspect `.pkt` file contents
- `format_parser.py` — Multi-format support (YAML/JSON/XML)

### Generators (12 Protocols)
- **Routing:** OSPF, BGP, EIGRP, Static routes
- **Services:** DHCP, NAT, HSRP, SSH
- **Network:** VLAN, IP addressing, CIDR, ASA firewall

### Examples
- Sample topologies in YAML, JSON, XML formats
- Ready-to-use as templates

---

## 🆘 Troubleshooting

Common issues? → See **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**

---

## 💡 Pro Tips

- Start with `examples/simple_topology.yaml` — easiest template
- YAML is 40% smaller than JSON/XML — use it for configs
- All tools support auto-format detection (YAML/JSON/XML)
- Run `python3 tools/pt_file_builder_tests.py` to verify your setup
- Keep generated files in `output/` — easy cleanup

---

## 📞 More Info

- **Quick Start:** `docs/GETTING_STARTED.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **API Reference:** `docs/PT_SCRIPTING_API.md`
- **Generators:** `docs/GENERATORS_GUIDE.md`
- **Workflows:** `docs/WORKFLOWS.md`
- **Integration:** `docs/INTEGRATION.md`

---

**Ready to extract your first topology?** → [Get Started](docs/GETTING_STARTED.md)
