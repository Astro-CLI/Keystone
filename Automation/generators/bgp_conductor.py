import json
import argparse
import sys
from format_parser import parse_file, detect_format

class BGPNeighbor:
    """Represents a BGP neighbor configuration."""
    def __init__(self, ip, remote_as, description=None, update_source=None, 
                 next_hop_self=False, ebgp_multihop=None):
        self.ip = ip
        self.remote_as = remote_as
        self.description = description
        self.update_source = update_source # e.g., 'Loopback0'
        self.next_hop_self = next_hop_self
        self.ebgp_multihop = ebgp_multihop # int (2-255)

class BGPRouter:
    """Represents a router running BGP."""
    def __init__(self, hostname, as_number, router_id=None):
        self.hostname = hostname
        self.as_number = as_number
        self.router_id = router_id
        self.neighbors = []
        self.networks = [] # List of tuples (network, mask)

    def add_neighbor(self, ip, remote_as, **kwargs):
        self.neighbors.append(BGPNeighbor(ip, remote_as, **kwargs))

    def add_network(self, network, mask):
        self.networks.append((network, mask))

    def generate_cli_config(self):
        """Generates Cisco IOS CLI commands for BGP."""
        lines = [f"! BGP Configuration for {self.hostname}"]
        lines.append(f"router bgp {self.as_number}")
        
        if self.router_id:
            lines.append(f" bgp router-id {self.router_id}")
            
        lines.append(" bgp log-neighbor-changes")
        
        # Neighbors
        for n in self.neighbors:
            lines.append(f" neighbor {n.ip} remote-as {n.remote_as}")
            if n.description:
                lines.append(f" neighbor {n.ip} description {n.description}")
            if n.update_source:
                lines.append(f" neighbor {n.ip} update-source {n.update_source}")
            if n.next_hop_self:
                lines.append(f" neighbor {n.ip} next-hop-self")
            if n.ebgp_multihop:
                lines.append(f" neighbor {n.ip} ebgp-multihop {n.ebgp_multihop}")
        
        # Network statements
        for net, mask in self.networks:
            lines.append(f" network {net} mask {mask}")
            
        lines.append(" exit")
        return "\n".join(lines)

    def to_dict(self):
        """Returns a dictionary representation for JSON export."""
        return {
            "hostname": self.hostname,
            "as_number": self.as_number,
            "router_id": self.router_id,
            "neighbors": [
                {
                    "ip": n.ip,
                    "remote_as": n.remote_as,
                    "description": n.description,
                    "update_source": n.update_source,
                    "next_hop_self": n.next_hop_self,
                    "ebgp_multihop": n.ebgp_multihop
                } for n in self.neighbors
            ],
            "networks": [{"network": net, "mask": mask} for net, mask in self.networks]
        }

def load_from_file(filepath):
    """
    Loads BGP configurations from JSON, YAML, or XML file.
    
    Automatically detects format based on file extension (.json, .yaml, .yml, .xml)
    or by analyzing file content.
    
    Args:
        filepath (str): Path to inventory file in JSON, YAML, or XML format
        
    Returns:
        list: List of BGPRouter objects
    """
    try:
        data = parse_file(filepath)
        
        # Ensure data is a list
        if isinstance(data, dict):
            data = [data]
        
        routers = []
        for r_data in data:
            router = BGPRouter(r_data['hostname'], r_data['as_number'], r_data.get('router_id'))
            for n_data in r_data.get('neighbors', []):
                router.add_neighbor(
                    n_data['ip'], 
                    n_data['remote_as'],
                    description=n_data.get('description'),
                    update_source=n_data.get('update_source'),
                    next_hop_self=n_data.get('next_hop_self', False),
                    ebgp_multihop=n_data.get('ebgp_multihop')
                )
            for net_data in r_data.get('networks', []):
                router.add_network(net_data['network'], net_data['mask'])
            routers.append(router)
        return routers
    except Exception as e:
        print(f"Error loading file: {e}")
        return []

def interactive_mode():
    """Runs the interactive CLI for BGP."""
    print("=== BGP Configuration Generator (Interactive) ===")
    routers = []
    
    while True:
        hostname = input("\nEnter Router Hostname (or 'done'): ").strip()
        if hostname.lower() == 'done': break
            
        as_num = input("Enter Local AS Number: ").strip()
        router_id = input("Enter Router ID (optional): ").strip() or None
        
        router = BGPRouter(hostname, int(as_num), router_id)
        
        # Neighbors
        while True:
            n_ip = input(f"  Neighbor IP (or 'done'): ").strip()
            if n_ip.lower() == 'done': break
            n_as = input(f"  Neighbor Remote AS: ").strip()
            desc = input(f"  Neighbor Description (optional): ").strip() or None
            src = input(f"  Update Source (e.g., Loopback0) [none]: ").strip() or None
            nhs = input(f"  Next-Hop-Self? (y/n) [n]: ").strip().lower() == 'y'
            hop = input(f"  EBGP Multihop (2-255) [none]: ").strip()
            ebgp_hop = int(hop) if hop else None
            
            router.add_neighbor(n_ip, int(n_as), description=desc, update_source=src, 
                               next_hop_self=nhs, ebgp_multihop=ebgp_hop)
        
        # Networks
        while True:
            net = input(f"  Network to advertise (or 'done'): ").strip()
            if net.lower() == 'done': break
            mask = input(f"  Mask for {net}: ").strip()
            router.add_network(net, mask)
            
        routers.append(router)
    return routers

def main():
    parser = argparse.ArgumentParser(description="Generate BGP configurations for Cisco IOS/Packet Tracer.")
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
        print(f"\n--- {router.hostname} ---")
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
