import json
import argparse
from format_parser import parse_file, detect_format

class SSHConfig:
    def __init__(self, hostname, domain_name, username, password, enable_secret=None, 
                 key_size=2048, version=2, timeout=60, retries=3):
        self.hostname = hostname
        self.domain_name = domain_name
        self.username = username
        self.password = password
        self.enable_secret = enable_secret
        self.key_size = key_size
        self.version = version
        self.timeout = timeout
        self.retries = retries

    def generate_cli_config(self):
        lines = [f"! SSH Security Configuration for {self.hostname}"]
        
        # Identity
        lines.append(f"hostname {self.hostname}")
        lines.append(f"ip domain-name {self.domain_name}")
        
        # Crypto keys
        lines.append(f"crypto key generate rsa modulus {self.key_size}")
        
        # SSH version and params
        lines.append(f"ip ssh version {self.version}")
        lines.append(f"ip ssh time-out {self.timeout}")
        lines.append(f"ip ssh authentication-retries {self.retries}")
        
        # Local Auth
        lines.append(f"username {self.username} secret {self.password}")
        if self.enable_secret:
            lines.append(f"enable secret {self.enable_secret}")
            
        # Line VTY
        lines.append("line vty 0 15")
        lines.append(" login local")
        lines.append(" transport input ssh")
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
                    retries=entry.get('retries', 3)
                )
                print(f"\n! --- {ssh.hostname} ---")
                print(ssh.generate_cli_config())
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Usage: python3 ssh_generator.py --file [config.yaml]")

if __name__ == "__main__":
    main()
