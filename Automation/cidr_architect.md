# Subnet/CIDR Planner

## Purpose and Design
The `cidr_architect.py` script is a specialized utility for network designers to automate the calculation of optimal subnet sizes. It uses the `SubnetPlanner` class to perform mathematical calculations based on host requirements, ensuring efficient use of IP address space (VLSM).

## Key Features
- **Smart Sizing**: Input the number of required host machines, and the script identifies the smallest valid CIDR prefix.
- **Comprehensive Details**: Provides network address, broadcast address, subnet mask, and wildcard mask.
- **Usable Range**: Calculates the first and last usable IP addresses for the subnet.
- **Flexible Output**: Supports standard text output and YAML for integration with other tools.

## Examples

### Example 1: Simple Scenario (Small Office Subnet)
Find the best subnet for a small office with 25 machines.
- **Input**: `--hosts 25`
- **Output**: Recommended /27 prefix.

### Example 2: Advanced Scenario (Large Department with YAML Export)
Calculate requirements for a department with 500 hosts and export for documentation.
- **Input**: `--hosts 500 --format yaml`
- **Output**: Detailed YAML block with /23 prefix information.

## CLI Usage
**Calculate by host count:**
```bash
python3 cidr_architect.py --hosts 25
```

**Calculate with a specific base IP:**
```bash
python3 cidr_architect.py --hosts 100 --base 10.0.0.0
```

**Output in YAML format:**
```bash
python3 cidr_architect.py --hosts 50 --format yaml
```

## Sample YAML Output
```yaml
cidr: 192.168.1.0/26
prefix: 26
netmask: 255.255.255.192
wildcard: 0.0.0.63
network_address: 192.168.1.0
broadcast_address: 192.168.1.63
first_usable: 192.168.1.1
last_usable: 192.168.1.62
total_hosts: 62
```
