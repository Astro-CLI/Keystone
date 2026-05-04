# Network Automation Suite

A collection of intelligent network configuration generators inspired by Steve Jobs' design philosophy: **beautiful, purposeful, and intuitive**.

---

## 🗂️ Generator Overview

| Tool | Purpose | Learn More |
|------|---------|-----------|
| 🛣️ **ospf_pathmaker** | Creates OSPF routing paths and network topology | [📖](./ospf_pathmaker.md) |
| 🎯 **bgp_conductor** | Orchestrates BGP neighbor relationships and AS peering | [📖](./bgp_conductor.md) |
| ⚡ **eigrp_catalyst** | Catalyzes EIGRP convergence and topology discovery | [📖](./eigrp_catalyst.md) |
| 🔄 **hsrp_sentinel** | Manages HSRP/SVI redundancy and failover | [📖](./hsrp_sentinel.md) |
| 🏢 **dhcp_allocator** | Assigns and manages DHCP pool configurations | [📖](./dhcp_allocator.md) |
| 🔐 **ssh_locksmith** | Creates secure SSH access and key management | [📖](./ssh_locksmith.md) |
| 🗺️ **ip_architect** | Designs IP addressing schemes and subnetting | [📖](./ip_architect.md) |
| ⚓ **static_anchor** | Fixes static routes and manual routing entries | [📖](./static_anchor.md) |
| 🌉 **nat_portal** | Creates NAT configurations and port forwarding | [📖](./nat_portal.md) |
| 🧵 **vlan_weaver** | Weaves VLAN configurations with intelligent ID assignment | [📖](./vlan_weaver.md) |
| 📐 **cidr_architect** | Plans CIDR blocks and optimizes subnet sizing | [📖](./cidr_architect.md) |
| 🛡️ **asa_shield** | Shields networks with ASA firewall configurations | [📖](./asa_shield.md) |

---

## 🚀 Getting Started

### Setup
All scripts support **YAML** (`.yaml` or `.yml`) for modern, readable configuration. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage
```bash
# Generate a configuration
python3 ospf_pathmaker.py --file network.yaml

# See help for any generator
python3 [generator_name].py --help
```

---

## ✨ Key Features

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

---

## 📚 Full Documentation

Each generator has detailed documentation in its own `.md` file (see table above). Start with the tool you need, or explore the suite to build complete automation workflows.











