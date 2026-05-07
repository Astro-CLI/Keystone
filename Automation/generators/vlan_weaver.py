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
    used_ids = [v.get('id') for v in vlans if v.get('id')]
    
    for v in vlans:
        v_id = v.get('id')
        if not v_id:
            # Generate random unique ID between 2 and 1001
            while True:
                v_id = random.randint(2, 1001)
                if v_id not in used_ids:
                    used_ids.append(v_id)
                    break
        
        lines.append(f"vlan {v_id}")
        lines.append(f" name {v['name']}")
    lines.append("exit")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Generate VLAN Database configurations.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    args = parser.parse_args()

    if not args.file:
        print("Usage: python3 vlan_generator.py --file [file.json/file.yaml/file.xml]")
        return

    try:
        data = parse_file(args.file)
        if isinstance(data, dict):
            data = [data]

        for entry in data:
            print(f"\n--- {entry['hostname']} ---")
            print(generate_vlan_config(entry['hostname'], entry['vlans']))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
