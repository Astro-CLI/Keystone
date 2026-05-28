"""
pt_analyzer_helper.py
Parses multi-device output from pt_analyzer.js into structured YAML.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from pt_config_parser import CiscoConfigParser

DEVICE_MODEL_MAP = {
    "2911": "router",
    "2960": "switch",
    "5506-X": "firewall",
    "PC-PT": "pc",
    "Laptop-PT": "laptop",
    "Server-PT": "server",
}


def _model_to_type(model):
    for key, val in DEVICE_MODEL_MAP.items():
        if key in model:
            return val
    return "router"


def split_analyzer_output(text):
    """Split multi-device analyzer output into per-device blocks.

    pt_analyzer.js format per device:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        DEVICE: name
        MODEL: model
        SIZE: N bytes
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        Building configuration...
        ... (config)
        end

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        DEVICE: next-device
        ...

    Returns list of dicts: {device, model, config_text}
    """
    SEP_RE = re.compile(r"^[━═]{10,}")
    DEVICE_RE = re.compile(r"^DEVICE:\s*(.+)")
    MODEL_RE = re.compile(r"^MODEL:\s*(.+)")

    blocks = []
    current = None
    phase = None  # None | HEADER | CONFIG
    config_lines = []
    saw_any_sep = False

    for line in text.splitlines():
        is_sep = bool(SEP_RE.match(line))

        if is_sep:
            saw_any_sep = True
            if phase == "CONFIG" and current and config_lines:
                current["config_text"] = "\n".join(config_lines).strip()
                blocks.append(current)
                current = None
                config_lines = []
                phase = "HEADER"
            elif phase == "HEADER" and current:
                config_lines = []
                phase = "CONFIG"
            else:
                phase = "HEADER"
            continue

        dm = DEVICE_RE.match(line)
        mm = MODEL_RE.match(line)

        if phase == "HEADER":
            if dm:
                current = {"device": dm.group(1).strip(), "model": "", "config_text": ""}
            elif mm and current:
                current["model"] = mm.group(1).strip()
            # skip SIZE, blank, etc.
            continue

        if phase == "CONFIG" and current:
            config_lines.append(line)

    # Handle last device if no trailing separator
    if phase == "CONFIG" and current and config_lines:
        current["config_text"] = "\n".join(config_lines).strip()
        blocks.append(current)

    return blocks


def parse_analyzer_output(text):
    """Parse full pt_analyzer.js output into YAML topology string."""
    blocks = split_analyzer_output(text)
    if not blocks:
        return "# No device configurations found in the analyzer output."

    devices_yaml = []
    for blk in blocks:
        device_name = blk["device"]
        model = blk["model"]
        config_text = blk["config_text"]
        device_type = _model_to_type(model)

        parser = CiscoConfigParser()
        parser.parse_running_config(config_text)

        yaml_lines = [
            f"  - hostname: {device_name}",
            f"    type: {device_type}",
        ]

        if parser.interfaces:
            yaml_lines.append("    interfaces:")
            for iface_name, iface_config in parser.interfaces.items():
                yaml_lines.append(f"      - name: {iface_name}")
                if "ip" in iface_config:
                    yaml_lines.append(f"        ip: {iface_config['ip']}")
                    yaml_lines.append(f"        mask: {iface_config['mask']}")
                if "description" in iface_config:
                    yaml_lines.append(
                        f'        description: "{iface_config["description"]}"'
                    )

        if parser.routing_protocols.get("ospf"):
            ospf = parser.routing_protocols["ospf"]
            yaml_lines.append("    ospf:")
            if "process_id" in ospf:
                yaml_lines.append(f"      process_id: {ospf['process_id']}")
            if "router_id" in ospf:
                yaml_lines.append(f"      router_id: {ospf['router_id']}")
            if ospf.get("networks"):
                yaml_lines.append("      networks:")
                for net in ospf["networks"]:
                    yaml_lines.append(f"        - network: {net['network']}")
                    yaml_lines.append(f"          wildcard: {net['wildcard']}")
                    yaml_lines.append(f"          area: {net['area']}")

        if parser.routing_protocols.get("bgp"):
            bgp = parser.routing_protocols["bgp"]
            yaml_lines.append("    bgp:")
            if "asn" in bgp:
                yaml_lines.append(f"      asn: {bgp['asn']}")
            if bgp.get("neighbors"):
                yaml_lines.append("      neighbors:")
                for nb in bgp["neighbors"]:
                    yaml_lines.append(f"        - ip: {nb['ip']}")
                    yaml_lines.append(f"          asn: {nb['asn']}")

        if parser.services.get("dhcp"):
            yaml_lines.append("    dhcp:")
            yaml_lines.append("      pools:")
            for pool_name, pool_config in parser.services["dhcp"].items():
                yaml_lines.append(f"        - name: {pool_name}")
                if "network" in pool_config:
                    yaml_lines.append(f"          network: {pool_config['network']}")
                    yaml_lines.append(f"          mask: {pool_config['mask']}")
                if "gateway" in pool_config:
                    yaml_lines.append(
                        f"          gateway: {pool_config['gateway']}"
                    )

        if parser.services.get("ssh"):
            yaml_lines.append("    ssh:")
            yaml_lines.append("      enabled: true")

        devices_yaml.append("\n".join(yaml_lines))

    header = "# Topology parsed from Packet Tracer analyzer output\n"
    header += "# Generated by Keystone pt_analyzer_helper\n"
    header += f"# Devices: {len(blocks)}\n"
    header += "devices:\n"
    return header + "\n".join(devices_yaml)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pt_analyzer_helper.py <analyzer_output.txt>")
        print()
        print("Paste the full output from pt_analyzer.js into a text file,")
        print("then run this script to parse it into structured YAML.")
        sys.exit(1)

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path) as f:
        text = f.read()

    yaml_out = parse_analyzer_output(text)
    out_path = Path(path).stem + "_parsed.yaml"
    with open(out_path, "w") as f:
        f.write(yaml_out)
    print(yaml_out)
    print(f"\n# Saved to: {out_path}")


if __name__ == "__main__":
    main()
