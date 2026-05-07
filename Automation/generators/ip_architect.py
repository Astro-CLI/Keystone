import ipaddress
import random
import argparse
import sys

class IPGenerator:
    # RFC 1918 Private Ranges
    PRIVATE_RANGES = {
        'A': '10.0.0.0/8',
        'B': '172.16.0.0/12',
        'C': '192.168.0.0/16'
    }

    # Common Public Ranges for Simulations
    PUBLIC_RANGES = {
        'A': '1.0.0.0/8',
        'B': '128.0.0.0/16',
        'C': '192.0.2.0/24'
    }

    @staticmethod
    def generate_ips(count, addr_class, addr_type, sequential=False):
        base_net_str = IPGenerator.PRIVATE_RANGES[addr_class] if addr_type == 'private' else IPGenerator.PUBLIC_RANGES[addr_class]
        net = ipaddress.IPv4Network(base_net_str)
        
        # Generator for hosts
        hosts = net.hosts()
        results = []
        
        if sequential:
            for _ in range(count):
                try:
                    results.append(str(next(hosts)))
                except StopIteration:
                    break
        else:
            # Pick random unique hosts
            num_available = int(net.num_addresses) - 2
            if count > num_available:
                count = num_available
            
            # For large networks, we don't want to list all IPs then shuffle (memory heavy)
            # So we use a set to track uniqueness
            seen = set()
            while len(seen) < count:
                ip_int = random.randint(int(net.network_address) + 1, int(net.broadcast_address) - 1)
                seen.add(str(ipaddress.IPv4Address(ip_int)))
            results = list(seen)
            
        return results

    @staticmethod
    def generate_subnets(count, parent_net_str, new_prefix):
        parent = ipaddress.IPv4Network(parent_net_str)
        subnets = list(parent.subnets(new_prefix=new_prefix))
        
        if count > len(subnets):
            count = len(subnets)
            
        return [str(s) for s in subnets[:count]]

def main():
    parser = argparse.ArgumentParser(description="Sophisticated IPv4 Address and Subnet Generator.")
    parser.add_argument("--mode", choices=['ip', 'subnet'], default='ip', help="Generate individual IPs or Subnets")
    parser.add_argument("--count", type=int, default=5, help="Number of items to generate")
    parser.add_argument("--class", dest="addr_class", choices=['A', 'B', 'C'], default='C', help="IP Class (for IP mode)")
    parser.add_argument("--type", choices=['public', 'private'], default='private', help="IP Type (for IP mode)")
    parser.add_argument("--parent", help="Parent network for Subnet mode (e.g., 10.0.0.0/8)")
    parser.add_argument("--prefix", type=int, help="New prefix for Subnet mode (e.g., 24)")
    parser.add_argument("--sequential", action="store_true", help="Generate sequential items instead of random")
    parser.add_argument("--format", choices=['list', 'yaml'], default='list', help="Output format")

    args = parser.parse_args()

    if args.mode == 'ip':
        print(f"--- Generating {args.count} {args.addr_class} {args.type.capitalize()} IPs ---")
        items = IPGenerator.generate_ips(args.count, args.addr_class, args.type, args.sequential)
    else:
        if not args.parent or not args.prefix:
            print("Error: --parent and --prefix are required for subnet mode.")
            return
        print(f"--- Generating {args.count} subnets of /{args.prefix} from {args.parent} ---")
        items = IPGenerator.generate_subnets(args.count, args.parent, args.prefix)

    if args.format == 'yaml':
        print("items:")
        for item in items:
            print(f"  - {item}")
    else:
        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")

if __name__ == "__main__":
    main()
