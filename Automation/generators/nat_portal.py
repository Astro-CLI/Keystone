import json
import argparse
from format_parser import parse_file, detect_format, normalize_entries, entry_name, normalize_interface_name, normalize_items


class IOSNATRule:
    def __init__(self, rule_type, local_ip=None, global_ip=None, local_port=None, global_port=None,
                 acl_id=None, pool=None, interface=None, protocol='tcp', description=None, is_ipv6=False):
        self.rule_type = rule_type
        self.local_ip = local_ip
        self.global_ip = global_ip
        self.local_port = local_port
        self.global_port = global_port
        self.acl_id = acl_id
        self.pool = pool
        self.interface = interface
        self.protocol = protocol
        self.description = description
        self.is_ipv6 = is_ipv6 or (local_ip and ':' in str(local_ip))

    def generate_command(self):
        cmd = ""
        prefix = "ipv6 nat" if self.is_ipv6 else "ip nat"
        if self.rule_type == 'static':
            cmd = f"{prefix} inside source static {self.local_ip} {self.global_ip}"
        elif self.rule_type == 'port-forward':
            cmd = f"{prefix} inside source static {self.protocol} {self.local_ip} {self.local_port} {self.global_ip} {self.global_port} extendable"
        elif self.rule_type == 'dynamic':
            cmd = f"{prefix} inside source list {self.acl_id} pool {self.pool}"
        elif self.rule_type == 'overload':
            target = f"interface {self.interface}" if self.interface else f"pool {self.pool}"
            cmd = f"{prefix} inside source list {self.acl_id} {target} overload"
        if self.description:
            return f"! {self.description}\n{cmd}"
        return cmd


class IOSNATRouter:
    def __init__(self, hostname, use_nvi=False):
        self.hostname = hostname
        self.use_nvi = use_nvi
        self.rules = []
        self.pools = []
        self.acls = {}
        self.inside_interfaces = []
        self.outside_interfaces = []

    def add_rule(self, **kwargs):
        self.rules.append(IOSNATRule(**kwargs))

    def add_pool(self, name, start, end, prefix):
        self.pools.append({'name': name, 'start': start, 'end': end, 'prefix': prefix})

    def add_acl_entry(self, acl_id, network):
        if acl_id not in self.acls:
            self.acls[acl_id] = []
        self.acls[acl_id].append(network)

    def add_interfaces(self, inside=None, outside=None):
        if inside:
            items = inside if isinstance(inside, list) else [inside]
            self.inside_interfaces.extend([normalize_interface_name(i) for i in items])
        if outside:
            items = outside if isinstance(outside, list) else [outside]
            self.outside_interfaces.extend([normalize_interface_name(i) for i in items])

    def generate_cli_config(self):
        lines = [f"! Master NAT/PAT Configuration for {self.hostname}"]
        lines.append("! Interface NAT Roles")
        nat_cmd = "ip nat enable" if self.use_nvi else "ip nat inside"
        for iface in self.inside_interfaces:
            lines.append(f"interface {iface}")
            lines.append(f" {nat_cmd}")
        nat_cmd = "ip nat enable" if self.use_nvi else "ip nat outside"
        for iface in self.outside_interfaces:
            lines.append(f"interface {iface}")
            lines.append(f" {nat_cmd}")
        lines.append("exit")
        if self.acls:
            lines.append("! NAT Access Control Lists")
            for acl_id, nets in self.acls.items():
                for net in nets:
                    lines.append(f"access-list {acl_id} permit {net}")
        if self.pools:
            lines.append("! NAT Pools")
            for p in self.pools:
                lines.append(f"ip nat pool {p['name']} {p['start']} {p['end']} prefix-length {p['prefix']}")
        if self.rules:
            lines.append("! NAT Translation Rules")
            for rule in self.rules:
                lines.append(rule.generate_command())
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Master Cisco IOS NAT/PAT Generator.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    args = parser.parse_args()
    if args.file:
        try:
            data = normalize_entries(parse_file(args.file), preferred_keys=('items', 'devices'))
            for idx, r_data in enumerate(data):
                if not isinstance(r_data, dict):
                    continue
                router = IOSNATRouter(entry_name(r_data, idx), r_data.get('use_nvi', False))
                router.add_interfaces(
                    inside=r_data.get('inside_interfaces'),
                    outside=r_data.get('outside_interfaces')
                )
                for acl_id, nets in r_data.get('acls', {}).items():
                    nets = normalize_items(nets)
                    for net in nets:
                        router.add_acl_entry(acl_id, net)
                for p in normalize_items(r_data.get('pools', [])):
                    if not isinstance(p, dict):
                        continue
                    router.add_pool(**p)
                for r in normalize_items(r_data.get('rules', [])):
                    if not isinstance(r, dict):
                        continue
                    router.add_rule(**r)
                for r in normalize_items(r_data.get('static_nats', [])):
                    if not isinstance(r, dict):
                        continue
                    router.add_rule(rule_type='static', local_ip=r.get('inside_ip'), global_ip=r.get('outside_ip'))
                for r in normalize_items(r_data.get('ipv6_nats', [])):
                    if not isinstance(r, dict):
                        continue
                    router.add_rule(rule_type='static', is_ipv6=True, local_ip=r.get('inside_ip'), global_ip=r.get('outside_ip'))
                print(f"\n! --- {router.hostname} ---")
                print(router.generate_cli_config())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python3 nat_portal.py --file [config.yaml]")


if __name__ == "__main__":
    main()
