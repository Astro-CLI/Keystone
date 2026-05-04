import json
import argparse

def generate_hsrp_config(hostname, interfaces):
    lines = [f"! HSRP & SVI Configuration for {hostname}"]
    for iface in interfaces:
        lines.append(f"interface vlan {iface['vlan_id']}")
        lines.append(f" ip address {iface['ip']} {iface['mask']}")
        lines.append(f" standby {iface['vlan_id']} ip {iface['hsrp_ip']}")
        lines.append(f" standby {iface['vlan_id']} priority {iface.get('priority', 100)}")
        lines.append(f" standby {iface['vlan_id']} preempt")
        lines.append(" no shutdown")
        lines.append(" exit")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate HSRP and SVI configurations.")
    parser.add_argument("--file", help="Path to JSON file")
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
        for entry in data:
            print(f"\n--- {entry['hostname']} ---")
            print(generate_hsrp_config(entry['hostname'], entry['interfaces']))

if __name__ == "__main__":
    main()
