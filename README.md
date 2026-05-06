# Keystone: Packet Tracer Network Automation Toolkit 🔑

[![Status](https://img.shields.io/badge/status-active-brightgreen.svg)](https://github.com/Astro-CLI/Keystone)
[![License](https://img.shields.io/badge/License-LGPL_v2.1-blue.svg)](./LICENSE.md)
[![Packet Tracer](https://img.shields.io/badge/Packet_Tracer-8.2%2B-orange.svg)](#)

> Extract, parse, generate, and rebuild Cisco Packet Tracer network topologies programmatically. No manual configuration. Pure automation.

---

## 📖 Table of Contents

- [What is Keystone?](#-what-is-keystone)
- [Core Features](#-core-features)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [The Example: SOYMSA](#-the-example-soymsa)
- [Capabilities & Tools](#-capabilities--tools)
- [License & Attribution](#-license--attribution)

---

## ⚡ What is Keystone?

Keystone is a comprehensive toolkit for automating Cisco Packet Tracer network operations. It bridges the gap between manual network configuration and truly programmable infrastructure.

**Problem:** Packet Tracer lacks native support for batch device creation, configuration injection, and topology extraction.

**Solution:** Keystone provides:
- **pt_analyzer.js** — Extract running configurations from live topologies
- **pt_config_parser.py** — Parse Cisco configs into structured YAML/JSON/XML formats
- **12 generator tools** — Create routers, switches, security devices, and services programmatically
- **Format support** — YAML, JSON, XML with automatic detection and conversion

### Tested On
- Packet Tracer 8.2.2 ✅
- Packet Tracer 9.0.0 ✅

---

## 🎯 Core Features

✅ **Extract topologies** from running Packet Tracer files via CommandLine API  
✅ **Parse configurations** into human-editable formats (YAML/JSON/XML)  
✅ **Modify topologies** by editing config files and re-building  
✅ **Generate network devices** programmatically (routers, switches, ASAs, DHCPs, etc.)  
✅ **Inject CLI commands** directly into device configurations  
✅ **Multi-format support** — YAML is 40% smaller than JSON/XML  
✅ **Well-documented** — Every tool has examples and troubleshooting guides  

---

## 🚀 Quick Start

### 1. Extract a Topology
Run `pt_analyzer.js` inside Packet Tracer to export all device configs:
```javascript
// Inside PT's Script Editor - runs the analyzer
```

### 2. Parse the Configs
Convert extracted running-configs to YAML:
```bash
python scripts/pt_config_parser.py --config router_config.txt --output network.yaml
```

### 3. Modify the Topology
Edit `network.yaml` with new IPs, interfaces, or protocols:
```yaml
routers:
  - name: Router1
    interfaces:
      - name: Gi0/0
        ip: 192.168.1.1
        subnet: 255.255.255.0
```

### 4. Rebuild
Use the generators to rebuild the topology with your modifications:
```bash
python generators/ospf_pathmaker.py --config network.yaml --output rebuilt.pkt
```

---

## 🔄 How It Works

```
[PT Topology] ──→ [pt_analyzer.js] ──→ [Running Configs]
                                            ↓
                                    [pt_config_parser.py]
                                            ↓
                                    [YAML/JSON/XML]
                                            ↓
                                        [Edit]
                                            ↓
                                  [Generators: ospf_pathmaker,
                                   bgp_conductor, etc.]
                                            ↓
                                    [New PT Topology]
```

---

## 📂 Project Structure

```
Automation/
├── scripts/                    # Core extraction & analysis tools
│   ├── pt_analyzer.js         # Extract configs from live topologies
│   └── pt_config_parser.py    # Parse Cisco configs to structured formats
├── generators/                 # Network device & protocol generators
│   ├── ospf_pathmaker.py      # Generate OSPF configurations
│   ├── bgp_conductor.py       # Generate BGP configurations
│   ├── dhcp_allocator.py      # Generate DHCP services
│   └── [8 more...]            # ASA, NAT, EIGRP, SSH, etc.
├── docs/                       # Comprehensive documentation
│   ├── PT_ANALYZER_README.md  # Full reference guide
│   ├── PT_ANALYZER_QUICKSTART.md
│   └── FORMAT_COMPARISON.md   # Why YAML beats JSON/XML
├── examples/                   # Sample topologies (YAML/JSON/XML)
│   └── simple_topology.yaml   # Start here
├── output/                     # Generated .pkt files & configs
└── tools/                      # Utility scripts & helpers
```

### Navigation Guides
- **README_START_HERE.md** — Entry point for new users
- **DIRECTORY_STRUCTURE.md** — Complete guide to all directories
- **STRUCTURE_VISUAL.txt** — Before/after ASCII comparison

---

## 🎓 The Example: SOYMSA

SOYMSA (*Sistemas, Organización y Métodos, Sociedad Anónima*) is a practical demonstration of Keystone's capabilities. It's a complete network simulation built for academic purposes that showcases:

- **Global topology extraction** from a complex multi-branch architecture
- **Configuration parsing** of real Cisco IOS running-configs
- **Programmatic rebuilding** with modifications
- **Production-grade simulation** using real ISPs (Movistar, Cellcom, AT&T)

### SOYMSA Architecture

| Layer | Component | Purpose |
|---|---|---|
| **WAN Core** | 3 ISP routers (BGP peers) | Global internet backbone |
| **Security** | Cisco ASA 5506-X | NAT, firewalls, DMZ |
| **Branches** | 3 geographically separated sites | Core/Distribution/Access layers |
| **Services** | DNS, Web, FTP, VPN servers | Cloud infrastructure |

The SOYMSA project files live in `/SOYMSA/` directory. Start with `Core.pkt` and follow the progression as each stage builds upon the previous one.

---

## 🛠️ Capabilities & Tools

### Generators (12 Total)

All generators support YAML/JSON/XML input formats via the shared `format_parser` module:

| Generator | Purpose | Creates |
|---|---|---|
| **ospf_pathmaker.py** | OSPF routing | Multi-area OSPF networks |
| **bgp_conductor.py** | BGP routing | Inter-AS networks with peers |
| **eigrp_catalyst.py** | EIGRP routing | Dynamic routing topologies |
| **static_anchor.py** | Static routes | Fixed route configurations |
| **dhcp_allocator.py** | DHCP services | IP address pools & gateway |
| **nat_portal.py** | NAT configuration | Static/dynamic address translation |
| **asa_shield.py** | Firewall rules | Access control & security policies |
| **vlan_weaver.py** | VLAN configuration | Network segmentation |
| **hsrp_sentinel.py** | High availability | Redundant gateways |
| **ssh_locksmith.py** | Secure access | SSH authentication |
| **ip_architect.py** | IP subnetting | CIDR planning & allocation |
| **subnet_calc.py** | Subnet calculator | Quick VLSM calculations |

### Analysis & Parsing

| Tool | Input | Output | Purpose |
|---|---|---|---|
| **pt_analyzer.js** | Live PT topology | Running configs (text) | Extract device state |
| **pt_config_parser.py** | Running configs | YAML/JSON/XML | Structured format parsing |

### Documentation

See `/docs/` for comprehensive guides:
- **PT_ANALYZER_README.md** — Complete extraction & parsing workflows
- **PT_ANALYZER_QUICKSTART.md** — 5-minute getting started
- **FORMAT_COMPARISON.md** — YAML vs JSON vs XML analysis
- **DIRECTORY_STRUCTURE.md** — Full project navigation
- **README_START_HERE.md** — Entry point for new users

---

## 📜 License & Attribution

This project is licensed under **LGPL v2.1 - Ariel's Edition**. See `LICENSE.md` for details.

**In human terms:**
- ✅ Use this anywhere (commercial, proprietary, educational, etc.)
- ✅ Share improvements back to the community
- ✅ Keep this project open source
- ✅ Give credit where it's due

---

## 🙏 Acknowledgments

Keystone stands on the shoulders of giants. We credit:
- **PTExplorer** — Early API exploration
- **Awesome Packet Tracer** — Community resource curation
- **PTBuilder** — Proof-of-concept for programmatic device creation
- **md2pkt** — Topology abstraction validation
- And the broader PT automation community

See `CREDITS.md` for full attribution.

---

## 🚀 Getting Started

1. **Read:** Start with `Automation/README_START_HERE.md`
2. **Explore:** Check out `examples/` for sample topologies
3. **Extract:** Use `scripts/pt_analyzer.js` on a live topology
4. **Parse:** Convert with `scripts/pt_config_parser.py`
5. **Generate:** Use any of the 12 generators to rebuild
6. **Learn:** Read the docs in `Automation/docs/`

---

Made with ❤️ and a lot of packets. | [CREDITS.md](./CREDITS.md) | [LICENSE.md](./LICENSE.md) | [MANIFESTO.md](./MANIFESTO.md)
