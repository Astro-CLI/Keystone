# Velocity

## Purpose and Design
The `Velocity.py` script automates the generation of Enhanced Interior Gateway Routing Protocol (EIGRP) configurations for Cisco devices. It uses an Object-Oriented approach to handle network calculations and router settings:
- `EIGRPInterface`: Represents a physical or logical interface, automatically calculating the network address and wildcard mask from the IP and subnet mask.
- `EIGRPRouter`: Manages the EIGRP process, including the AS number, router ID, passive interfaces, and stub status.

## Key Features
- **Wildcard Mask Calculation**: Automatically converts subnet masks to wildcard masks for EIGRP network statements.
- **Passive Interface Support**: Easily mark interfaces as passive to prevent EIGRP adjacencies where they aren't needed.
- **Stub Routing**: Supports EIGRP stub configuration for branch or leaf routers.
- **Flexible Input**: Supports JSON inventory files and an interactive mode.

## Examples

### Example 1: Simple Scenario (Basic EIGRP Peering)
A standard EIGRP setup with two active interfaces.
- **AS Number**: 100
- **Interfaces**: Gi0/0 and Gi0/1.

### Example 2: Advanced Scenario (EIGRP Stub with Passive Interfaces)
A branch router configuration using EIGRP stub and passive-interface default.
- **AS Number**: 100
- **Stub Mode**: `connected summary`
- **Passive Interfaces**: All user-facing interfaces are set to passive.

## CLI Usage
**Generate from JSON file:**
```bash
python3 Velocity.py --file inventory.json
```

**Interactive Mode:**
```bash
python3 Velocity.py
```

## Sample JSON Input
```json
[
  {
    "hostname": "Branch-R1",
    "as_number": 100,
    "router_id": "1.1.1.1",
    "is_stub": true,
    "interfaces": [
      {
        "name": "GigabitEthernet0/0",
        "ip_address": "10.0.0.1",
        "subnet_mask": "255.255.255.252",
        "is_passive": false
      },
      {
        "name": "GigabitEthernet0/1",
        "ip_address": "192.168.1.1",
        "subnet_mask": "255.255.255.0",
        "is_passive": true
      }
    ]
  }
]
```
