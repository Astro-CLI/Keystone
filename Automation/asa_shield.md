# Sentry

## Purpose and Design
The `Sentry.py` script is designed to automate the creation of Cisco ASA firewall configurations. It employs an Object-Oriented (OO) design to model various firewall components, making the configuration process modular and extensible. Key classes include:
- `ASAInterface`: Manages physical interface settings, security levels, and IP addressing.
- `ASANetworkObject`: Defines network objects for hosts or subnets.
- `ASANAT`: Handles Network Address Translation (NAT) rules.
- `ASAACLRule`: Defines Access Control List (ACL) entries.
- `ASARouter`: An orchestrator class that aggregates interfaces, objects, NAT rules, and ACLs to generate a complete configuration.

## Key Features
- **Object-Oriented Modeling**: Clean separation of concerns for firewall components.
- **NAT Support**: Automates dynamic NAT configuration for network objects.
- **ACL Management**: Simplifies the creation of extended access lists.
- **Flexible Input**: Supports both structured JSON files for complex deployments and an interactive CLI mode for quick setups.

## Examples

### Example 1: Simple Scenario (Basic Inside/Outside Setup)
A standard firewall setup with one inside and one outside interface.
- **Inside**: 192.168.1.1/24 (Security Level 100)
- **Outside**: 203.0.113.1/24 (Security Level 0)

### Example 2: Advanced Scenario (Multi-Interface with NAT and ACLs)
A complex setup including a DMZ, network objects for internal servers, and ACLs to permit specific traffic.
- **Interfaces**: Inside, Outside, and DMZ.
- **Objects**: Web-Server (192.168.10.50), Mail-Server (192.168.10.60).
- **NAT**: Dynamic PAT for internal users.
- **ACLs**: Permit HTTP/HTTPS traffic to the Web-Server from the outside.

## CLI Usage
**Using a JSON inventory file:**
```bash
python3 Sentry.py --file inventory.json
```

**Interactive Mode:**
```bash
python3 Sentry.py
```

## Sample JSON Input
```json
[
  {
    "hostname": "ASA-FW-01",
    "interfaces": [
      {
        "name": "GigabitEthernet0/0",
        "nameif": "inside",
        "security_level": 100,
        "ip": "192.168.1.1",
        "mask": "255.255.255.0"
      },
      {
        "name": "GigabitEthernet0/1",
        "nameif": "outside",
        "security_level": 0,
        "ip": "203.0.113.1",
        "mask": "255.255.255.252"
      }
    ],
    "objects": [
      {
        "name": "INTERNAL_NET",
        "subnet": "192.168.1.0",
        "mask": "255.255.255.0"
      }
    ],
    "nats": [
      {
        "obj_name": "INTERNAL_NET",
        "type": "dynamic",
        "translated_interface": "outside"
      }
    ],
    "acls": [
      {
        "access_list": "OUTSIDE_IN",
        "action": "permit",
        "protocol": "tcp",
        "source": "any",
        "destination": "any",
        "service": "eq 443"
      }
    ],
    "access_groups": {
      "OUTSIDE_IN": "outside"
    }
  }
]
```
