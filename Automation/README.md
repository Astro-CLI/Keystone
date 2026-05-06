# Network Automation Suite

A collection of intelligent network configuration generators inspired by Steve Jobs' design philosophy: **beautiful, purposeful, and intuitive**.

---

## 🗂️ Generator Overview

| Tool | Purpose | Learn More |
|------|---------|-----------|
| 🎼 **topology_composer** | Converts topology definitions into copy-paste CLI commands for Packet Tracer | [📖](./topology_composer.md) |
| 🛣️ **ospf_pathmaker** | Creates OSPF routing paths and network topology | [📖](./ospf_pathmaker.md) |
| 🎯 **bgp_conductor** | Orchestrates BGP neighbor relationships and AS peering | [📖](./bgp_conductor.md) |
| ⚡ **eigrp_catalyst** | Catalyzes EIGRP convergence and topology discovery | [📖](./eigrp_catalyst.md) |
| 🔄 **hsrp_sentinel** | Manages HSRP/SVI redundancy and failover | [📖](./hsrp_sentinel.md) |
| 🏢 **dhcp_allocator** | Assigns and manages DHCP pool configurations | [📖](./dhcp_allocator.md) |
| 🔐 **ssh_locksmith** | Creates secure SSH access and key management | [📖](./ssh_locksmith.md) |
| 🗺️ **ip_architect** | Designs IP addressing schemes and subneting | [📖](./ip_architect.md) |
| ⚓ **static_anchor** | Fixes static routes and manual routing entries | [📖](./static_anchor.md) |
| 🌉 **nat_portal** | Creates NAT configurations and port forwarding | [📖](./nat_portal.md) |
| 🧵 **vlan_weaver** | Weaves VLAN configurations with intelligent ID assignment | [📖](./vlan_weaver.md) |
| 📐 **cidr_architect** | Plans CIDR blocks and optimizes subnet sizing | [📖](./cidr_architect.md) |
| 🛡️ **asa_shield** | Shields networks with ASA firewall configurations | [📖](./asa_shield.md) |

---

## 🚀 Getting Started

### Setup
All scripts support **YAML**, **JSON**, and **XML** formats for maximum flexibility. Install dependencies:
```bash
pip install -r requirements.txt
```

### Two Ways to Build Packet Tracer Labs

#### Option 1: CLI Commands (Fast & Safe)
```bash
# Generate copy-paste commands for Packet Tracer
python3 topology_composer.py --file my_network.yaml --output config_commands.txt
```
Best for: Learning, testing, manual control

#### Option 2: Direct .pkt File Generation (Research/Development)
```bash
# Generate .pkt file (experimental - see status below)
python3 pt_file_builder.py my_network.yaml -o lab.pkt
```
Best for: Research, format investigation, structural validation

### Basic Usage
```bash
# Use any generator
python3 [generator_name].py --file config.yaml

# See help for any generator
python3 [generator_name].py --help
```

---

## ✨ Key Features

### 🎼 Topology Composer (Option A: CLI Commands)
Define your entire network topology once in YAML/JSON/XML, then generate all CLI commands ready to copy-paste into Packet Tracer. Saves hours of manual configuration!

```bash
python3 topology_composer.py --file network.yaml --output config_commands.txt
```

Then simply copy each device's commands and paste into Packet Tracer. See [topology_composer.md](./topology_composer.md) for full details.

### 🔧 PT File Builder (Option B: Research/Development) 🔬

**⚠️ STATUS:** Reverse-engineered .pkt binary format successfully, but Packet Tracer 8.2.2 rejects generated files ("Unable to open file. The file was not saved correctly."). Investigation ongoing.

**What Works:**
- ✅ Binary format reverse-engineered (XOR encryption + zlib)
- ✅ Files generate with valid structure
- ✅ XML decompresses correctly
- ✅ 33 internal validation tests (100% passing)
- ✅ Built-in inspector tool to analyze .pkt files

**What Doesn't:**
- ❌ Packet Tracer won't open generated files
- ❌ Likely missing additional validation/checksum
- 🔍 Root cause under investigation

**For Production:** Use [Topology Composer (Option A)](#🎼-topology-composer-option-a-cli-commands) instead.

**For Research/Investigation:**
```bash
# Generate .pkt file (for analysis)
python3 pt_file_builder.py topology.yaml -o my_lab.pkt

# Inspect file structure
python3 pt_file_inspector.py my_lab.pkt --list-devices
python3 pt_file_inspector.py my_lab.pkt --xml --pretty
```

See [pt_file_builder.md](./pt_file_builder.md) for technical details and ongoing investigation status.

### 🎲 Dynamic VLAN IDs
The `vlan_weaver.py` intelligently generates unique VLAN IDs if you omit them from your config:

```yaml
- hostname: DSW-1
  vlans:
    - name: Management
      id: 10
    - name: Sales
      # id omitted -> random ID assigned automatically
    - name: Guest
      # id omitted -> random ID assigned automatically
```

### 📐 Smart CIDR Planning
`cidr_architect.py` automatically determines the best subnet size based on your host requirements (VLSM support):

**Features:**
- **Smart Sizing**: Input the number of machines → finds the smallest efficient subnet (e.g., 25 hosts → /27)
- **Full Masking**: Provides subnet mask AND wildcard mask (essential for OSPF/EIGRP/ACLs)
- **Range Mapping**: Shows exact usable IP ranges
- **Critical Addresses**: Identifies network, broadcast, and gateway addresses

**Usage:**
```bash
python3 cidr_architect.py --hosts 25
```

**Output:**
```text
Recommended Prefix: /27
Network Address:    192.168.1.0
Subnet Mask:        255.255.255.224
Wildcard Mask:      0.0.0.31
Usable Range:       192.168.1.1 - 192.168.1.30
```

### 📋 Multi-Format Support
All generators support **JSON**, **YAML**, and **XML** input formats. Format is auto-detected:

```bash
# All these work - format auto-detected
python3 ospf_pathmaker.py --file network.json
python3 ospf_pathmaker.py --file network.yaml
python3 ospf_pathmaker.py --file network.xml
```

---

## 📚 Full Documentation

Each generator has detailed documentation in its own `.md` file (see table above). Start with the tool you need, or explore the suite to build complete automation workflows.

**New to Packet Tracer automation?** Start with [topology_composer.md](./topology_composer.md)!












## Investigation Results: Option B Analysis

A comprehensive investigation into PT 8.2.2 .pkt format has been completed. See [OPTION_B_STATUS.md](./OPTION_B_STATUS.md) for full details.

**Key Finding**: PT 8.2.2 uses proprietary encryption not documented publicly. The format is significantly different from what was available in ptexplorer (which documented PT 5.x).

**Status**: Option A is production-ready. Option B remains research.

