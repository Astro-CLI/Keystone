import json
import argparse
import random
import sys
from format_parser import parse_file, detect_format, normalize_entries, entry_name

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def generate_vlan_config(hostname, vlans):
    lines = [f"! VLAN Configuration for {hostname}"]
    vlans = [v for v in normalize_entries(vlans, preferred_keys=('vlans',)) if isinstance(v, dict)]
    used_ids = set(v.get('id') for v in vlans if v.get('id'))
    next_id = 10
    svi_lines = []
    for v in vlans:
        v_id = v.get('id')
        if not v_id:
            while next_id in used_ids:
                next_id += 1
            v_id = next_id
            used_ids.add(v_id)
        lines.append(f"vlan {v_id}")
        lines.append(f" name {v.get('name', f'VLAN{v_id}')}")
    lines.append("exit")
    for v in vlans:
        v_id = v.get('id')
        if not v_id and 'id' not in v:
            continue
        if v.get('ip') or v.get('ipv6'):
            svi_lines.append(f"interface vlan {v_id}")
            if v.get('ip') and v.get('mask'):
                svi_lines.append(f" ip address {v['ip']} {v['mask']}")
            if v.get('ipv6'):
                svi_lines.append(f" ipv6 address {v['ipv6']}")
            svi_lines.append(" no shutdown")
            svi_lines.append(" exit")
    if svi_lines:
        lines.append("")
        lines.extend(svi_lines)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate VLAN Database configurations.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    args = parser.parse_args()
    if not args.file:
        print("Usage: python3 vlan_weaver.py --file [file.json/file.yaml/file.xml]")
        return
    try:
        data = normalize_entries(parse_file(args.file), preferred_keys=('items', 'devices'))
        for idx, entry in enumerate(data):
            if not isinstance(entry, dict):
                continue
            hostname = entry_name(entry, idx)
            print(f"\n! --- {hostname} ---")
            print(generate_vlan_config(hostname, entry.get('vlans', [])))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
