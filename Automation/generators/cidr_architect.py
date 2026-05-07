import ipaddress
import math
import argparse
import sys

class SubnetPlanner:
    @staticmethod
    def find_best_fit(required_hosts):
        # We need 2^(32-prefix) - 2 >= required_hosts
        # So 2^(32-prefix) >= required_hosts + 2
        # 32 - prefix >= log2(required_hosts + 2)
        # prefix <= 32 - log2(required_hosts + 2)
        
        if required_hosts < 0:
            return None
        
        if required_hosts == 0:
            return 32 # Point-to-point or single host

        # Calculate needed bits for hosts
        needed_bits = math.ceil(math.log2(required_hosts + 2))
        prefix = 32 - needed_bits
        
        if prefix < 0:
            return None # Too many hosts for IPv4
            
        return prefix

    @staticmethod
    def get_wildcard(netmask):
        parts = [int(p) for p in netmask.split('.')]
        wildcard_parts = [255 - p for p in parts]
        return ".".join(map(str, wildcard_parts))

    @staticmethod
    def calculate_details(base_ip, prefix):
        try:
            net = ipaddress.IPv4Network(f"{base_ip}/{prefix}", strict=False)
            return {
                "cidr": str(net),
                "prefix": net.prefixlen,
                "netmask": str(net.netmask),
                "wildcard": SubnetPlanner.get_wildcard(str(net.netmask)),
                "network_address": str(net.network_address),
                "broadcast_address": str(net.broadcast_address),
                "first_usable": str(net.network_address + 1) if net.num_addresses > 2 else "N/A",
                "last_usable": str(net.broadcast_address - 1) if net.num_addresses > 2 else "N/A",
                "total_hosts": max(0, net.num_addresses - 2) if net.prefixlen < 31 else (2 if net.prefixlen == 31 else 1)
            }
        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Subnet/CIDR Planner for Network Design.")
    parser.add_argument("--hosts", type=int, help="Number of required host machines")
    parser.add_argument("--base", default="192.168.1.0", help="Base IP address for calculation")
    parser.add_argument("--format", choices=['list', 'yaml'], default='list', help="Output format")
    
    args = parser.parse_args()

    if args.hosts is None:
        print("Usage: python3 subnet_calc.py --hosts [number]")
        return

    prefix = SubnetPlanner.find_best_fit(args.hosts)
    if prefix is None:
        print(f"Error: Could not find a valid subnet for {args.hosts} hosts.")
        return

    details = SubnetPlanner.calculate_details(args.base, prefix)

    if args.format == 'yaml':
        import yaml
        print(yaml.dump(details, sort_keys=False))
    else:
        print(f"=== Subnet Plan for {args.hosts} Hosts ===")
        print(f"Recommended Prefix: /{details['prefix']}")
        print(f"Network Address:    {details['network_address']}")
        print(f"Subnet Mask:        {details['netmask']}")
        print(f"Wildcard Mask:      {details['wildcard']}")
        print(f"Broadcast Address:  {details['broadcast_address']}")
        print(f"Usable Range:       {details['first_usable']} - {details['last_usable']}")
        print(f"Total Usable Hosts: {details['total_hosts']}")

if __name__ == "__main__":
    main()
