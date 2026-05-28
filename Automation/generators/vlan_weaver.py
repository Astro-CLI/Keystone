import json
import argparse
import random
import sys
from format_parser import parse_file, detect_format

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def generate_vlan_config(hostname, vlans):
    lines = [f"! VLAN Configuration for {hostname}"]

    # Track used IDs to avoid collisions
    used_ids = set(v.get('id') for v in vlans if v.get('id'))

    # Start assigning from 10 if not specified, or next available
    next_id = 10

    for v in vlans:
        v_id = v.get('id')
        if not v_id:
            while next_id in used_ids:
                next_id += 1
            v_id = next_id
            used_ids.add(v_id)

        lines.append(f"vlan {v_id}")
        lines.append(f" name {v['name']}")
    lines.append("exit")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate VLAN Database configurations.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    args = parser.parse_args()

    if not args.file:
        print("Usage: python3 vlan_weaver.py --file [file.json/file.yaml/file.xml]")
        return

    try:
        data = parse_file(args.file)
        if isinstance(data, dict):
            data = [data]

        for entry in data:
            print(f"\n! --- {entry['hostname']} ---")
            print(generate_vlan_config(entry['hostname'], entry['vlans']))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
