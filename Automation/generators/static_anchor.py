import json
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from format_parser import parse_file, normalize_entries, entry_name, normalize_interface_name, normalize_items

class StaticRoute:
    """Represents a single static route configuration (IPv4 or IPv6)."""
    def __init__(self, network, mask, next_hop=None, exit_interface=None, distance=1, description=None):
        self.network = network
        self.mask = mask
        self.next_hop = next_hop
        self.exit_interface = normalize_interface_name(exit_interface) if exit_interface else exit_interface
        self.distance = distance # Administrative Distance (Priority)
        self.description = description
        self.is_ipv6 = self._detect_ipv6()
    
    def _detect_ipv6(self):
        """Detect if this is an IPv6 route (contains colons)"""
        return ':' in str(self.network)

    def generate_command(self):
        """Generates the Cisco IOS 'ip route' or 'ipv6 route' command."""
        target = ""
        if self.next_hop and self.exit_interface:
            target = f"{self.exit_interface} {self.next_hop}"
        elif self.next_hop:
            target = self.next_hop
        elif self.exit_interface:
            target = self.exit_interface
        
        if self.is_ipv6:
            # IPv6 static routes use prefix notation.
            prefix = str(self.mask)
            network = self.network if "/" in str(self.network) else f"{self.network}/{prefix}"
            cmd = f"ipv6 route {network} {target}".rstrip()
        else:
            # IPv4 static routes keep the network + dotted-decimal mask form.
            cmd = f"ip route {self.network} {self.mask} {target}".rstrip()
        
        if self.distance != 1:
            cmd += f" {self.distance}"
        
        if self.description:
            return f"! {self.description}\n{cmd}"
        return cmd

class StaticRouteRouter:
    """Represents a router with a collection of static routes."""
    def __init__(self, hostname):
        self.hostname = hostname
        self.routes = []

    def add_route(self, network, mask, **kwargs):
        self.routes.append(StaticRoute(network, mask, **kwargs))

    def generate_cli_config(self):
        """Generates the full CLI config for the router's static routes."""
        lines = [f"! Static Routes for {self.hostname}"]
        for route in self.routes:
            lines.append(route.generate_command())
        return "\n".join(lines)

    def to_dict(self):
        """Returns a dictionary representation for JSON export."""
        return {
            "hostname": self.hostname,
            "routes": [
                {
                    "network": r.network,
                    "mask": r.mask,
                    "next_hop": r.next_hop,
                    "exit_interface": r.exit_interface,
                    "distance": r.distance,
                    "description": r.description
                } for r in self.routes
            ]
        }

def load_from_file(filepath):
    """Loads static route configurations from a JSON, YAML, or XML file."""
    try:
        data = normalize_entries(parse_file(filepath), preferred_keys=('items', 'devices'))
        
        routers = []
        for idx, r_data in enumerate(data):
            if not isinstance(r_data, dict):
                continue
            router = StaticRouteRouter(entry_name(r_data, idx))
            for route_data in normalize_items(r_data.get('routes', [])):
                if not isinstance(route_data, dict):
                    continue
                router.add_route(
                    route_data['network'],
                    route_data['mask'],
                    next_hop=route_data.get('next_hop'),
                    exit_interface=route_data.get('exit_interface'),
                    distance=route_data.get('distance', 1),
                    description=route_data.get('description')
                )
            routers.append(router)
        return routers
    except Exception as e:
        print(f"Error loading file: {e}")
        return []

def interactive_mode():
    """Runs the interactive CLI for static routes."""
    print("=== Static Route Configuration Generator (Interactive) ===")
    routers = []
    
    while True:
        hostname = input("\nEnter Router Hostname (or 'done'): ").strip()
        if hostname.lower() == 'done': break
            
        router = StaticRouteRouter(hostname)
        
        while True:
            net = input(f"  Destination Network (IPv4: 192.168.1.0 or IPv6: 2001:db8::) or 'done': ").strip()
            if net.lower() == 'done': break
            mask = input(f"  Subnet Mask (IPv4: 255.255.255.0 or IPv6 Prefix: 64): ").strip()
            
            print("  Define Next-Hop (provide at least one):")
            nh = input(f"    Next-Hop IP [none]: ").strip() or None
            exit_if = input(f"    Exit Interface (e.g., Gi0/0) [none]: ").strip() or None
            
            dist = input(f"    Admin Distance (Priority) [1]: ").strip()
            distance = int(dist) if dist else 1
            
            desc = input(f"    Description/Comment [none]: ").strip() or None
            
            router.add_route(net, mask, next_hop=nh, exit_interface=exit_if, 
                            distance=distance, description=desc)
            
        routers.append(router)
    return routers

def main():
    parser = argparse.ArgumentParser(description="Generate Static Route configurations for Cisco IOS/Packet Tracer (IPv4 & IPv6).")
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
