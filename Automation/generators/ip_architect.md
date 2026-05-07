# IPv4 Address and Subnet Generator

## Purpose and Design
The `ip_generator.py` script is a utility for generating IPv4 addresses and subnets for network simulations and lab environments. It provides static methods within the `IPGenerator` class to handle both individual address generation (Private and Public) and subnet division.

## Key Features
- **Address Generation**: Generate random or sequential IPs from RFC 1918 (Private) or common simulation (Public) ranges.
- **Subnetting**: Divide a parent network into smaller subnets based on a new prefix.
- **Formatting**: Output results as a simple list or a structured YAML block.

## Examples

### Example 1: Simple Scenario (Generate Random Private IPs)
Generate 10 random private Class C addresses for testing.
- **Mode**: IP
- **Class**: C
- **Type**: Private

### Example 2: Advanced Scenario (Sequential Subnet Generation)
Create a set of /26 subnets from a larger /24 parent network.
- **Mode**: Subnet
- **Parent**: 192.168.10.0/24
- **Prefix**: 26

## CLI Usage
**Generate individual IPs:**
```bash
python3 ip_generator.py --mode ip --count 10 --class C --type private
```

**Generate subnets from a parent network:**
```bash
python3 ip_generator.py --mode subnet --parent 10.0.0.0/8 --prefix 24 --count 5
```

**Output in YAML format:**
```bash
python3 ip_generator.py --count 5 --format yaml
```

## Sample YAML Output
```yaml
items:
  - 192.168.1.15
  - 192.168.1.42
  - 192.168.1.103
  - 192.168.1.2
  - 192.168.1.250
```
