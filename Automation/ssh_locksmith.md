# Cisco SSH Security Generator

## Purpose and Design
The `ssh_generator.py` script is designed to automate the process of securing Cisco IOS devices for SSH access. It follows an Object-Oriented design using the `SSHConfig` class to encapsulate all security parameters, ensuring that essential hardening steps are not missed during deployment.

## Key Features
- **Key Management**: Automates RSA key generation with customizable modulus sizes.
- **Access Hardening**: Configures SSH version, timeouts, and authentication retries.
- **Identity Management**: Sets hostname, domain name, local users, and enable secrets.
- **Line Security**: Automatically secures VTY lines for local authentication and SSH transport only.

## Examples

### Example 1: Simple Scenario (Standard SSH Hardening)
A basic setup to enable SSH access on a new router.
- **RSA Key**: 2048 bits
- **Version**: 2
- **User**: admin

### Example 2: Advanced Scenario (High-Security Environment)
Hardened configuration for sensitive infrastructure.
- **RSA Key**: 4096 bits
- **Timeout**: 30 seconds
- **Retries**: 2
- **Enable Secret**: Defined for privileged access.

## CLI Usage
**Generate from YAML file:**
```bash
python3 ssh_generator.py --file security_inventory.yaml
```

**Generate from JSON file:**
```bash
python3 ssh_generator.py --file security_inventory.json
```

## Sample YAML Input
```yaml
- hostname: Core-Switch-01
  domain_name: corp.internal
  username: netadmin
  password: StrongPassword123
  enable_secret: SuperSecretEnable
  key_size: 2048
  timeout: 120
```
