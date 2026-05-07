# Fabric

## Purpose and Design
The `Fabric.py` script automates the creation of VLAN database configurations for Cisco switches. It is designed to handle both explicitly defined VLAN structures and dynamic environments where VLAN IDs can be automatically assigned.

## Key Features
- **Dynamic ID Assignment**: If a VLAN ID is omitted, the script automatically assigns a unique, random ID between 2 and 1001.
- **VLAN Naming**: Ensures all VLANs are properly named for better administrative visibility.
- **YAML & JSON Support**: Seamlessly parses both YAML and JSON inventory files.

## Examples

### Example 1: Simple Scenario (Standard VLANs)
A set of predefined VLANs for a small business.
- **VLAN 10**: Management
- **VLAN 20**: Data

### Example 2: Advanced Scenario (Dynamic VLAN Generation)
Creating departmental VLANs without worrying about manual ID management.
- **Input**: List of names (Sales, Guest, Marketing).
- **Result**: Unique IDs automatically assigned to each.

## CLI Usage
**Generate from YAML file:**
```bash
python3 Fabric.py --file vlans.yaml
```

**Generate from JSON file:**
```bash
python3 Fabric.py --file vlans.json
```

## Sample YAML Input
```yaml
- hostname: DSW-1
  vlans:
    - name: Management
      id: 10
    - name: Sales
      # id omitted -> random ID assigned
    - name: Guest
      # id omitted -> random ID assigned
```
