#!/usr/bin/env python3
"""
Topology Composer - Generates bulk CLI commands from topology definitions
Converts YAML/JSON/XML topology specs into copy-paste-ready configurations for Packet Tracer

This tool takes your network topology definition and outputs all the CLI commands
needed to configure devices in Packet Tracer, eliminating manual typing.

Supports YAML, JSON, and XML input formats.
"""

import json
import argparse
import sys
import os

# Import format parser from shared utility
sys.path.insert(0, os.path.dirname(__file__))
from format_parser import parse_file


class TopologyComposer:
    """Generates CLI commands from topology definitions."""
    
    def __init__(self, topology_data):
        self.topology = topology_data
        self.commands = {}
    
    def generate_device_config(self, device):
        """Generate CLI commands for a single device."""
        hostname = device.get('hostname', 'Router')
        device_type = device.get('type', 'router').lower()
        commands = []
        
        # Enable commands
        commands.append("enable")
        commands.append("configure terminal")
        
        # Hostname
        commands.append(f"hostname {hostname}")
        
        # Interfaces
        if 'interfaces' in device:
            for iface in device['interfaces']:
                iface_name = iface.get('name', '')
                ip = iface.get('ip')
                mask = iface.get('mask')
                vlan = iface.get('vlan')
                description = iface.get('description', '')
                
                if vlan:
                    commands.append(f"interface vlan {vlan}")
                else:
                    commands.append(f"interface {iface_name}")
                
                if description:
                    commands.append(f" description {description}")
                
                if ip and mask:
                    commands.append(f" ip address {ip} {mask}")
                
                commands.append(" no shutdown")
                commands.append(" exit")
        
        # OSPF Configuration
        if 'ospf' in device:
            ospf = device['ospf']
            pid = ospf.get('process_id', 1)
            rid = ospf.get('router_id', '')
            
            commands.append(f"router ospf {pid}")
            
            if rid:
                commands.append(f" router-id {rid}")
            
            if 'networks' in ospf:
                for net in ospf['networks']:
                    network = net.get('network')
                    wildcard = net.get('wildcard')
                    area = net.get('area', 0)
                    if network and wildcard:
                        commands.append(f" network {network} {wildcard} area {area}")
            
            commands.append(" exit")
        
        # BGP Configuration
        if 'bgp' in device:
            bgp = device['bgp']
            asn = bgp.get('asn')
            rid = bgp.get('router_id', '')
            
            if asn:
                commands.append(f"router bgp {asn}")
                
                if rid:
                    commands.append(f" bgp router-id {rid}")
                
                if 'neighbors' in bgp:
                    for neighbor in bgp['neighbors']:
                        neighbor_ip = neighbor.get('ip')
                        neighbor_asn = neighbor.get('asn')
                        description = neighbor.get('description', '')
                        
                        if neighbor_ip and neighbor_asn:
                            commands.append(f" neighbor {neighbor_ip} remote-as {neighbor_asn}")
                            if description:
                                commands.append(f" neighbor {neighbor_ip} description {description}")
                
                if 'networks' in bgp:
                    for net in bgp['networks']:
                        network = net.get('network')
                        mask = net.get('mask')
                        if network and mask:
                            commands.append(f" network {network} mask {mask}")
                
                commands.append(" exit")
        
        # EIGRP Configuration
        if 'eigrp' in device:
            eigrp = device['eigrp']
            asn = eigrp.get('asn')
            rid = eigrp.get('router_id', '')
            
            if asn:
                commands.append(f"router eigrp {asn}")
                
                if rid:
                    commands.append(f" eigrp router-id {rid}")
                
                if 'networks' in eigrp:
                    for net in eigrp['networks']:
                        network = net.get('network')
                        wildcard = net.get('wildcard')
                        if network and wildcard:
                            commands.append(f" network {network} {wildcard}")
                
                commands.append(" exit")
        
        # DHCP Configuration
        if 'dhcp' in device:
            dhcp = device['dhcp']
            if 'pools' in dhcp:
                for pool in dhcp['pools']:
                    pool_name = pool.get('name')
                    network = pool.get('network')
                    mask = pool.get('mask')
                    gateway = pool.get('gateway')
                    dns = pool.get('dns', '8.8.8.8')
                    
                    if pool_name and network and mask:
                        commands.append(f"ip dhcp pool {pool_name}")
                        commands.append(f" network {network} {mask}")
                        if gateway:
                            commands.append(f" default-router {gateway}")
                        commands.append(f" dns-server {dns}")
                        commands.append(" exit")
            
            if 'excluded' in dhcp:
                for excluded in dhcp['excluded']:
                    start = excluded.get('start')
                    end = excluded.get('end')
                    if start:
                        if end:
                            commands.append(f"ip dhcp excluded-address {start} {end}")
                        else:
                            commands.append(f"ip dhcp excluded-address {start}")
        
        # HSRP Configuration
        if 'hsrp' in device:
            hsrp = device['hsrp']
            if 'groups' in hsrp:
                for group in hsrp['groups']:
                    vlan = group.get('vlan')
                    gid = group.get('group_id')
                    priority = group.get('priority', 100)
                    virtual_ip = group.get('virtual_ip')
                    
                    if vlan and gid and virtual_ip:
                        commands.append(f"interface vlan {vlan}")
                        commands.append(f" standby {gid} ip {virtual_ip}")
                        commands.append(f" standby {gid} priority {priority}")
                        commands.append(f" standby {gid} preempt")
                        commands.append(" no shutdown")
                        commands.append(" exit")
        
        # NAT Configuration
        if 'nat' in device:
            nat = device['nat']
            
            if 'inside_interfaces' in nat:
                for iface in nat['inside_interfaces']:
                    commands.append(f"interface {iface}")
                    commands.append(" ip nat inside")
                    commands.append(" exit")
            
            if 'outside_interfaces' in nat:
                for iface in nat['outside_interfaces']:
                    commands.append(f"interface {iface}")
                    commands.append(" ip nat outside")
                    commands.append(" exit")
            
            if 'static' in nat:
                for mapping in nat['static']:
                    inside_ip = mapping.get('inside_ip')
                    outside_ip = mapping.get('outside_ip')
                    if inside_ip and outside_ip:
                        commands.append(f"ip nat inside source static {inside_ip} {outside_ip}")
            
            if 'dynamic' in nat:
                for pool in nat['dynamic']:
                    pool_name = pool.get('name')
                    start_ip = pool.get('start_ip')
                    end_ip = pool.get('end_ip')
                    if pool_name and start_ip and end_ip:
                        commands.append(f"ip nat pool {pool_name} {start_ip} {end_ip} netmask 255.255.255.0")
        
        # Static Routes
        if 'static_routes' in device:
            for route in device['static_routes']:
                destination = route.get('destination')
                mask = route.get('mask')
                next_hop = route.get('next_hop')
                if destination and mask and next_hop:
                    commands.append(f"ip route {destination} {mask} {next_hop}")
        
        # SSH/Security
        if 'ssh' in device:
            ssh = device['ssh']
            if ssh.get('enabled'):
                commands.append("ip domain-name lab.local")
                commands.append("crypto key generate rsa modulus 1024")
                commands.append("line vty 0 4")
                commands.append(" transport input ssh")
                commands.append(" exit")
        
        # Access Lists
        if 'acls' in device:
            for acl in device['acls']:
                acl_num = acl.get('number')
                if 'rules' in acl:
                    for rule in acl['rules']:
                        action = rule.get('action', 'permit')
                        protocol = rule.get('protocol', 'ip')
                        source = rule.get('source')
                        destination = rule.get('destination', 'any')
                        if source:
                            commands.append(f"access-list {acl_num} {action} {protocol} {source} {destination}")
        
        commands.append("end")
        commands.append("write memory")
        
        return commands
    
    def compose(self):
        """Generate all device configurations."""
        if 'devices' not in self.topology:
            return {}
        
        for device in self.topology['devices']:
            hostname = device.get('hostname', 'Device')
            self.commands[hostname] = self.generate_device_config(device)
        
        return self.commands
    
    def output_text(self):
        """Output commands in a copy-paste format."""
        output = []
        for hostname, commands in self.commands.items():
            output.append(f"\n{'='*60}")
            output.append(f"Configuration for: {hostname}")
            output.append(f"{'='*60}\n")
            output.extend(commands)
            output.append("\n")
        
        return "\n".join(output)
    
    def output_by_device(self):
        """Output commands organized by device."""
        result = {}
        for hostname, commands in self.commands.items():
            result[hostname] = "\n".join(commands)
        return result


def main():
    parser = argparse.ArgumentParser(
        description="Topology Composer - Generate bulk CLI commands from topology definitions"
    )
    parser.add_argument(
        "--file",
        help="Path to topology definition (YAML, JSON, or XML)",
        required=True
    )
    parser.add_argument(
        "--output",
        help="Output file (if not specified, prints to stdout)",
        default=None
    )
    parser.add_argument(
        "--format",
        choices=['text', 'json'],
        default='text',
        help="Output format: text (copy-paste ready) or json"
    )
    
    args = parser.parse_args()
    
    try:
        topology_data = parse_file(args.file)
    except Exception as e:
        print(f"❌ Error loading topology file: {e}", file=sys.stderr)
        sys.exit(1)
    
    composer = TopologyComposer(topology_data)
    composer.compose()
    
    if args.format == 'json':
        output = json.dumps(composer.output_by_device(), indent=2)
    else:
        output = composer.output_text()
    
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✅ Configuration written to {args.output}")
        except Exception as e:
            print(f"❌ Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == "__main__":
    main()
