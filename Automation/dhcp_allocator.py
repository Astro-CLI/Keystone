import json
import argparse

def generate_dhcp_config(hostname, pools, excluded):
    lines = [f"! DHCP Configuration for {hostname}"]
    
    if excluded:
        lines.append("! Excluded Addresses")
        for ex in excluded:
            if 'end' in ex:
                lines.append(f"ip dhcp excluded-address {ex['start']} {ex['end']}")
            else:
                lines.append(f"ip dhcp excluded-address {ex['start']}")
                
    for p in pools:
        lines.append(f"ip dhcp pool {p['name']}")
        lines.append(f" network {p['network']} {p['mask']}")
        lines.append(f" default-router {p['gateway']}")
        lines.append(f" dns-server {p.get('dns', '8.8.8.8')}")
        lines.append(" exit")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate DHCP Pool configurations.")
    parser.add_argument("--file", help="Path to JSON file")
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
        for entry in data:
            print(f"\n--- {entry['hostname']} ---")
            print(generate_dhcp_config(entry['hostname'], entry.get('pools', []), entry.get('excluded', [])))

if __name__ == "__main__":
    main()
