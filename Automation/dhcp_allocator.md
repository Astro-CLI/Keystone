# Identity

## Purpose and Design
The `Identity.py` script is a utility for generating Cisco IOS DHCP server configurations. It follows a functional design to process host information and their respective DHCP requirements, transforming structured data into ready-to-paste CLI commands.

## Key Features
- **Pool Management**: Create multiple DHCP pools with specific network, gateway, and DNS settings.
- **Address Exclusion**: Support for excluding specific IP addresses or ranges from the DHCP pool to prevent conflicts with static assignments.
- **Standardized Configuration**: Ensures consistent DHCP configuration across multiple devices.

## Examples

### Example 1: Simple Scenario (Single DHCP Pool)
A basic DHCP setup for a single VLAN.
- **Pool Name**: DATA_VLAN
- **Network**: 192.168.10.0/24
- **Gateway**: 192.168.10.1

### Example 2: Advanced Scenario (Multiple Pools with Exclusions)
A comprehensive setup for a site with multiple departments and reserved addresses.
- **Exclusions**: 192.168.1.1 - 192.168.1.10 (Gateways/Servers).
- **Pools**: Management, Sales, and Voice pools with distinct DNS settings.

## CLI Usage
**Generate from JSON file:**
```bash
python3 Identity.py --file dhcp_inventory.json
```

## Sample JSON Input
```json
[
  {
    "hostname": "Core-Switch-01",
    "excluded": [
      { "start": "192.168.10.1", "end": "192.168.10.10" },
      { "start": "192.168.20.1" }
    ],
    "pools": [
      {
        "name": "VLAN10_DATA",
        "network": "192.168.10.0",
        "mask": "255.255.255.0",
        "gateway": "192.168.10.1",
        "dns": "8.8.8.8"
      },
      {
        "name": "VLAN20_VOICE",
        "network": "192.168.20.0",
        "mask": "255.255.255.0",
        "gateway": "192.168.20.1",
        "dns": "1.1.1.1"
      }
    ]
  }
]
```
