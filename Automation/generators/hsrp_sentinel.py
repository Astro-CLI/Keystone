import json
import argparse
from format_parser import parse_file, detect_format, normalize_entries, entry_name, normalize_items

def generate_hsrp_config(hostname, interfaces):
    lines = [f"! HSRP & SVI Configuration for {hostname}"]
    for iface in normalize_items(interfaces):
        if not isinstance(iface, dict):
            continue
        lines.append(f"interface vlan {iface['vlan_id']}")
        
        # IPv4 HSRP
        if 'ip' in iface and 'hsrp_ip' in iface:
            lines.append(f" ip address {iface['ip']} {iface['mask']}")
            lines.append(f" standby {iface['vlan_id']} ip {iface['hsrp_ip']}")
            lines.append(f" standby {iface['vlan_id']} priority {iface.get('priority', 100)}")
            lines.append(f" standby {iface['vlan_id']} preempt")
            
        # IPv6 HSRP
        if 'ipv6' in iface and 'hsrp_ipv6' in iface:
            lines.append(f" ipv6 address {iface['ipv6']}/{iface.get('ipv6_mask', 64)}")
            lines.append(f" standby {iface['vlan_id']} ipv6 {iface['hsrp_ipv6']}")
            lines.append(f" standby {iface['vlan_id']} priority {iface.get('priority', 100)}")
            lines.append(f" standby {iface['vlan_id']} preempt")
            
        lines.append(" no shutdown")
        lines.append(" exit")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate HSRP and SVI configurations.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    args = parser.parse_args()

    if args.file:
        data = normalize_entries(parse_file(args.file), preferred_keys=('items', 'devices'))
        for idx, entry in enumerate(data):
            if not isinstance(entry, dict):
                continue
            hostname = entry_name(entry, idx)
            print(f"\n! --- {hostname} ---")
            print(generate_hsrp_config(hostname, entry.get('interfaces', [])))

if __name__ == "__main__":
    main()
