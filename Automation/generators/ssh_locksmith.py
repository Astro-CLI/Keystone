import json
import argparse
from format_parser import parse_file, detect_format


class SSHConfig:
    def __init__(self, hostname, domain_name, username, password, enable_secret=None,
                 key_size=2048, version=2, timeout=60, retries=3,
                 ipv6_vty=False, vty_acl_ipv6=None):
        self.hostname = hostname
        self.domain_name = domain_name
        self.username = username
        self.password = password
        self.enable_secret = enable_secret
        self.key_size = key_size
        self.version = version
        self.timeout = timeout
        self.retries = retries
        self.ipv6_vty = ipv6_vty
        self.vty_acl_ipv6 = vty_acl_ipv6 or "2001:db8::/32"

    def generate_cli_config(self):
        lines = [f"! SSH Security Configuration for {self.hostname}"]
        lines.append(f"hostname {self.hostname}")
        lines.append(f"ip domain-name {self.domain_name}")
        lines.append(f"crypto key generate rsa modulus {self.key_size}")
        lines.append(f"ip ssh version {self.version}")
        lines.append(f"ip ssh time-out {self.timeout}")
        lines.append(f"ip ssh authentication-retries {self.retries}")
        lines.append(f"username {self.username} secret {self.password}")
        if self.enable_secret:
            lines.append(f"enable secret {self.enable_secret}")
        if self.ipv6_vty:
            lines.append("ipv6 access-list VTY_ACL")
            lines.append(f" permit tcp {self.vty_acl_ipv6} any eq 22")
            lines.append(" exit")
        lines.append("line vty 0 15")
        lines.append(" login local")
        lines.append(" transport input ssh")
        if self.ipv6_vty:
            lines.append(" ipv6 access-class VTY_ACL in")
        lines.append(" exit")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate Cisco SSH configurations.")
    parser.add_argument("--file", help="Path to inventory file (JSON, YAML, or XML)")
    args = parser.parse_args()
    if args.file:
        try:
            data = parse_file(args.file)
            if isinstance(data, dict):
                data = [data]
            for entry in data:
                ssh = SSHConfig(
                    hostname=entry['hostname'],
                    domain_name=entry.get('domain_name', 'soymsa.local'),
                    username=entry.get('username', 'admin'),
                    password=entry.get('password', 'Cisco123'),
                    enable_secret=entry.get('enable_secret'),
                    key_size=entry.get('key_size', 1024),
                    version=entry.get('version', 2),
                    timeout=entry.get('timeout', 60),
                    retries=entry.get('retries', 3),
                    ipv6_vty=entry.get('ipv6_vty', False),
                    vty_acl_ipv6=entry.get('vty_acl_ipv6'),
                )
                print(f"\n! --- {ssh.hostname} ---")
                print(ssh.generate_cli_config())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python3 ssh_locksmith.py --file [config.yaml]")


if __name__ == "__main__":
    main()
