# Topology Composer

**Generate bulk CLI commands from network topology definitions for Packet Tracer**

Instead of manually typing configuration commands into each Packet Tracer device, define your entire network topology once in YAML/JSON/XML—and Topology Composer generates all the CLI commands ready to copy-paste.

---

## 🎯 What It Does

1. **Read** your topology definition (YAML/JSON/XML)
2. **Generate** complete CLI configurations for every device
3. **Output** as copy-paste-ready text or structured JSON
4. **Paste** into Packet Tracer devices instantly

### Supported Devices & Protocols
- ✅ Routers (IOS)
- ✅ OSPF, BGP, EIGRP routing
- ✅ DHCP servers & pools
- ✅ HSRP redundancy
- ✅ Static routing
- ✅ NAT (static & dynamic)
- ✅ SSH/Security
- ✅ Access Control Lists (ACLs)

---

## 🚀 Quick Start

### Basic Usage
```bash
python3 topology_composer.py --file my_network.yaml
```

### Save to File
```bash
python3 topology_composer.py --file my_network.yaml --output config_commands.txt
```

### Output as JSON
```bash
python3 topology_composer.py --file my_network.yaml --format json
```

---

## 📝 Topology Definition Format

Define your network topology in YAML, JSON, or XML. Here's a complete example:

### Example YAML (`network_topology.yaml`)
```yaml
devices:
  - hostname: R1-CORE
    type: router
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.1
        mask: 255.255.255.0
        description: "Link to R2"
      - name: GigabitEthernet0/0/1
        ip: 10.0.2.1
        mask: 255.255.255.0
        description: "Link to SW1"
    
    ospf:
      process_id: 1
      router_id: 1.1.1.1
      networks:
        - network: 10.0.1.0
          wildcard: 0.0.0.255
          area: 0
        - network: 10.0.2.0
          wildcard: 0.0.0.255
          area: 0

  - hostname: R2-EDGE
    type: router
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.2
        mask: 255.255.255.0
        description: "Link to R1"
      - name: GigabitEthernet0/0/1
        ip: 192.168.1.1
        mask: 255.255.255.0
        description: "WAN Link"
    
    bgp:
      asn: 65001
      router_id: 2.2.2.2
      neighbors:
        - ip: 192.168.1.2
          asn: 65002
          description: "ISP1"
      networks:
        - network: 10.0.0.0
          mask: 255.255.0.0

  - hostname: DHCP-SERVER
    type: router
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.2.254
        mask: 255.255.255.0
        description: "LAN Interface"
    
    dhcp:
      pools:
        - name: VLAN10
          network: 10.0.10.0
          mask: 255.255.255.0
          gateway: 10.0.10.1
          dns: "8.8.8.8 8.8.4.4"
        - name: VLAN20
          network: 10.0.20.0
          mask: 255.255.255.0
          gateway: 10.0.20.1
          dns: "8.8.8.8"
      excluded:
        - start: 10.0.10.1
          end: 10.0.10.10
        - start: 10.0.20.1
          end: 10.0.20.10

  - hostname: NAT-GATEWAY
    type: router
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.3
        mask: 255.255.255.0
        description: "Inside"
      - name: GigabitEthernet0/0/1
        ip: 203.0.113.50
        mask: 255.255.255.0
        description: "Outside"
    
    nat:
      inside_interfaces:
        - GigabitEthernet0/0/0
      outside_interfaces:
        - GigabitEthernet0/0/1
      static:
        - inside_ip: 10.0.1.100
          outside_ip: 203.0.113.100
      dynamic:
        - name: NATPOOL
          start_ip: 203.0.113.200
          end_ip: 203.0.113.220

  - hostname: HA-ROUTER-1
    type: router
    interfaces:
      - name: VLAN10
        vlan: 10
        ip: 10.0.10.254
        mask: 255.255.255.0
    
    hsrp:
      groups:
        - vlan: 10
          group_id: 1
          priority: 110
          virtual_ip: 10.0.10.1
```

---

## 📊 Configuration Options

### Basic Device
```yaml
hostname: DEVICE-NAME        # Required: router/switch hostname
type: router                 # Device type
interfaces: [...]           # List of interfaces to configure
```

### Interface Configuration
```yaml
interfaces:
  - name: GigabitEthernet0/0/0  # Interface name
    ip: 10.0.1.1                # IP address
    mask: 255.255.255.0         # Subnet mask
    vlan: 10                     # (for VLAN interfaces)
    description: "Link info"    # Optional description
```

### OSPF Routing
```yaml
ospf:
  process_id: 1              # OSPF process ID
  router_id: 1.1.1.1         # Router ID
  networks:
    - network: 10.0.1.0
      wildcard: 0.0.0.255
      area: 0
```

### BGP Routing
```yaml
bgp:
  asn: 65001                 # Autonomous System Number
  router_id: 1.1.1.1         # Router ID
  neighbors:
    - ip: 10.0.1.2
      asn: 65002
      description: "Neighbor description"
  networks:
    - network: 10.0.0.0
      mask: 255.255.0.0
```

### EIGRP Routing
```yaml
eigrp:
  asn: 100                   # EIGRP AS number
  router_id: 1.1.1.1         # Router ID (optional)
  networks:
    - network: 10.0.1.0
      wildcard: 0.0.0.255
```

### DHCP Configuration
```yaml
dhcp:
  pools:
    - name: POOL1
      network: 10.0.10.0
      mask: 255.255.255.0
      gateway: 10.0.10.1
      dns: "8.8.8.8 8.8.4.4"
  excluded:
    - start: 10.0.10.1
      end: 10.0.10.20
```

### HSRP Redundancy
```yaml
hsrp:
  groups:
    - vlan: 10               # VLAN ID
      group_id: 1            # HSRP group number
      priority: 110          # Priority (100-255)
      virtual_ip: 10.0.10.1  # Virtual IP
```

### NAT Configuration
```yaml
nat:
  inside_interfaces:
    - GigabitEthernet0/0/0
  outside_interfaces:
    - GigabitEthernet0/0/1
  static:
    - inside_ip: 10.0.1.100
      outside_ip: 203.0.113.100
  dynamic:
    - name: NATPOOL
      start_ip: 203.0.113.200
      end_ip: 203.0.113.220
```

### Static Routes
```yaml
static_routes:
  - destination: 192.168.1.0
    mask: 255.255.255.0
    next_hop: 10.0.1.1
```

### SSH/Security
```yaml
ssh:
  enabled: true              # Enables SSH configuration
```

### Access Control Lists
```yaml
acls:
  - number: 100
    rules:
      - action: permit
        protocol: ip
        source: 10.0.1.0
        destination: 10.0.2.0
      - action: deny
        protocol: ip
        source: 192.168.1.0
        destination: any
```

---

## 📋 Output Example

**Command output (text format):**
```
============================================================
Configuration for: R1-CORE
============================================================

enable
configure terminal
hostname R1-CORE
interface GigabitEthernet0/0/0
 description Link to R2
 ip address 10.0.1.1 255.255.255.0
 no shutdown
 exit
interface GigabitEthernet0/0/1
 description Link to SW1
 ip address 10.0.2.1 255.255.255.0
 no shutdown
 exit
router ospf 1
 router-id 1.1.1.1
 network 10.0.1.0 0.0.0.255 area 0
 network 10.0.2.0 0.0.0.255 area 0
 exit
end
write memory
```

Simply copy and paste these commands into each device in Packet Tracer!

---

## ✨ Workflow

1. **Define topology once** in YAML/JSON/XML
2. **Generate all CLI commands** for the entire network
3. **Copy device config** (R1-CORE section) into Packet Tracer R1
4. **Paste & execute** in device terminal
5. **Repeat** for each device
6. **Network is configured** in seconds vs hours of manual typing

---

## 🔧 Advanced Usage

### Generate Config for Specific Topology
```bash
# Text format (easy to copy/paste)
python3 topology_composer.py --file my_network.yaml --output commands.txt

# JSON format (for automation/scripting)
python3 topology_composer.py --file my_network.yaml --format json --output commands.json
```

### Supported Input Formats
- ✅ YAML (`.yaml`, `.yml`)
- ✅ JSON (`.json`)
- ✅ XML (`.xml`)

Format is auto-detected by file extension!

---

## 📚 Tips & Best Practices

1. **Start Simple** – Define interfaces and one routing protocol at a time
2. **Validate IPs** – Make sure your subnet masks and IP ranges make sense
3. **Use Descriptions** – Add descriptive names to interfaces for clarity
4. **Test Incrementally** – Apply one device's config at a time and test connectivity
5. **Keep YAML Clean** – Use consistent indentation (2 spaces in YAML)
6. **Router IDs** – Always specify unique router IDs for OSPF/BGP/EIGRP

---

## 🤝 Integration with Other Tools

Combine Topology Composer with other Keystone automation tools:

- **Define topology** → `topology_composer.py`
- **Validate subnetting** → `cidr_architect.py`
- **Plan VLANS** → `vlan_weaver.py`
- **Document network** → Reference the YAML topology file

---

## ❓ Troubleshooting

**Q: My commands aren't pasting correctly in Packet Tracer**
A: Make sure you're copying the text from the output and pasting into the device's terminal in config mode (`configure terminal`).

**Q: How do I add more devices?**
A: Simply add another item to the `devices` list in your YAML/JSON with its hostname and configuration.

**Q: Can I generate configs for switches too?**
A: Currently optimized for routers. Switch support (VLAN, spanning-tree, etc.) coming soon!

**Q: Can this create the .pkt file directly?**
A: Not yet—use this to generate CLI commands, then paste into Packet Tracer manually. Direct `.pkt` generation requires reverse-engineering Packet Tracer's binary format.

---

## 📖 See Also

- `ospf_pathmaker.py` – Deep dive into OSPF configurations
- `bgp_conductor.py` – Advanced BGP peering
- `cidr_architect.py` – Subnet planning
- `vlan_weaver.py` – VLAN design
