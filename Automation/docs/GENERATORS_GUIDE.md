# Generators Guide -- All 13 Protocol Generators

Keystone includes 13 specialized generators for different network protocols and functions. You can use them via the Python GUI, browser SPA, or CLI.

---

## Quick Reference

| Generator | Protocol | Purpose | Input | Output |
|-----------|----------|---------|-------|--------|
| **ospf_pathmaker.py** | OSPF | Dynamic routing | Topology YAML | OSPF config section |
| **bgp_conductor.py** | BGP | External routing | Topology YAML | BGP config section |
| **eigrp_catalyst.py** | EIGRP | Enhanced interior routing | Topology YAML | EIGRP config section |
| **static_anchor.py** | Static Routes | Fixed routes | Topology YAML | Static route commands |
| **dhcp_allocator.py** | DHCP | Address allocation | Topology YAML | DHCP pool config |
| **nat_portal.py** | NAT | Network address translation | Topology YAML | NAT translation rules |
| **hsrp_sentinel.py** | HSRP | First hop redundancy | Topology YAML | HSRP group config |
| **ssh_locksmith.py** | SSH | Secure shell | Topology YAML | SSH security config |
| **vlan_weaver.py** | VLAN | Virtual LANs + SVIs | Topology YAML | VLAN and trunk config |
| **asa_shield.py** | ASA | Firewall rules | Topology YAML | ASA firewall config |
| **ip_architect.py** | IP Addressing | Address planning | Network info | IP allocation |
| **cidr_architect.py** | CIDR | Subnetting | Network specs | CIDR breakdown |
| **full_topology.py** | Multi-layer | Full topology composer | Topology YAML | Complete CLI + PT-Builder |

---

## Dual Output

Every generator produces **two outputs**:

- **CLI commands** -- Raw Cisco IOS commands ready to paste or deploy via `main.js`
- **PT-Builder script** -- Python script using the PTBuilder library to create `.pkt` files programmatically

In the **Python GUI** (`KeystoneGUI.py`) and **browser SPA** (`orchestrator.html`), switch between CLI and PT-Builder tabs to see both outputs.

---

## Routing Protocols

### ospf_pathmaker.py -- OSPF Routing

**What it does:**
- Generates OSPF configuration blocks
- Calculates optimal router IDs
- Creates area and network definitions
- Suggests network masks based on topology

**Usage:**

```bash
python3 generators/ospf_pathmaker.py \
  --topology examples/simple_topology.yaml \
  --output ospf_config.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: Router1
    type: router
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.1.1
        mask: 255.255.255.0
```

**Output (YAML):**
```yaml
routing:
  ospf:
    process_id: 1
    router_id: 1.1.1.1
    networks:
      - network: 10.0.1.0
        wildcard: 0.0.0.255
        area: 0
```

**Use when:**
- Building OSPF networks
- Need automatic router ID assignment
- Creating multi-area OSPF designs

---

### bgp_conductor.py -- BGP Routing

**What it does:**
- Generates BGP configuration
- Assigns AS numbers intelligently
- Creates neighbor relationships
- Configures network announcements

**Usage:**
```bash
python3 generators/bgp_conductor.py \
  --topology examples/simple_topology.yaml \
  --asn 65000 \
  --output bgp_config.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: Router1
    type: router
    bgp:
      enabled: true
```

**Output (YAML):**
```yaml
routing:
  bgp:
    asn: 65000
    router_id: 1.1.1.1
    neighbors:
      - address: 10.0.1.2
        remote_as: 65001
    networks:
      - prefix: 10.0.1.0
        mask: 255.255.255.0
```

**Use when:**
- Designing BGP networks
- Need automated neighbor discovery
- Building multi-AS networks

---

### eigrp_catalyst.py -- EIGRP Routing

**What it does:**
- Generates EIGRP configuration
- Assigns process IDs
- Creates network definitions
- Configures wildcard masks

**Usage:**
```bash
python3 generators/eigrp_catalyst.py \
  --topology examples/simple_topology.yaml \
  --as 100 \
  --output eigrp_config.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: Router1
    routing:
      eigrp:
        enabled: true
```

**Output (YAML):**
```yaml
routing:
  eigrp:
    process_id: 100
    networks:
      - network: 10.0.1.0
        wildcard: 0.0.0.255
    k_values:
      k1: 1
      k3: 1
      k4: 0
      k5: 0
```

**Use when:**
- Designing EIGRP networks
- Need automatic wildcard mask generation
- Building hybrid routing designs

---

### static_anchor.py -- Static Routes

**What it does:**
- Generates static route commands
- Calculates shortest paths
- Configures default routes
- Suggests backup routes

**Usage:**
```bash
python3 generators/static_anchor.py \
  --topology examples/simple_topology.yaml \
  --default-route 0.0.0.0 \
  --output static_routes.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: Router1
    interfaces:
      - ip: 10.0.1.1
      - ip: 192.168.1.1
```

**Output (YAML):**
```yaml
routing:
  static:
    - destination: 10.0.2.0
      mask: 255.255.255.0
      next_hop: 10.0.1.2
    - destination: 0.0.0.0
      mask: 0.0.0.0
      next_hop: 192.168.1.254
```

**Use when:**
- Designing simple route topologies
- Need automatic default gateway setup
- Building static routing labs

---

## Network Services

### dhcp_allocator.py -- DHCP Configuration

**What it does:**
- Generates DHCP pools
- Assigns pool ranges
- Configures default gateways
- Sets DNS servers
- Supports DHCPv6 (IPv6 dual-stack)

**Usage:**
```bash
python3 generators/dhcp_allocator.py \
  --topology examples/simple_topology.yaml \
  --output dhcp_config.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: DHCP_Server
    type: server
```

**Output (YAML):**
```yaml
services:
  dhcp:
    - pool_name: POOL1
      network: 10.0.1.0
      mask: 255.255.255.0
      default_gateway: 10.0.1.254
      dns_servers:
        - 8.8.8.8
        - 8.8.4.4
      excluded:
        - 10.0.1.1
        - 10.0.1.254
```

**Use when:**
- Configuring DHCP servers
- Need automatic pool calculation
- Assigning IP ranges for labs

---

### nat_portal.py -- NAT Configuration

**What it does:**
- Generates NAT translations
- Configures inside/outside interfaces
- Creates access lists
- Suggests NAT pool ranges
- Supports IPv6 NAT (NAT66)

**Usage:**
```bash
python3 generators/nat_portal.py \
  --topology examples/simple_topology.yaml \
  --inside-network 192.168.1.0/24 \
  --outside-network 203.0.113.0/24 \
  --output nat_config.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: Router_NAT
    type: router
```

**Output (YAML):**
```yaml
services:
  nat:
    inside_interface: GigabitEthernet0/0
    outside_interface: GigabitEthernet0/1
    inside_network: 192.168.1.0
    inside_mask: 255.255.255.0
    outside_network: 203.0.113.0
    translations:
      - type: dynamic
        local: 192.168.1.0
        local_mask: 255.255.255.0
        pool: 203.0.113.0
        pool_mask: 255.255.255.0
```

**Use when:**
- Configuring NAT routers
- Need automatic pool generation
- Building NAT lab scenarios

---

### hsrp_sentinel.py -- HSRP Configuration

**What it does:**
- Generates HSRP groups
- Assigns virtual IPs
- Sets priorities
- Configures standby devices

**Usage:**
```bash
python3 generators/hsrp_sentinel.py \
  --topology examples/simple_topology.yaml \
  --group 1 \
  --virtual-ip 10.0.1.254 \
  --output hsrp_config.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: Router1
    type: router
  - hostname: Router2
    type: router
```

**Output (YAML):**
```yaml
services:
  hsrp:
    - group: 1
      virtual_ip: 10.0.1.254
      priority: 100
      standby_priority: 90
      preempt: true
      timers:
        hello: 3
        hold: 10
```

**Use when:**
- Designing redundant gateways
- Need automatic priority assignment
- Building HSRP failover labs

---

### ssh_locksmith.py -- SSH Security

**What it does:**
- Generates SSH configuration
- Creates SSH keys
- Configures authentication
- Sets encryption algorithms
- Supports IPv6 VTY ACL (dual-stack)

**Usage:**
```bash
python3 generators/ssh_locksmith.py \
  --topology examples/simple_topology.yaml \
  --version 2 \
  --output ssh_config.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: Router1
    type: router
```

**Output (YAML):**
```yaml
services:
  ssh:
    version: 2
    authentication:
      - local
    encryption_algorithms:
      - aes128-ctr
      - aes192-ctr
      - aes256-ctr
    key_exchange_algorithms:
      - diffie-hellman-group14-sha1
    timeout: 120
    retries: 3
```

**Use when:**
- Securing device access
- Need SSH configuration templates
- Building secure network designs

---

## Network Design

### vlan_weaver.py -- VLAN Configuration

**What it does:**
- Generates VLAN definitions
- Configures trunk ports
- Assigns access VLANs
- Creates VLAN interfaces (SVIs)
- Supports IPv6 SVI addressing

**Usage:**
```bash
python3 generators/vlan_weaver.py \
  --topology examples/simple_topology.yaml \
  --output vlan_config.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: Switch1
    type: switch
```

**Output (YAML):**
```yaml
vlan:
  - id: 10
    name: Management
    ip: 10.0.10.1
    mask: 255.255.255.0
  - id: 20
    name: Users
    ip: 10.0.20.1
    mask: 255.255.255.0
  - id: 30
    name: Servers
    ip: 10.0.30.1
    mask: 255.255.255.0
trunk_ports:
  - GigabitEthernet0/24
  - GigabitEthernet0/48
```

**Use when:**
- Designing VLAN schemes
- Need automatic VLAN numbering
- Creating multi-VLAN networks

---

### asa_shield.py -- ASA Firewall

**What it does:**
- Generates ASA firewall rules
- Creates access lists
- Configures security zones
- Sets up NAT policies

**Usage:**
```bash
python3 generators/asa_shield.py \
  --topology examples/simple_topology.yaml \
  --inside-zone INSIDE \
  --outside-zone OUTSIDE \
  --output asa_config.yaml
```

**Input (YAML):**
```yaml
devices:
  - hostname: ASA1
    type: firewall
```

**Output (YAML):**
```yaml
firewall:
  zones:
    - name: INSIDE
      priority: 100
    - name: OUTSIDE
      priority: 0
  rules:
    - source_zone: INSIDE
      dest_zone: OUTSIDE
      action: allow
    - source_zone: OUTSIDE
      dest_zone: INSIDE
      action: deny
  nat:
    dynamic:
      - inside_net: 192.168.1.0
        inside_mask: 255.255.255.0
        outside_pool: 203.0.113.0
```

**Use when:**
- Designing firewall policies
- Need automatic ACL generation
- Building security designs

---

## Address Planning

### ip_architect.py -- IP Addressing

**What it does:**
- Plans IP address schemes
- Calculates subnet allocations
- Assigns interface IPs
- Creates address pools

**Usage:**
```bash
python3 generators/ip_architect.py \
  --network 10.0.0.0/16 \
  --device-count 10 \
  --output ip_scheme.yaml
```

**Input:**
```bash
--network 10.0.0.0/16
--device-count 10
--interface-count 3
```

**Output (YAML):**
```yaml
addressing_scheme:
  network: 10.0.0.0
  mask: 255.0.0.0
  subnets:
    - subnet: 10.0.0.0
      mask: 255.255.255.0
      gateway: 10.0.0.254
      usable: 253
    - subnet: 10.0.1.0
      mask: 255.255.255.0
      gateway: 10.0.1.254
      usable: 253
```

**Use when:**
- Planning address schemes
- Need automatic subnet calculation
- Designing IP hierarchies

---

### cidr_architect.py -- CIDR Subnetting

**What it does:**
- Performs CIDR calculations
- Breaks networks into subnets
- Calculates broadcast addresses
- Creates address ranges

**Usage:**
```bash
python3 generators/cidr_architect.py \
  --network 192.168.1.0/24 \
  --subnets 4 \
  --output cidr_breakdown.yaml
```

**Input:**
```bash
--network 192.168.1.0/24
--subnets 4
```

**Output (YAML):**
```yaml
cidr_breakdown:
  original: 192.168.1.0/24
  subnets:
    - 192.168.1.0/26      (hosts: 62)
    - 192.168.1.64/26     (hosts: 62)
    - 192.168.1.128/26    (hosts: 62)
    - 192.168.1.192/26    (hosts: 62)
  broadcast: 192.168.1.255
  total_hosts: 248
```

**Use when:**
- Subnetting networks
- Need CIDR calculations
- Learning network math

---

## Multi-Layer Topology Composer

### full_topology.py -- Full Multi-Layer Topology

**What it does:**
- Generates a complete 12-device enterprise topology in one shot
- Combines OSPF, EIGRP, BGP, DHCP, NAT, HSRP, SSH, VLANs, IPv6
- Creates 12 devices (routers, switches, PCs, servers, firewall, laptop)
- Outputs CLI commands and PT-Builder script
- Python output matches JS `tool_engine.js` exactly (byte-for-byte parity)

**Usage:**
```bash
python3 generators/full_topology.py \
  --topology examples/simple_topology.yaml \
  --output full_topology.yaml
```

**Or use the GUI:**
```bash
python3 KeystoneGUI.py
# Select "Full Topology" from the sidebar
# Click Generate
```

**Output includes:**
- OSPF, EIGRP, BGP routing on designated routers
- DHCP/DHCPv6 pools on servers
- NAT translations on border router
- HSRP gateway redundancy on distribution routers
- SSH security config on all routers
- VLANs and SVIs on switches
- IPv6 dual-stack addressing
- Topology summary in the last device's config

**Use when:**
- Building a complete enterprise lab from scratch
- Need a consistent multi-protocol topology
- Quick lab generation for testing

---

## Generator Workflow

Typical multi-generator usage:

```
                    +---------------------------+
                    |  Base Topology YAML       |
                    |  (devices, interfaces)    |
                    +------------+--------------+
                                 |
            +--------------------+-------------------+----------------+
            |                                        |                |
            v                                        v                v
  +---------------------+                 +------------------+  +-------------+
  | ospf_pathmaker      |                 | dhcp_allocator   |  | nat_portal  |
  | (routing)           |                 | (services)       |  | (services)  |
  +----------+----------+                 +--------+---------+  +------+------+
             |                                       |                  |
             | (outputs YAML for OSPF)               | (DHCP)           | (NAT)
             +------------------+--------------------+------------------+
                                |
                     +----------v------------+
                     |  Merge all into       |
                     |  final topology YAML  |
                     +----------+------------+
                                |
                     +----------v------------+
                     |  topology_composer.py  |
                     |  (CLI commands)        |
                     +----------+------------+
                                |
                     +----------v------------+
                     |  pt_builder_gen.py     |
                     |  (PT-Builder script)   |
                     +------------------------+
```

---

## Integration Examples

### Example 1: OSPF + DHCP Network

```bash
# 1. Start with base topology
cp examples/simple_topology.yaml mylab.yaml

# 2. Generate OSPF config
python3 generators/ospf_pathmaker.py --topology mylab.yaml
# Merge output into mylab.yaml

# 3. Generate DHCP config
python3 generators/dhcp_allocator.py --topology mylab.yaml
# Merge output into mylab.yaml

# 4. Deploy
python3 tools/yaml_to_mainjs.py mylab.yaml --output main.js
# Run main.js in PT
```

### Example 2: Full Topology via GUI

```bash
# 1. Launch GUI
python3 KeystoneGUI.py

# 2. Click "Full Topology" in sidebar

# 3. Click Generate (or Ctrl+Enter)

# 4. Copy CLI commands from CLI tab OR
#    Copy PT-Builder script from PT-Builder tab

# 5. Paste CLI into PT or run PT-Builder to create .pkt
```

### Example 3: BGP + NAT + Firewall

```bash
# 1. BGP routing
python3 generators/bgp_conductor.py --topology mylab.yaml --asn 65000

# 2. NAT for inside
python3 generators/nat_portal.py --topology mylab.yaml

# 3. Firewall protection
python3 generators/asa_shield.py --topology mylab.yaml

# 4. Merge all
# 5. Deploy
```

---

## Common Issues

**Generator says "Invalid topology format":**
- Check YAML syntax (indentation, colons)
- Verify required fields (hostname, type, interfaces)

**Output seems incomplete:**
- Some generators require specific device types
- Check input topology has needed information

**Conflicts between generators:**
- Don't merge same section twice
- Plan which generators you'll use first

**PT-Builder and CLI outputs differ:**
- Run `python3 tools/pt_file_builder_tests.py` to check parity
- Report mismatches as issues

---

## Learn More

- **Getting Started:** `docs/GETTING_STARTED.md`
- **All Workflows:** `docs/WORKFLOWS.md`
- **Tools:** `tools/README.md`
- **Scripts:** `scripts/README.md`

---

**Next:** Pick generators that match your topology design, then use the GUI or CLI to deploy!
