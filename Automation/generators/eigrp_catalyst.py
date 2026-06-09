import json
import ipaddress
import argparse
import sys
from format_parser import parse_file, detect_format, normalize_entries, entry_name, normalize_interface_name, normalize_items

class EIGRPInterface:
    """Represents a network interface with EIGRP configuration."""
    def __init__(self, name, ip_address=None, subnet_mask=None, is_passive=False, ipv6_enabled=False):
        self.name = normalize_interface_name(name)
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.is_passive = is_passive
        self.ipv6_enabled = ipv6_enabled

    def get_network_and_wildcard(self):
        """Calculates the network address and wildcard mask (IPv4)."""
        if not self.ip_address or not self.subnet_mask:
            return None, None
        try:
            if ':' in str(self.ip_address):
                return None, None
            interface = ipaddress.IPv4Interface(f"{self.ip_address}/{self.subnet_mask}")
            network = interface.network.network_address
            
            # Calculate wildcard by XORing 255.255.255.255 with netmask
            netmask_parts = [int(p) for p in self.subnet_mask.split('.')]
            wildcard_parts = [255 - p for p in netmask_parts]
            wildcard = ".".join(map(str, wildcard_parts))
            
            return str(network), wildcard
        except ValueError:
            return None, None

class EIGRPRouter:
    """Represents a router running EIGRP."""
    def __init__(self, hostname, as_number, router_id=None, is_stub=False, ipv6_as_number=None):
        self.hostname = hostname
        self.as_number = as_number
        self.router_id = router_id
        self.is_stub = is_stub
        self.ipv6_as_number = ipv6_as_number
        self.interfaces = []

    def add_interface(self, name, ip_address=None, subnet_mask=None, is_passive=False, ipv6_enabled=False):
        self.interfaces.append(EIGRPInterface(normalize_interface_name(name), ip_address, subnet_mask, is_passive, ipv6_enabled))

    def generate_cli_config(self):
        """Generates Cisco IOS CLI commands for EIGRP (IPv4 and IPv6)."""
        lines = [f"! EIGRP Configuration for {self.hostname}"]
        
        # IPv6 Interface level config
        if self.ipv6_as_number is not None:
            for iface in self.interfaces:
                if iface.ipv6_enabled:
                    lines.append(f"interface {iface.name}")
                    lines.append(f" ipv6 eigrp {self.ipv6_as_number}")
                    lines.append(" exit")

        # IPv4 Router EIGRP
        lines.append(f"router eigrp {self.as_number}")
        if self.router_id:
            lines.append(f" eigrp router-id {self.router_id}")
        if self.is_stub:
            lines.append(" eigrp stub connected summary")
            
        # Passive interfaces (IPv4)
        passive_ifs = [iface.name for iface in self.interfaces if iface.is_passive]
        if passive_ifs:
            for iface_name in passive_ifs:
                lines.append(f" passive-interface {iface_name}")
            
        # Network statements (IPv4)
        networks = []
        for iface in self.interfaces:
            net, wildcard = iface.get_network_and_wildcard()
            if net and wildcard:
                networks.append(f" network {net} {wildcard}")
        
        lines.extend(sorted(list(set(networks))))
        lines.append(" no auto-summary")
        lines.append(" exit")

        # IPv6 Router EIGRP
        if self.ipv6_as_number is not None:
            lines.append(f"ipv6 router eigrp {self.ipv6_as_number}")
            if self.router_id:
                lines.append(f" eigrp router-id {self.router_id}")
            if self.is_stub:
                lines.append(" eigrp stub connected summary")
            # Passive interfaces (IPv6)
            for iface in self.interfaces:
                if iface.is_passive and iface.ipv6_enabled:
                    lines.append(f" passive-interface {iface.name}")
            lines.append(" no shutdown")
            lines.append(" exit")
            
        return "\n".join(lines)

    def to_dict(self):
        """Returns a dictionary representation for JSON export."""
        return {
            "hostname": self.hostname,
            "as_number": self.as_number,
            "ipv6_as_number": self.ipv6_as_number,
            "router_id": self.router_id,
            "is_stub": self.is_stub,
            "interfaces": [
                {
                    "name": i.name,
                    "ip_address": i.ip_address,
                    "subnet_mask": i.subnet_mask,
                    "is_passive": i.is_passive,
                    "ipv6_enabled": i.ipv6_enabled
                } for i in self.interfaces
            ]
        }

def load_from_file(filepath):
    """Loads router configurations from a JSON, YAML, or XML file."""
    try:
        data = normalize_entries(parse_file(filepath), preferred_keys=('items', 'devices'))
        
        routers = []
        for idx, r_data in enumerate(data):
            if not isinstance(r_data, dict):
                continue
            router = EIGRPRouter(entry_name(r_data, idx), r_data.get('as_number', 100), 
                                r_data.get('router_id'),
                                r_data.get('is_stub', False),
                                r_data.get('ipv6_as_number'))
            for i_data in normalize_items(r_data.get('interfaces', [])):
                if not isinstance(i_data, dict):
                    continue
                router.add_interface(
                    i_data['name'], 
                    i_data.get('ip_address'), 
                    i_data.get('subnet_mask'),
                    i_data.get('is_passive', False),
                    i_data.get('ipv6_enabled', False)
                )
            routers.append(router)
        return routers
    except Exception as e:
        print(f"Error loading file: {e}")
        return []

def interactive_mode():
    """Runs the interactive CLI to gather user input."""
    print("=== EIGRP Configuration Generator (Interactive) ===")
    routers = []
    
    while True:
        hostname = input("\nEnter Router Hostname (or 'done'): ").strip()
        if hostname.lower() == 'done': break
            
        as_num = input("Enter EIGRP AS Number: ").strip()
        router_id = input("Enter Router ID (optional, e.g., 1.1.1.1): ").strip() or None
        is_stub = input("Is this a stub router? (y/n) [n]: ").strip().lower() == 'y'
        
        router = EIGRPRouter(hostname, int(as_num), router_id, is_stub)
        
        while True:
            if_name = input(f"  Interface Name (e.g., Gi0/0) or 'done': ").strip()
            if if_name.lower() == 'done': break
                
            ip = input(f"  IP Address: ").strip()
            mask = input(f"  Subnet Mask: ").strip()
            passive = input(f"  Passive? (y/n) [n]: ").strip().lower() == 'y'
            
            router.add_interface(if_name, ip, mask, passive)
            
        routers.append(router)
    return routers

def main():
    parser = argparse.ArgumentParser(description="Generate EIGRP configurations for Cisco IOS/Packet Tracer.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    parser.add_argument("--output", help="Path to save generated CLI config")
    parser.add_argument("--json-out", help="Path to save inventory as JSON")
    
    args = parser.parse_args()
    
    if args.file:
        routers = load_from_file(args.file)
    else:
        routers = interactive_mode()
        
    if not routers:
        print("No router configurations found.")
        return

    full_config = ""
    for router in routers:
        config = router.generate_cli_config()
        print(f"\n! --- {router.hostname} ---")
        print(config)
        full_config += config + "\n"
        
    if args.output:
        with open(args.output, 'w') as f:
            f.write(full_config)
        print(f"\nSaved CLI config to {args.output}")

    if args.json_out:
        with open(args.json_out, 'w') as f:
            json.dump([r.to_dict() for r in routers], f, indent=4)
        print(f"Saved JSON inventory to {args.json_out}")

if __name__ == "__main__":
    main()
