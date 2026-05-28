import ipaddress
import math
import argparse
import sys

class SubnetPlanner:
    @staticmethod
    def is_ipv6(network_str):
        """Check if network is IPv6"""
        return ':' in network_str
    
    @staticmethod
    def find_best_fit(required_hosts, is_ipv6=False):
        """Find best fitting prefix for requested hosts"""
        if required_hosts < 0:
            return None
        
        if is_ipv6:
            # For IPv6, default to /64 per subnet (standard practice)
            # Each /64 can theoretically hold 2^64 addresses
            # The "size" parameter for IPv6 represents number of /64 subnets needed
            if required_hosts == 0:
                return 128
            if required_hosts == 1:
                return 64
            # For multiple subnets, calculate prefix based on count
            needed_bits = math.ceil(math.log2(required_hosts))
            prefix = 64 - needed_bits
            return max(prefix, 48)  # Don't go smaller than /48 for practical reasons
        else:
            # IPv4 logic (original)
            if required_hosts == 0:
                return 32
            needed_bits = math.ceil(math.log2(required_hosts + 2))
            prefix = 32 - needed_bits
            if prefix < 0:
                return None
            return prefix
    
    @staticmethod
    def get_wildcard(netmask):
        """Calculate wildcard mask (IPv4 only)"""
        parts = [int(p) for p in netmask.split('.')]
        wildcard_parts = [255 - p for p in parts]
        return ".".join(map(str, wildcard_parts))

    @staticmethod
    def calculate_details(base_ip, prefix, is_ipv6=False):
        """Calculate subnet details for IPv4 or IPv6"""
        try:
            if is_ipv6:
                net = ipaddress.IPv6Network(f"{base_ip}/{prefix}", strict=False)
                return {
                    "cidr": str(net),
                    "prefix": net.prefixlen,
                    "netmask": f"/{net.prefixlen}",
                    "wildcard": "N/A (IPv6)",
                    "network_address": str(net.network_address),
                    "broadcast_address": str(net.broadcast_address),
                    "first_usable": str(net.network_address + 1),
                    "last_usable": str(net.broadcast_address - 1),
                    "total_hosts": net.num_addresses,
                    "is_ipv6": True
                }
            else:
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
                    "total_hosts": max(0, net.num_addresses - 2) if net.prefixlen < 31 else (2 if net.prefixlen == 31 else 1),
                    "is_ipv6": False
                }
        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Subnet/CIDR Planner for Network Design.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    parser.add_argument("--hosts", type=int, help="Number of required host machines")
    parser.add_argument("--base", default="192.168.1.0", help="Base IP address for calculation")
    parser.add_argument("--format", choices=['list', 'yaml'], default='list', help="Output format")
    
    args = parser.parse_args()

    if args.file:
        try:
            from format_parser import parse_file
            data = parse_file(args.file)
            
            # Handle list of networks (multiple network entries)
            networks_to_process = []
            if isinstance(data, list):
                networks_to_process = data
            else:
                networks_to_process = [data]
            
            # Process each network
            for network_config in networks_to_process:
                # Handle new CIDR Architect format with network and subnets
                if 'network' in network_config and 'subnets' in network_config:
                    network = network_config['network']
                    subnets = network_config['subnets']
                    
                    # Detect if IPv6 or IPv4
                    is_ipv6 = SubnetPlanner.is_ipv6(network)
                    
                    # Parse base network to get the IP
                    if is_ipv6:
                        base_net = ipaddress.IPv6Network(network, strict=False)
                        capacity_text = f"{base_net.num_addresses} addresses"
                    else:
                        base_net = ipaddress.IPv4Network(network, strict=False)
                        capacity_text = f"{base_net.num_addresses - 2} usable hosts"
                    
                    base = str(base_net.network_address)
                    
                    # Generate subnet plan for each subnet
                    version = "IPv6" if is_ipv6 else "IPv4"
                    print(f"\n=== CIDR Subnet Allocation Plan ({version}) ===\n")
                    print(f"Base Network: {network}")
                    if is_ipv6:
                        print(f"Total Capacity: 2^{128 - base_net.prefixlen} addresses (essentially unlimited)")
                    else:
                        print(f"Total Capacity: {base_net.num_addresses - 2} usable hosts")
                        print(f"Netmask: {base_net.netmask}")
                    print()
                    print("=" * 70 + "\n")
                    
                    # For IPv6, we use /64 per subnet (standard)
                    # For IPv4, we calculate based on size
                    if is_ipv6:
                        current_prefix = base_net.prefixlen + 1
                    
                    current_ip = base_net.network_address
                    total_allocated = 0
                    
                    for idx, subnet in enumerate(subnets, 1):
                        subnet_name = subnet['name']
                        subnet_size = subnet['size']
                        
                        if is_ipv6:
                            # For IPv6, allocate sequential /64 subnets
                            # Calculate the subnet offset: idx-1 shifted left by 64 bits
                            subnet_offset = idx - 1
                            # Manually create the /64 subnet by calculating the address
                            base_int = int(base_net.network_address)
                            subnet_start_int = base_int + (subnet_offset * (2 ** 64))
                            subnet_start_addr = ipaddress.IPv6Address(subnet_start_int)
                            subnet_net = ipaddress.IPv6Network(f"{subnet_start_addr}/64", strict=False)
                            
                            details = SubnetPlanner.calculate_details(str(subnet_net.network_address), 64, is_ipv6=True)
                        else:
                            prefix = SubnetPlanner.find_best_fit(subnet_size, is_ipv6)
                            if prefix is None:
                                print(f"ERROR: Could not find a valid subnet for {subnet_name} ({subnet_size})\n")
                                continue
                            
                            # Create subnet at current IP
                            subnet_net = ipaddress.IPv4Network(f"{current_ip}/{prefix}", strict=False)
                            details = SubnetPlanner.calculate_details(str(subnet_net.network_address), prefix, is_ipv6=False)
                        
                        total_allocated += 1  # Count subnets, not hosts
                        
                        print(f"[{idx}] {subnet_name}")
                        print(f"    Requested: {subnet_size}")
                        print(f"    CIDR: {details['cidr']} (/{details['prefix']})")
                        if not is_ipv6:
                            print(f"    Netmask: {details['netmask']}")
                        print(f"    Network Address: {details['network_address']}")
                        if not is_ipv6:
                            print(f"    Broadcast Address: {details['broadcast_address']}")
                        
                        if details['first_usable'] != "N/A":
                            if is_ipv6:
                                print(f"    Usable Range: {details['first_usable']} - {details['last_usable']}")
                                print(f"    Gateway: {details['first_usable']}")
                                print(f"    Prefix (IPv6): /{details['prefix']}")
                            else:
                                first_ip = ipaddress.IPv4Address(details['first_usable'])
                                last_ip = ipaddress.IPv4Address(details['last_usable'])
                                dhcp_end = str(last_ip - 1)
                                
                                print(f"    Usable Range: {details['first_usable']} - {details['last_usable']}")
                                print(f"    Gateway: {details['first_usable']}")
                                print(f"    DHCP Pool: {str(first_ip + 1)} - {dhcp_end}")
                        
                        print(f"    Total Addresses: {details['total_hosts']}\n")
                        
                        # Move to next subnet (only for IPv4)
                        if not is_ipv6:
                            current_ip = subnet_net.broadcast_address + 1
                    
                    print("=" * 70)
                    if is_ipv6:
                        print(f"Summary: {len(subnets)} /64 subnets allocated\n")
                    else:
                        print(f"Summary: {len(subnets)} subnets | {total_allocated} total hosts")
                        print(f"Utilization: {(total_allocated / (base_net.num_addresses - 2)) * 100:.1f}%\n")
            
            # Check if any network was processed
            network_processed = any('network' in nc and 'subnets' in nc for nc in networks_to_process)
            if network_processed:
                return
            
            # Handle legacy format with hosts field
            hosts = networks_to_process[0].get('hosts') if networks_to_process else None
            base = networks_to_process[0].get('base', '192.168.1.0') if networks_to_process else '192.168.1.0'
            out_format = networks_to_process[0].get('format', 'list') if networks_to_process else 'list'
        except Exception as e:
            print(f"Error: {e}")
            return
    else:
        hosts = args.hosts
        base = args.base
        out_format = args.format

    if hosts is None:
        print("Usage: python3 cidr_architect.py --hosts [number] OR --file [config.yaml]")
        return

    prefix = SubnetPlanner.find_best_fit(hosts)
    if prefix is None:
        print(f"Error: Could not find a valid subnet for {hosts} hosts.")
        return

    details = SubnetPlanner.calculate_details(base, prefix)

    if out_format == 'yaml':
        import yaml
        print(yaml.dump(details, sort_keys=False))
    else:
        print(f"=== Subnet Plan for {hosts} Hosts ===")
        print(f"Recommended Prefix: /{details['prefix']}")
        print(f"Network Address:    {details['network_address']}")
        print(f"Subnet Mask:        {details['netmask']}")
        print(f"Wildcard Mask:      {details['wildcard']}")
        print(f"Broadcast Address:  {details['broadcast_address']}")
        print(f"Usable Range:       {details['first_usable']} - {details['last_usable']}")
        print(f"Total Usable Hosts: {details['total_hosts']}")

if __name__ == "__main__":
    main()
