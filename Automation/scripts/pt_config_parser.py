#!/usr/bin/env python3
"""
Keystone PT Config Parser
Parses extracted Cisco configs and generates new topologies with modifications
"""

import re
import sys
import json
from pathlib import Path

class CiscoConfigParser:
    def __init__(self):
        self.hostname = None
        self.interfaces = {}
        self.routing_protocols = {
            'ospf': {},
            'bgp': {},
            'eigrp': {},
            'static': []
        }
        self.services = {
            'dhcp': {},
            'nat': {'inside': [], 'outside': [], 'static': [], 'dynamic': []},
            'hsrp': [],
            'ssh': False,
            'vlan': {}
        }
    
    def parse_running_config(self, config_text):
        """Parse Cisco IOS running config"""
        lines = config_text.split('\n')
        current_context = None
        current_interface = None
        
        for line in lines:
            line = line.rstrip()
            
            # Skip empty lines and banners
            if not line or line.startswith('!'):
                continue
            
            # Hostname
            if line.startswith('hostname '):
                self.hostname = line.replace('hostname ', '').strip()
                continue
            
            # Interface configuration
            if line.startswith('interface '):
                match = re.match(r'interface\s+(\S+)', line)
                if match:
                    current_interface = match.group(1)
                    self.interfaces[current_interface] = {}
                    current_context = 'interface'
                continue
            
            # Interface IP configuration
            if current_interface and current_context == 'interface':
                if line.strip().startswith('ip address '):
                    match = re.match(r'\s+ip address\s+(\S+)\s+(\S+)', line)
                    if match:
                        self.interfaces[current_interface]['ip'] = match.group(1)
                        self.interfaces[current_interface]['mask'] = match.group(2)
                
                elif line.strip().startswith('description '):
                    desc = line.strip().replace('description ', '').strip('"')
                    self.interfaces[current_interface]['description'] = desc
                
                elif line.strip().startswith('no shutdown'):
                    self.interfaces[current_interface]['enabled'] = True
            
            # OSPF configuration
            if line.startswith('router ospf '):
                match = re.match(r'router ospf\s+(\d+)', line)
                if match:
                    pid = match.group(1)
                    self.routing_protocols['ospf']['process_id'] = int(pid)
                    current_context = 'ospf'
                    self.routing_protocols['ospf']['networks'] = []
                continue
            
            if current_context == 'ospf':
                if line.strip().startswith('router-id '):
                    rid = line.strip().replace('router-id ', '').strip()
                    self.routing_protocols['ospf']['router_id'] = rid
                
                elif line.strip().startswith('network '):
                    match = re.match(r'\s+network\s+(\S+)\s+(\S+)\s+area\s+(\S+)', line)
                    if match:
                        network_entry = {
                            'network': match.group(1),
                            'wildcard': match.group(2),
                            'area': int(match.group(3))
                        }
                        self.routing_protocols['ospf']['networks'].append(network_entry)
            
            # BGP configuration
            if line.startswith('router bgp '):
                match = re.match(r'router bgp\s+(\d+)', line)
                if match:
                    asn = match.group(1)
                    self.routing_protocols['bgp']['asn'] = int(asn)
                    current_context = 'bgp'
                    self.routing_protocols['bgp']['neighbors'] = []
                continue
            
            if current_context == 'bgp':
                if line.strip().startswith('neighbor '):
                    match = re.match(r'\s+neighbor\s+(\S+)\s+remote-as\s+(\d+)', line)
                    if match:
                        neighbor = {
                            'ip': match.group(1),
                            'asn': int(match.group(2))
                        }
                        self.routing_protocols['bgp']['neighbors'].append(neighbor)
            
            # DHCP configuration
            if line.startswith('ip dhcp pool '):
                pool_name = line.replace('ip dhcp pool ', '').strip()
                self.services['dhcp'][pool_name] = {'excluded': []}
                current_context = 'dhcp'
                current_dhcp_pool = pool_name
                continue
            
            if current_context == 'dhcp':
                if line.strip().startswith('network '):
                    match = re.match(r'\s+network\s+(\S+)\s+(\S+)', line)
                    if match:
                        self.services['dhcp'][current_dhcp_pool]['network'] = match.group(1)
                        self.services['dhcp'][current_dhcp_pool]['mask'] = match.group(2)
                
                elif line.strip().startswith('default-router '):
                    gw = line.strip().replace('default-router ', '').strip()
                    self.services['dhcp'][current_dhcp_pool]['gateway'] = gw
                
                elif line.strip().startswith('dns-server '):
                    dns = line.strip().replace('dns-server ', '').strip()
                    self.services['dhcp'][current_dhcp_pool]['dns'] = dns
            
            # NAT configuration
            if line.startswith('ip nat inside source '):
                self.services['nat']['dynamic'].append(line.strip())
            elif line.startswith('ip nat outside source '):
                self.services['nat']['static'].append(line.strip())
            elif line.startswith('ip nat inside'):
                self.services['nat']['inside'].append(line.strip())
            elif line.startswith('ip nat outside'):
                self.services['nat']['outside'].append(line.strip())
            
            # SSH
            if 'ip ssh' in line or 'crypto key generate rsa' in line:
                self.services['ssh'] = True
        
        return self
    
    def to_yaml_topology(self, device_type='router'):
        """Convert parsed config to YAML topology format"""
        
        yaml_lines = [
            "# Auto-generated topology from PT config analysis",
            f"# Device: {self.hostname}",
            "devices:",
            f"  - hostname: {self.hostname}",
            f"    type: {device_type}",
        ]
        
        # Interfaces
        if self.interfaces:
            yaml_lines.append("    interfaces:")
            for iface_name, iface_config in self.interfaces.items():
                yaml_lines.append(f"      - name: {iface_name}")
                if 'ip' in iface_config:
                    yaml_lines.append(f"        ip: {iface_config['ip']}")
                    yaml_lines.append(f"        mask: {iface_config['mask']}")
                if 'description' in iface_config:
                    yaml_lines.append(f"        description: \"{iface_config['description']}\"")
        
        # OSPF
        if self.routing_protocols['ospf']:
            ospf = self.routing_protocols['ospf']
            yaml_lines.append("    ospf:")
            if 'process_id' in ospf:
                yaml_lines.append(f"      process_id: {ospf['process_id']}")
            if 'router_id' in ospf:
                yaml_lines.append(f"      router_id: {ospf['router_id']}")
            if 'networks' in ospf and ospf['networks']:
                yaml_lines.append("      networks:")
                for net in ospf['networks']:
                    yaml_lines.append(f"        - network: {net['network']}")
                    yaml_lines.append(f"          wildcard: {net['wildcard']}")
                    yaml_lines.append(f"          area: {net['area']}")
        
        # BGP
        if self.routing_protocols['bgp']:
            bgp = self.routing_protocols['bgp']
            yaml_lines.append("    bgp:")
            if 'asn' in bgp:
                yaml_lines.append(f"      asn: {bgp['asn']}")
            if 'neighbors' in bgp and bgp['neighbors']:
                yaml_lines.append("      neighbors:")
                for neighbor in bgp['neighbors']:
                    yaml_lines.append(f"        - ip: {neighbor['ip']}")
                    yaml_lines.append(f"          asn: {neighbor['asn']}")
        
        # DHCP
        if self.services['dhcp']:
            yaml_lines.append("    dhcp:")
            yaml_lines.append("      pools:")
            for pool_name, pool_config in self.services['dhcp'].items():
                yaml_lines.append(f"        - name: {pool_name}")
                if 'network' in pool_config:
                    yaml_lines.append(f"          network: {pool_config['network']}")
                    yaml_lines.append(f"          mask: {pool_config['mask']}")
                if 'gateway' in pool_config:
                    yaml_lines.append(f"          gateway: {pool_config['gateway']}")
                if 'dns' in pool_config:
                    yaml_lines.append(f"          dns: \"{pool_config['dns']}\"")
        
        # NAT
        if any([self.services['nat']['inside'], self.services['nat']['outside'], 
                self.services['nat']['static'], self.services['nat']['dynamic']]):
            yaml_lines.append("    nat:")
            if self.services['nat']['inside']:
                yaml_lines.append("      inside_interfaces:")
                for iface in self.services['nat']['inside']:
                    yaml_lines.append(f"        - {iface}")
            if self.services['nat']['outside']:
                yaml_lines.append("      outside_interfaces:")
                for iface in self.services['nat']['outside']:
                    yaml_lines.append(f"        - {iface}")
        
        # SSH
        if self.services['ssh']:
            yaml_lines.append("    ssh:")
            yaml_lines.append("      enabled: true")
        
        return '\n'.join(yaml_lines)
    
    def to_json_topology(self, device_type='router'):
        """Convert to JSON topology"""
        
        config = {
            'hostname': self.hostname,
            'type': device_type,
            'interfaces': self.interfaces,
            'routing': self.routing_protocols,
            'services': self.services
        }
        
        return json.dumps({'devices': [config]}, indent=2)
    
    def display_summary(self):
        """Print parsed configuration summary"""
        
        print(f"\n{'═'*60}")
        print(f"PARSED CONFIGURATION SUMMARY")
        print(f"{'═'*60}\n")
        
        print(f"Hostname: {self.hostname}")
        print(f"Interfaces configured: {len(self.interfaces)}")
        
        for iface, config in self.interfaces.items():
            print(f"  - {iface}")
            if 'ip' in config:
                print(f"    IP: {config['ip']}/{self._mask_to_cidr(config.get('mask', '0.0.0.0'))}")
            if 'description' in config:
                print(f"    Description: {config['description']}")
        
        print(f"\nRouting Protocols:")
        if self.routing_protocols['ospf']:
            print(f"  ✓ OSPF (PID: {self.routing_protocols['ospf'].get('process_id', 'N/A')})")
        if self.routing_protocols['bgp']:
            print(f"  ✓ BGP (ASN: {self.routing_protocols['bgp'].get('asn', 'N/A')})")
        
        print(f"\nServices:")
        if self.services['dhcp']:
            print(f"  ✓ DHCP ({len(self.services['dhcp'])} pools)")
        if any([self.services['nat']['inside'], self.services['nat']['outside']]):
            print(f"  ✓ NAT")
        if self.services['ssh']:
            print(f"  ✓ SSH")
        
        print(f"\n{'═'*60}\n")
    
    @staticmethod
    def _mask_to_cidr(mask):
        """Convert subnet mask to CIDR notation"""
        parts = mask.split('.')
        if len(parts) != 4:
            return '24'
        bits = 0
        for part in parts:
            bits += bin(int(part)).count('1')
        return str(bits)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pt_config_parser.py <config_file.txt> [--yaml|--json]")
        print("\nExample:")
        print("  python3 pt_config_parser.py router_config.txt --yaml")
        print("  python3 pt_config_parser.py router_config.txt --json")
        sys.exit(1)
    
    config_file = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else '--yaml'
    
    if not Path(config_file).exists():
        print(f"❌ File not found: {config_file}")
        sys.exit(1)
    
    # Read config
    with open(config_file, 'r') as f:
        config_text = f.read()
    
    # Parse
    parser = CiscoConfigParser()
    parser.parse_running_config(config_text)
    
    # Display summary
    parser.display_summary()
    
    # Generate output
    if '--json' in output_format:
        output = parser.to_json_topology()
        output_file = config_file.replace('.txt', '_topology.json')
    else:  # Default to YAML
        output = parser.to_yaml_topology()
        output_file = config_file.replace('.txt', '_topology.yaml')
    
    # Save
    with open(output_file, 'w') as f:
        f.write(output)
    
    print(f"✅ Generated: {output_file}\n")
    print(output)


if __name__ == '__main__':
    main()
