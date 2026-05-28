import json
import argparse
import sys
from format_parser import parse_file, detect_format

class ASAInterface:
    def __init__(self, name, nameif, security_level, ip=None, mask=None, ipv6=None, ipv6_mask=64):
        self.name = name
        self.nameif = nameif
        self.security_level = security_level
        self.ip = ip
        self.mask = mask
        self.ipv6 = ipv6
        self.ipv6_mask = ipv6_mask

    def generate_config(self):
        cmds = [f"interface {self.name}", f" nameif {self.nameif}", f" security-level {self.security_level}"]
        if self.ip and self.mask:
            cmds.append(f" ip address {self.ip} {self.mask}")
        if self.ipv6:
            cmds.append(f" ipv6 address {self.ipv6}/{self.ipv6_mask}")
        cmds.append(" no shutdown")
        return "\n".join(cmds)

class ASANetworkObject:
    def __init__(self, name, host=None, subnet=None, mask=None, ipv6_host=None, ipv6_subnet=None):
        self.name = name
        self.host = host
        self.subnet = subnet
        self.mask = mask
        self.ipv6_host = ipv6_host
        self.ipv6_subnet = ipv6_subnet

    def generate_config(self):
        config = f"object network {self.name}\n"
        if self.host:
            config += f" host {self.host}"
        elif self.subnet and self.mask:
            config += f" subnet {self.subnet} {self.mask}"
        elif self.ipv6_host:
            config += f" host {self.ipv6_host}"
        elif self.ipv6_subnet:
            config += f" subnet {self.ipv6_subnet}"
        return config

class ASANAT:
    def __init__(self, obj_name, type="dynamic", translated_interface="outside"):
        self.obj_name = obj_name
        self.type = type # 'static' or 'dynamic'
        self.translated_interface = translated_interface

    def generate_config(self):
        if self.type == "dynamic":
            return (f"object network {self.obj_name}\n"
                    f" nat (inside,{self.translated_interface}) dynamic interface")
        return f"! Manual NAT config required for {self.obj_name}"

class ASAACLRule:
    def __init__(self, access_list, action, protocol, source, destination, service=None):
        self.access_list = access_list
        self.action = action # 'permit' or 'deny'
        self.protocol = protocol
        self.source = source # object name or 'any'
        self.destination = destination # object name or 'any'
        self.service = service # e.g. 'eq 80'

    def generate_config(self):
        line = f"access-list {self.access_list} extended {self.action} {self.protocol} {self.source} {self.destination}"
        if self.service:
            line += f" {self.service}"
        return line

class ASARouter:
    def __init__(self, hostname):
        self.hostname = hostname
        self.interfaces = []
        self.objects = []
        self.nats = []
        self.acls = []
        self.access_groups = {} # name: interface

    def add_interface(self, **kwargs):
        self.interfaces.append(ASAInterface(**kwargs))

    def add_object(self, **kwargs):
        self.objects.append(ASANetworkObject(**kwargs))

    def add_nat(self, **kwargs):
        self.nats.append(ASANAT(**kwargs))

    def add_acl_rule(self, **kwargs):
        self.acls.append(ASAACLRule(**kwargs))

    def add_access_group(self, name, interface):
        self.access_groups[name] = interface

    def generate_cli_config(self):
        lines = [f"! ASA_Shield Configuration for {self.hostname}", "terminal width 132"]
        
        lines.append("! Interfaces")
        for i in self.interfaces:
            lines.append(i.generate_config())
            
        lines.append("! Network Objects")
        for o in self.objects:
            lines.append(o.generate_config())
            
        lines.append("! NAT")
        for n in self.nats:
            lines.append(n.generate_config())
            
        lines.append("! ACLs")
        for a in self.acls:
            lines.append(a.generate_config())
            
        lines.append("! Access Groups")
        for name, interface in self.access_groups.items():
            lines.append(f"access-group {name} in interface {interface}")
            
        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="ASA_Shield: Protecting the core with elegant precision.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    args = parser.parse_args()

    if args.file:
        try:
            data = parse_file(args.file)
            if isinstance(data, dict):
                data = [data]
            
            for r_data in data:
                asa = ASARouter(r_data['hostname'])
                for i in r_data.get('interfaces', []):
                    asa.add_interface(**i)
                for o in r_data.get('objects', []):
                    asa.add_object(**o)
                for n in r_data.get('nats', []):
                    asa.add_nat(**n)
                for a in r_data.get('acls', []):
                    asa.add_acl_rule(**a)
                for name, iface in r_data.get('access_groups', {}).items():
                    asa.add_access_group(name, iface)
                
                print(f"\n! --- {asa.hostname} ---")
                print(asa.generate_cli_config())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("=== ASA_Shield (Interactive) ===")
        print("Interactive mode for ASA is simplified. Use --file for complex setups.")
        hostname = input("Hostname: ")
        asa = ASARouter(hostname)
        print("Configuring Inside Interface:")
        asa.add_interface(name="GigabitEthernet0/0", nameif="inside", security_level=100, 
                         ip=input("Inside IP: "), mask=input("Inside Mask: "))
        print("Configuring Outside Interface:")
        asa.add_interface(name="GigabitEthernet0/1", nameif="outside", security_level=0, 
                         ip=input("Outside IP: "), mask=input("Outside Mask: "))
        
        print("\n--- Generated Config ---")
        print(asa.generate_cli_config())

if __name__ == "__main__":
    main()
