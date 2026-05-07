# OSPF Pathmaker

## Purpose and Design
The `ospf_pathmaker.py` script automates the generation of Open Shortest Path First (OSPFv2) configurations for Cisco IOS devices. It utilizes an Object-Oriented design to model OSPF entities:
- `OSPFInterface`: Represents an interface participating in OSPF, handling area assignment and authentication.
- `OSPFRouter`: Represents the OSPF process, managing router ID, process ID, and passive interfaces.

## Key Features
- **Multiple Configuration Styles**: Supports both traditional `network` statements and modern interface-level (`ip ospf area`) configuration.
- **Authentication Support**: Generates configuration for both Cleartext and MD5 (Message-Digest) authentication.
- **Wildcard Masking**: Automatically calculates wildcard masks for OSPF network statements.
- **Area Management**: Easily configure multi-area OSPF environments.

## Examples

### Example 1: Simple Scenario (Single-Area OSPF)
A basic OSPF setup for all interfaces in Area 0.
- **Area**: 0
- **Process ID**: 1
- **Method**: Network statements.

### Example 2: Advanced Scenario (Multi-Area with MD5 Authentication)
A complex backbone and area configuration using interface-level commands and MD5 security.
- **Areas**: 0 (Backbone) and 10 (Branch).
- **Authentication**: MD5 on Area 0 interfaces.
- **Method**: Interface-level configuration.

## CLI Usage
**Generate from JSON file:**
```bash
python3 ospf_pathmaker.py --file inventory.json
```

**Interactive Mode:**
```bash
python3 ospf_pathmaker.py
```

## Sample JSON Input
```json
[
  {
    "hostname": "Core-R1",
    "router_id": "1.1.1.1",
    "process_id": 1,
    "use_interface_config": true,
    "interfaces": [
      {
        "name": "GigabitEthernet0/0",
        "area": 0,
        "auth_type": "md5",
        "auth_key": "CiscoMD5Key"
      },
      {
        "name": "GigabitEthernet0/1",
        "area": 10,
        "is_passive": true
      }
    ]
  }
]
```
