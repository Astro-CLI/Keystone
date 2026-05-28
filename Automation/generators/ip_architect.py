import ipaddress
import random
import argparse
import sys

class IPGenerator:
    # RFC 1918 Private Ranges (IPv4)
    PRIVATE_RANGES_V4 = {
        'A': '10.0.0.0/8',
        'B': '172.16.0.0/12',
        'C': '192.168.0.0/16'
    }

    # Common Public Ranges for Simulations (IPv4)
    PUBLIC_RANGES_V4 = {
        'A': '1.0.0.0/8',
        'B': '128.0.0.0/16',
        'C': '192.0.2.0/24'
    }

    # RFC 4193 ULA Ranges (IPv6)
    PRIVATE_RANGES_V6 = {
        'A': 'fc00:0000:0000:0000::/32',  # ULA /32 (large organization)
        'B': 'fc00:0000:0100:0000::/40',  # ULA /40 (medium organization)
        'C': 'fc00:0000:0200:0000::/48'   # ULA /48 (small organization/site)
    }

    # Documentation ranges (IPv6)
    PUBLIC_RANGES_V6 = {
        'A': '2001:db8:0000:0000::/32',
        'B': '2001:db8:0100:0000::/40',
        'C': '2001:db8:0200:0000::/48'
    }

    @staticmethod
    def is_ipv6(ip_str):
        """Check if IP string is IPv6 (contains colons)"""
        return ':' in ip_str

    @staticmethod
    def generate_ips(count, addr_class, addr_type, sequential=False, is_ipv6=False):
        if is_ipv6:
            base_net_str = IPGenerator.PRIVATE_RANGES_V6[addr_class] if addr_type == 'private' else IPGenerator.PUBLIC_RANGES_V6[addr_class]
            net = ipaddress.IPv6Network(base_net_str)
        else:
            base_net_str = IPGenerator.PRIVATE_RANGES_V4[addr_class] if addr_type == 'private' else IPGenerator.PUBLIC_RANGES_V4[addr_class]
            net = ipaddress.IPv4Network(base_net_str)
        
        results = []
        
        if sequential:
            hosts = net.hosts()
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
            
            seen = set()
            while len(seen) < count:
                ip_int = random.randint(int(net.network_address) + 1, int(net.broadcast_address) - 1)
                if is_ipv6:
                    seen.add(str(ipaddress.IPv6Address(ip_int)))
                else:
                    seen.add(str(ipaddress.IPv4Address(ip_int)))
            results = list(seen)
            
        return results

    @staticmethod
    def generate_ips_from_subnet(network_str, prefix_str, count):
        """Generate random IPs from a specific subnet (works for both IPv4 and IPv6)"""
        try:
            is_ipv6 = IPGenerator.is_ipv6(network_str)
            
            if is_ipv6:
                net = ipaddress.IPv6Network(f"{network_str}/{prefix_str}", strict=False)
                num_available = int(net.num_addresses) - 2 if int(net.num_addresses) > 2 else int(net.num_addresses)
                
                if count > num_available:
                    count = num_available
                
                seen = set()
                while len(seen) < count:
                    ip_int = random.randint(int(net.network_address) + 1, int(net.broadcast_address) - 1)
                    seen.add(str(ipaddress.IPv6Address(ip_int)))
                return list(seen)
            else:
                net = ipaddress.IPv4Network(f"{network_str}/{prefix_str}", strict=False)
                num_available = len(list(net.hosts()))
                
                if count > num_available:
                    count = num_available
                
                seen = set()
                while len(seen) < count:
                    ip_int = random.randint(int(net.network_address) + 1, int(net.broadcast_address) - 1)
                    seen.add(str(ipaddress.IPv4Address(ip_int)))
                return list(seen)
        except Exception as e:
            return []

    @staticmethod
    def generate_subnets(count, parent_net_str, new_prefix):
        """Generate subnets from parent network (works for both IPv4 and IPv6)"""
        try:
            is_ipv6 = IPGenerator.is_ipv6(parent_net_str)
            if is_ipv6:
                parent = ipaddress.IPv6Network(parent_net_str)
            else:
                parent = ipaddress.IPv4Network(parent_net_str)
            
            subnets = list(parent.subnets(new_prefix=new_prefix))
            
            if count > len(subnets):
                count = len(subnets)
                
            return [str(s) for s in subnets[:count]]
        except Exception as e:
            return []

def main():
    parser = argparse.ArgumentParser(description="Hybrid IPv4 IP Generator: Generate from subnets or standalone random IPs.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    parser.add_argument("--mode", choices=['ip', 'subnet', 'from_interfaces', 'random'], default='ip', help="Generation mode")
    parser.add_argument("--count", type=int, default=5, help="Number of IPs to generate")
    parser.add_argument("--class", dest="addr_class", choices=['A', 'B', 'C'], default='C', help="IP Class (for random mode)")
    parser.add_argument("--type", choices=['public', 'private'], default='private', help="IP Type (for random mode)")
    parser.add_argument("--parent", help="Parent network for Subnet mode (e.g., 10.0.0.0/8)")
    parser.add_argument("--prefix", type=int, help="New prefix for Subnet mode (e.g., 24)")
    parser.add_argument("--sequential", action="store_true", help="Generate sequential items instead of random")
    parser.add_argument("--format", choices=['list', 'yaml'], default='list', help="Output format")

    args = parser.parse_args()

    if args.file:
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
            from format_parser import parse_file
            data = parse_file(args.file)
            
            # Keep as list to support multiple devices/entries
            if not isinstance(data, list):
                data = [data]
            
            # Process all items in the list
            for item_index, data_item in enumerate(data):
                # Set default values
                count = 5
                addr_class = 'C'
                addr_type = 'private'
                parent = None
                prefix = None
                sequential = False
                out_format = 'list'
                
                # Detect mode: if "interfaces" exist, use from_interfaces; else if random_ips, use random
                if 'interfaces' in data_item:
                    mode = 'from_interfaces'
                    hostname = data_item.get('hostname', 'Unknown')
                    interfaces = data_item.get('interfaces', [])
                    
                    # Process this device's interfaces
                    print(f"--- Generating Random IPs from {hostname} Interfaces ---\n")
                    
                    for iface in interfaces:
                        name = iface.get('name', 'Unknown')
                        ip = iface.get('ip')
                        mask = iface.get('mask')
                        
                        if ip and mask:
                            is_ipv6 = IPGenerator.is_ipv6(ip)
                            ip_version = "IPv6" if is_ipv6 else "IPv4"
                            
                            # Calculate number of usable hosts in this subnet
                            if is_ipv6:
                                net = ipaddress.IPv6Network(f"{ip}/{mask}", strict=False)
                                num_hosts = int(net.num_addresses) - 2 if int(net.num_addresses) > 2 else int(net.num_addresses)
                            else:
                                net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
                                num_hosts = len(list(net.hosts()))
                            
                            # Generate random IPs for this subnet
                            count_for_subnet = min(count, max(1, num_hosts // 4))  # Use ~25% of subnet
                            random_ips = IPGenerator.generate_ips_from_subnet(ip, mask, count_for_subnet)
                            
                            print(f"Interface: {name}")
                            print(f"  Network: {ip}/{mask} ({ip_version})")
                            print(f"  Generated IPs:")
                            for i, generated_ip in enumerate(random_ips, 1):
                                print(f"    {i}. {generated_ip}")
                            print()
                
                elif 'random_ips' in data_item:
                    mode = 'random'
                    random_config = data_item.get('random_ips', {})
                    count = random_config.get('count', 5)
                    classes = random_config.get('classes', ['C'])
                    is_ipv6 = random_config.get('ipv6', False)
                    ip_version = "IPv6" if is_ipv6 else "IPv4"
                    
                    print(f"--- Generating Random {ip_version} Private IPs ---\n")
                    
                    for ip_class in classes:
                        count_per_class = count // len(classes) if len(classes) > 1 else count
                        ips = IPGenerator.generate_ips(count_per_class, ip_class, 'private', sequential=False, is_ipv6=is_ipv6)
                        
                        if is_ipv6:
                            range_str = IPGenerator.PRIVATE_RANGES_V6[ip_class]
                        else:
                            range_str = IPGenerator.PRIVATE_RANGES_V4[ip_class]
                        
                        print(f"Class {ip_class} ({range_str}, {ip_version}):")
                        for i, ip in enumerate(ips, 1):
                            print(f"  {i}. {ip}")
                        print()
                
        except Exception as e:
            print(f"Error reading file: {e}")
            import traceback
            traceback.print_exc()
            return
    else:
        mode = args.mode
        count = args.count
        addr_class = args.addr_class
        addr_type = args.type
        parent = args.parent
        prefix = args.prefix
        sequential = args.sequential
        out_format = args.format
        
        # --- Legacy mode processing (non-file) ---
        if mode == 'from_interfaces':
            print(f"--- Generating Random IPs from Interfaces ---\n")
        elif mode == 'subnet':
            if not parent or not prefix:
                print("Error: --parent and --prefix are required for subnet mode (or specify in --file).")
                return
            print(f"--- Generating {count} subnets of /{prefix} from {parent} ---")
            all_ips = IPGenerator.generate_subnets(count, parent, prefix)
            
            if out_format == 'yaml':
                print("items:")
                for item in all_ips:
                    print(f"  - {item}")
            else:
                for i, item in enumerate(all_ips, 1):
                    print(f"{i}. {item}")
            return
        else:  # mode == 'ip'
            print(f"--- Generating {count} {args.addr_class} {args.type.capitalize()} IPs ---")
            all_ips = IPGenerator.generate_ips(count, args.addr_class, args.type, sequential)
            
            for i, ip in enumerate(all_ips, 1):
                print(f"{i}. {ip}")
            return

if __name__ == "__main__":
    main()
