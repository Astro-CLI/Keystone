import json
import argparse
from format_parser import parse_file, detect_format

class IOSNATRule:
    def __init__(self, rule_type, local_ip=None, global_ip=None, local_port=None, global_port=None, 
                 acl_id=None, pool=None, interface=None, protocol='tcp', description=None):
        self.rule_type = rule_type # 'static', 'dynamic', 'overload', 'port-forward'
        self.local_ip = local_ip
        self.global_ip = global_ip
        self.local_port = local_port
        self.global_port = global_port
        self.acl_id = acl_id
        self.pool = pool
        self.interface = interface
        self.protocol = protocol
        self.description = description

    def generate_command(self):
        cmd = ""
        if self.rule_type == 'static':
            cmd = f"ip nat inside source static {self.local_ip} {self.global_ip}"
        
        elif self.rule_type == 'port-forward':
            cmd = f"ip nat inside source static {self.protocol} {self.local_ip} {self.local_port} {self.global_ip} {self.global_port} extendable"
        
        elif self.rule_type == 'dynamic':
            cmd = f"ip nat inside source list {self.acl_id} pool {self.pool}"
        
        elif self.rule_type == 'overload':
            target = f"interface {self.interface}" if self.interface else f"pool {self.pool}"
            cmd = f"ip nat inside source list {self.acl_id} {target} overload"
        
        if self.description:
            return f"! {self.description}\n{cmd}"
        return cmd

class IOSNATRouter:
    def __init__(self, hostname, use_nvi=False):
        self.hostname = hostname
        self.use_nvi = use_nvi # NAT Virtual Interface (ip nat enable)
        self.rules = []
        self.pools = []
        self.acls = {} # id: [networks]
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
        if inside: self.inside_interfaces.extend(inside if isinstance(inside, list) else [inside])
        if outside: self.outside_interfaces.extend(outside if isinstance(outside, list) else [outside])

    def generate_cli_config(self):
        lines = [f"! Master NAT/PAT Configuration for {self.hostname}"]
        
        # Interface configuration
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

        # ACL Generation
        if self.acls:
            lines.append("! NAT Access Control Lists")
            for acl_id, nets in self.acls.items():
                for net in nets:
                    lines.append(f"access-list {acl_id} permit {net}")

        # NAT Pools
        if self.pools:
            lines.append("! NAT Pools")
            for p in self.pools:
                lines.append(f"ip nat pool {p['name']} {p['start']} {p['end']} prefix-length {p['prefix']}")

        # NAT Rules
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
            data = parse_file(args.file)
            if isinstance(data, dict):
                data = [data]
            
            for r_data in data:
                router = IOSNATRouter(r_data['hostname'], r_data.get('use_nvi', False))
                router.add_interfaces(inside=r_data.get('inside_interfaces'), 
                                     outside=r_data.get('outside_interfaces'))
                for acl_id, nets in r_data.get('acls', {}).items():
                    for net in nets:
                        router.add_acl_entry(acl_id, net)
                for p in r_data.get('pools', []):
                    router.add_pool(**p)
                for r in r_data.get('rules', []):
                    router.add_rule(**r)
                
                print(f"\n--- {router.hostname} ---")
                print(router.generate_cli_config())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python3 ios_nat_generator.py --file [config.yaml]")

if __name__ == "__main__":
    main()
