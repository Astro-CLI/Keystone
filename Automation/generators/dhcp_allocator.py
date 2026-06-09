import json
import argparse
from format_parser import parse_file, detect_format, normalize_entries, entry_name, normalize_items


def generate_dhcp_config(hostname, pools, excluded, ipv6_pools=None):
    lines = [f"! DHCP Configuration for {hostname}"]
    excluded = normalize_items(excluded)
    pools = normalize_items(pools)
    ipv6_pools = normalize_items(ipv6_pools)
    if excluded:
        lines.append("! Excluded Addresses")
        for ex in excluded:
            if 'end' in ex:
                lines.append(f"ip dhcp excluded-address {ex['start']} {ex['end']}")
            else:
                lines.append(f"ip dhcp excluded-address {ex['start']}")
    for p in pools:
        if not isinstance(p, dict):
            continue
        lines.append(f"ip dhcp pool {p['name']}")
        lines.append(f" network {p['network']} {p['mask']}")
        lines.append(f" default-router {p['gateway']}")
        lines.append(f" dns-server {p.get('dns', '8.8.8.8')}")
        lines.append(" exit")
    if ipv6_pools:
        lines.append("! DHCPv6 Pools")
        for p in ipv6_pools:
            if not isinstance(p, dict):
                continue
            lines.append(f"ipv6 dhcp pool {p['name']}")
            lines.append(f" prefix-delegation pool {p['prefix']}")
            if p.get('dns'):
                lines.append(f" dns-server {p['dns']}")
            lines.append(" exit")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate DHCP Pool configurations.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    args = parser.parse_args()
    if args.file:
        data = normalize_entries(parse_file(args.file), preferred_keys=('items', 'devices'))
        for idx, entry in enumerate(data):
            if not isinstance(entry, dict):
                continue
            hostname = entry_name(entry, idx)
            print(f"\n! --- {hostname} ---")
            print(generate_dhcp_config(
                hostname,
                entry.get('pools', []),
                entry.get('excluded', []),
                entry.get('ipv6_pools')
            ))


if __name__ == "__main__":
    main()
