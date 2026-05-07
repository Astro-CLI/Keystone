# BGP Spinner

## Purpose and Design
The `bgp_conductor.py` script automates the configuration of Border Gateway Protocol (BGP) on Cisco IOS devices. It uses an object-oriented approach to represent the BGP routing process and its peering relationships.
- `BGPNeighbor`: Models a BGP peer, including parameters like remote AS, description, and update-source.
- `BGPRouter`: Represents the BGP process on a router, managing its own AS number, router ID, and list of neighbors and advertised networks.

## Key Features
- **Neighbor Management**: Easily configure multiple neighbors with specific attributes like `next-hop-self` and `ebgp-multihop`.
- **Network Advertisements**: Automates the `network` and `mask` statements for route propagation.
- **Flexible Peering**: Supports both iBGP (same AS) and eBGP (different AS) configurations.
- **Input/Output**: Supports JSON file input, interactive CLI, and can export configurations to both CLI and JSON formats.

## Examples

### Example 1: Simple Scenario (Basic eBGP Peering)
Peering between a corporate edge router and an ISP.
- **Local AS**: 65001
- **Peer**: 203.0.113.2 (Remote AS 65100)
- **Advertised Network**: 192.168.10.0/24

### Example 2: Advanced Scenario (iBGP with Loopbacks and eBGP Multihop)
An internal iBGP mesh using loopback interfaces and an eBGP session requiring multihop.
- **iBGP Peer**: 1.1.1.1 (AS 65001) using `update-source Loopback0` and `next-hop-self`.
- **eBGP Peer**: 10.255.255.1 (AS 65200) with `ebgp-multihop 2`.

## CLI Usage
**Generate from JSON file:**
```bash
python3 bgp_conductor.py --file inventory.json
```

**Interactive Mode:**
```bash
python3 bgp_conductor.py
```

**Save output to file:**
```bash
python3 bgp_conductor.py --file inventory.json --output bgp_configs.txt
```

## Sample JSON Input
```json
[
  {
    "hostname": "R1",
    "as_number": 65001,
    "router_id": "1.1.1.1",
    "neighbors": [
      {
        "ip": "10.0.0.2",
        "remote_as": 65001,
        "description": "iBGP to R2",
        "update_source": "Loopback0",
        "next_hop_self": true
      },
      {
        "ip": "203.0.113.2",
        "remote_as": 65100,
        "description": "eBGP to ISP",
        "ebgp_multihop": 2
      }
    ],
    "networks": [
      {
        "network": "192.168.1.0",
        "mask": "255.255.255.0"
      }
    ]
  }
]
```
