# Portal

## Purpose and Design
The `Portal.py` script is a comprehensive tool for generating Cisco IOS Network Address Translation (NAT) and Port Address Translation (PAT) configurations. It uses an Object-Oriented design to handle the complexity of different NAT types:
- `IOSNATRule`: Models individual translation rules (Static, Dynamic, Overload, Port-Forward).
- `IOSNATRouter`: Manages the overall NAT configuration for a router, including interfaces, pools, and ACLs.

## Key Features
- **Multiple NAT Types**: Support for Static NAT, Dynamic NAT, PAT (Overload), and Port Forwarding.
- **Interface Management**: Easily define inside and outside NAT roles for interfaces.
- **NVI Support**: Optional support for NAT Virtual Interface (`ip nat enable`).
- **YAML Support**: Read industry-standard YAML files for configuration inventory.

## Examples

### Example 1: Simple Scenario (Basic PAT/Overload)
Standard internet access setup using PAT on the outside interface.
- **Inside**: GigabitEthernet0/0
- **Outside**: GigabitEthernet0/1
- **Action**: Overload internal traffic using the outside interface IP.

### Example 2: Advanced Scenario (NAT with Port Forwarding and Pools)
A complex setup with a dynamic NAT pool and port forwarding for an internal server.
- **Pool**: 203.0.113.10 to 203.0.113.20.
- **Port Forwarding**: TCP Port 80 on the outside interface forwarded to an internal web server (192.168.1.100).

## CLI Usage
**Generate from YAML file:**
```bash
python3 Portal.py --file nat_config.yaml
```

**Generate from JSON file:**
```bash
python3 Portal.py --file nat_config.json
```

## Sample YAML Input
```yaml
- hostname: Edge-Router-01
  inside_interfaces:
    - GigabitEthernet0/0
  outside_interfaces:
    - GigabitEthernet0/1
  acls:
    1:
      - 192.168.1.0 0.0.0.255
  rules:
    - rule_type: overload
      acl_id: 1
      interface: GigabitEthernet0/1
      description: Default PAT for Internal LAN
    - rule_type: port-forward
      local_ip: 192.168.1.100
      local_port: 80
      global_ip: 203.0.113.1
      global_port: 80
      protocol: tcp
      description: Forward HTTP to Web Server
```
