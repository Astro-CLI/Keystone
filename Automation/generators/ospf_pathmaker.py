import json
import ipaddress
import argparse
import sys
from format_parser import parse_file, detect_format, normalize_entries, entry_name, normalize_interface_name, normalize_items

class OSPFInterface:
    """Represents a network interface with OSPF configuration."""
    def __init__(self, name, ip_address=None, subnet_mask=None, area=0, is_passive=False, 
                 auth_type=None, auth_key=None, ipv6_area=None, ipv6_address=None):
        self.name = normalize_interface_name(name)
        self.ip_address = ip_address
        self.subnet_mask = subnet_mask
        self.area = area
        self.is_passive = is_passive
        self.auth_type = auth_type # 'message-digest' or 'cleartext'
        self.auth_key = auth_key
        self.ipv6_area = ipv6_area # If set, interface participates in IPv6 OSPF
        self.ipv6_address = ipv6_address # e.g., '2001:db8::1/64'

    def get_network_and_wildcard(self):
        """Calculates the network address and wildcard mask (IPv4)."""
        if not self.ip_address or not self.subnet_mask:
            return None, None
        try:
            # Check if this is an IPv6 address (skip for IPv4 network statements)
            if ':' in str(self.ip_address):
                return None, None
                
            interface = ipaddress.IPv4Interface(f"{self.ip_address}/{self.subnet_mask}")
            network = interface.network.network_address
            
            # Calculate wildcard by XORing 255.255.255.255 with netmask
            netmask_parts = [int(p) for p in self.subnet_mask.split('.')]
            wildcard_parts = [255 - p for p in netmask_parts]
            wildcard = ".".join(map(str, wildcard_parts))
            
            return str(network), wildcard
        except (ValueError, AttributeError):
            return None, None

class OSPFRouter:
    """Represents a router running OSPF."""
    def __init__(self, hostname, router_id, process_id=1, use_interface_config=False, ipv6_process_id=None):
        self.hostname = hostname
        self.router_id = router_id
        self.process_id = process_id
        self.use_interface_config = use_interface_config
        self.ipv6_process_id = ipv6_process_id
        self.interfaces = []

    def add_interface(self, name, ip_address=None, subnet_mask=None, area=0, 
                      is_passive=False, auth_type=None, auth_key=None, ipv6_area=None, ipv6_address=None):
        self.interfaces.append(OSPFInterface(normalize_interface_name(name), ip_address, subnet_mask, area, 
                                            is_passive, auth_type, auth_key, ipv6_area, ipv6_address))

    def generate_cli_config(self):
        """Generates Cisco IOS CLI commands for OSPF (v2 and v3)."""
        lines = [f"! OSPF Configuration for {self.hostname}"]
        
        # Global IPv6 Routing
        if self.ipv6_process_id is not None:
            lines.append("ipv6 unicast-routing")
        
        # Interface level config (IPs and OSPF)
        for iface in self.interfaces:
            iface_lines = []
            
            # Foundational IP Addressing
            if iface.ip_address and iface.subnet_mask:
                iface_lines.append(f" ip address {iface.ip_address} {iface.subnet_mask}")
            if iface.ipv6_address:
                iface_lines.append(f" ipv6 address {iface.ipv6_address}")
            
            # IPv4 OSPF interface config
            if self.use_interface_config:
                iface_lines.append(f" ip ospf {self.process_id} area {iface.area}")
                if iface.auth_type == 'message-digest':
                    iface_lines.append(f" ip ospf authentication message-digest")
                    iface_lines.append(f" ip ospf message-digest-key 1 md5 {iface.auth_key}")
                elif iface.auth_type == 'cleartext':
                    iface_lines.append(f" ip ospf authentication")
                    iface_lines.append(f" ip ospf authentication-key {iface.auth_key}")
            
            # IPv6 OSPF interface config
            if self.ipv6_process_id is not None and iface.ipv6_area is not None:
                iface_lines.append(f" ipv6 ospf {self.ipv6_process_id} area {iface.ipv6_area}")
            
            if iface_lines:
                lines.append(f"interface {iface.name}")
                lines.extend(iface_lines)
                lines.append(" no shutdown")
                lines.append(" exit")

        # Global IPv4 Router OSPF config
        lines.append(f"router ospf {self.process_id}")
        lines.append(f" router-id {self.router_id}")
        
        # Passive interfaces (IPv4)
        for iface in self.interfaces:
            if iface.is_passive:
                lines.append(f" passive-interface {iface.name}")
            
        # Network statements (if not using interface level config)
        if not self.use_interface_config:
            networks = []
            for iface in self.interfaces:
                net, wildcard = iface.get_network_and_wildcard()
                if net and wildcard:
                    networks.append(f" network {net} {wildcard} area {iface.area}")
            
            # Remove duplicates
            lines.extend(sorted(list(set(networks))))
        
        lines.append(" exit")

        # Global IPv6 Router OSPF config
        if self.ipv6_process_id is not None:
            lines.append(f"ipv6 router ospf {self.ipv6_process_id}")
            lines.append(f" router-id {self.router_id}") # IPv6 OSPF still uses 32-bit ID
            for iface in self.interfaces:
                if iface.is_passive:
                    lines.append(f" passive-interface {iface.name}")
            lines.append(" exit")
            
        return "\n".join(lines)

    def to_dict(self):
        """Returns a dictionary representation for JSON export."""
        return {
            "hostname": self.hostname,
            "router_id": self.router_id,
            "process_id": self.process_id,
            "ipv6_process_id": self.ipv6_process_id,
            "use_interface_config": self.use_interface_config,
            "interfaces": [
                {
                    "name": i.name,
                    "ip_address": i.ip_address,
                    "subnet_mask": i.subnet_mask,
                    "ipv6_address": i.ipv6_address,
                    "area": i.area,
                    "ipv6_area": i.ipv6_area,
                    "is_passive": i.is_passive,
                    "auth_type": i.auth_type,
                    "auth_key": i.auth_key
                } for i in self.interfaces
            ]
        }

def load_from_file(filepath):
    """Loads router configurations from JSON, YAML, or XML file."""
    try:
        data = normalize_entries(parse_file(filepath), preferred_keys=('items', 'devices'))
        
        routers = []
        for idx, r_data in enumerate(data):
            if not isinstance(r_data, dict):
                continue
            router = OSPFRouter(entry_name(r_data, idx), r_data.get('router_id', '1.1.1.1'),
                                r_data.get('process_id', 1),
                                r_data.get('use_interface_config', False),
                                r_data.get('ipv6_process_id'))
            for i_data in normalize_items(r_data.get('interfaces', [])):
                if not isinstance(i_data, dict):
                    continue
                router.add_interface(
                    i_data['name'], 
                    i_data.get('ip_address'), 
                    i_data.get('subnet_mask'),
                    i_data.get('area', 0),
                    i_data.get('is_passive', False),
                    i_data.get('auth_type'),
                    i_data.get('auth_key'),
                    i_data.get('ipv6_area'),
                    i_data.get('ipv6_address')
                )
            routers.append(router)
        return routers
    except Exception as e:
        print(f"Error loading file: {e}")
        return []

def interactive_mode():
    """Runs the interactive CLI to gather user input."""
    print("=== OSPF Pathmaker (Interactive) ===")
    routers = []
    
    while True:
        hostname = input("\nEnter Router Hostname (or 'done'): ").strip()
        if hostname.lower() == 'done': break
            
        router_id = input(f"Enter Router ID (e.g., 1.1.1.1): ").strip()
        proc_id = input("Enter OSPF Process ID [1]: ").strip() or "1"
        use_if = input("Use interface-level config? (y/n) [n]: ").strip().lower() == 'y'
        
        router = OSPFRouter(hostname, router_id, int(proc_id), use_if)
        
        while True:
            if_name = input(f"  Interface Name (e.g., Gi0/0) or 'done': ").strip()
            if if_name.lower() == 'done': break
                
            ip = input(f"  IP Address (press enter if using if-level config): ").strip() or None
            mask = input(f"  Subnet Mask (press enter if using if-level config): ").strip() or None
            area = input(f"  Area [0]: ").strip() or "0"
            passive = input(f"  Passive? (y/n) [n]: ").strip().lower() == 'y'
            
            auth = input("  Auth (md5/clear/none) [none]: ").strip().lower()
            auth_type = 'message-digest' if auth == 'md5' else 'cleartext' if auth == 'clear' else None
            auth_key = input("  Auth Key: ").strip() if auth_type else None
            
            router.add_interface(if_name, ip, mask, int(area), passive, auth_type, auth_key)
            
        routers.append(router)
    return routers

def main():
    parser = argparse.ArgumentParser(description="Generate OSPF configurations for Cisco IOS/Packet Tracer.")
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
