# Anchor

## Purpose and Design
The `static_anchor.py` script automates the creation of static routing entries for Cisco IOS devices. It uses an Object-Oriented approach to model routing logic:
- `StaticRoute`: Represents a single route entry, supporting next-hops, exit interfaces, and administrative distances.
- `StaticRouteRouter`: A container for a router's collection of static routes.

## Key Features
- **Flexible Targets**: Specify routes via next-hop IP, exit interface, or both.
- **Floating Static Routes**: Easily configure backup routes by specifying a custom Administrative Distance.
- **Route Documentation**: Supports adding descriptions/comments to generated routes for better maintainability.
- **Input Variety**: Supports JSON files for batch processing and an interactive CLI mode.

## Examples

### Example 1: Simple Scenario (Standard Gateway Route)
A basic route to a remote branch network.
- **Network**: 10.10.20.0/24
- **Next-Hop**: 10.0.0.2

### Example 2: Advanced Scenario (Floating Static Route for Redundancy)
A primary route via a fast link and a backup route (floating) via a slower link.
- **Primary**: Via GigabitEthernet0/0 (AD 1).
- **Backup**: Via 192.168.255.2 (AD 200).

## CLI Usage
**Generate from JSON file:**
```bash
python3 static_anchor.py --file routes.json
```

**Interactive Mode:**
```bash
python3 static_anchor.py
```

## Sample JSON Input
```json
[
  {
    "hostname": "Edge-R1",
    "routes": [
      {
        "network": "0.0.0.0",
        "mask": "0.0.0.0",
        "next_hop": "203.0.113.1",
        "description": "Default Route to ISP"
      },
      {
        "network": "192.168.50.0",
        "mask": "255.255.255.0",
        "next_hop": "10.0.0.5",
        "distance": 200,
        "description": "Backup route to Branch B"
      }
    ]
  }
]
```
