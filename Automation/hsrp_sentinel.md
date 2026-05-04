# Cisco HSRP and SVI Generator

## Purpose and Design
The `hsrp_generator.py` script simplifies the creation of Hot Standby Router Protocol (HSRP) and Switch Virtual Interface (SVI) configurations for Cisco multilayer switches. It uses a functional design to iterate through interface data and generate the appropriate redundancy commands.

## Key Features
- **SVI Configuration**: Automates the creation of VLAN interfaces with IP addresses.
- **HSRP Redundancy**: Configures HSRP virtual IPs, priority, and preemption.
- **Consistent Sizing**: Ensures HSRP group IDs match VLAN IDs for easier troubleshooting.

## Examples

### Example 1: Simple Scenario (Single VLAN Redundancy)
Basic HSRP setup for a single data VLAN.
- **VLAN ID**: 10
- **Physical IP**: 192.168.10.2/24
- **Virtual IP**: 192.168.10.1

### Example 2: Advanced Scenario (Load Balancing with Multiple VLANs)
Configuring HSRP across multiple VLANs with alternating priorities to distribute traffic between two switches.
- **VLAN 10**: High priority (110) on Switch A.
- **VLAN 20**: High priority (110) on Switch B.

## CLI Usage
**Generate from JSON file:**
```bash
python3 hsrp_generator.py --file inventory.json
```

## Sample JSON Input
```json
[
  {
    "hostname": "DSW-1",
    "interfaces": [
      {
        "vlan_id": 10,
        "ip": "192.168.10.2",
        "mask": "255.255.255.0",
        "hsrp_ip": "192.168.10.1",
        "priority": 110
      },
      {
        "vlan_id": 20,
        "ip": "192.168.20.2",
        "mask": "255.255.255.0",
        "hsrp_ip": "192.168.20.1",
        "priority": 90
      }
    ]
  }
]
```
