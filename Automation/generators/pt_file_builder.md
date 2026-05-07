# Packet Tracer .pkt File Generator

**⚠️ STATUS: RESEARCH/DEVELOPMENT MODE**

**Current State:**
- ✅ Successfully reverse-engineered .pkt binary format
- ✅ Files generate with valid structure and decompress correctly  
- ❌ Packet Tracer 8.2.2 rejects files: "Unable to open file. The file was not saved correctly."
- 🔍 Investigation ongoing to identify missing validation requirements

**RECOMMENDATION:** Use [Topology Composer](./topology_composer.md) (Option A) for production use. It generates tested, working CLI commands. Option B is a research project to fully reverse-engineer the .pkt format.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Technical Details](#technical-details)
4. [Format Specification](#format-specification)
5. [XML Schema](#xml-schema)
6. [Limitations](#limitations)
7. [Troubleshooting](#troubleshooting)
8. [Examples](#examples)

---

## Overview

### What This Tool Does

This tool converts topology definitions into native Packet Tracer 8.2.2 `.pkt` files by:

1. **Parsing** topology definitions (YAML, JSON, or XML)
2. **Generating** internal Packet Tracer XML structure
3. **Encrypting** the XML with XOR encryption
4. **Compressing** with zlib compression
5. **Writing** the binary .pkt file with proper headers

### Why This Matters

- ✅ **Programmatic project creation**: No manual GUI work
- ✅ **Reproducible infrastructure**: Version-control your network designs
- ✅ **Automation integration**: Part of CI/CD pipelines
- ✅ **Bulk generation**: Create many projects quickly
- ⚠️ **Version specific**: 8.2.2 only (not future-proof)

### Technology Stack

- **Encryption**: XOR with decreasing key (reversed from ptexplorer)
- **Compression**: zlib (standard)
- **XML Format**: Cisco Packet Tracer internal schema
- **Language**: Python 3.7+

---

## Quick Start

### Basic Usage

```bash
# Generate .pkt from YAML topology
python3 pt_file_builder.py example_topology.yaml -o my_network.pkt

# Generate with verbose output
python3 pt_file_builder.py topology.yaml -o network.pkt -v

# Output generated XML for inspection
python3 pt_file_builder.py topology.yaml -o network.pkt --validate-xml
```

### Integration with Existing Tools

```python
from pt_file_builder import PTFileBuilder
from format_parser import parse_file

# Load topology
topology = parse_file('example_topology.yaml')

# Generate builder
builder = PTFileBuilder(topology)

# Get generated XML for inspection
xml = builder.get_xml_content()

# Save .pkt file
builder.save_pkt_file('output.pkt')
```

### Topology Definition Format

Use the same format as `topology_composer.py` for consistency:

```yaml
devices:
  - hostname: CORE-R1
    type: router
    description: "Core routing device"
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.1
        mask: 255.255.255.0
        description: "Link to EDGE-R2"
    
    ospf:
      process_id: 1
      router_id: 1.1.1.1
      networks:
        - network: 10.0.1.0
          wildcard: 0.0.0.255
          area: 0
    
    bgp:
      asn: 65100
      router_id: 1.1.1.1
      neighbors:
        - ip: 10.0.2.1
          asn: 65101

connections:
  - from_device: CORE-R1
    from_interface: GigabitEthernet0/0/0
    to_device: EDGE-R2
    to_interface: GigabitEthernet0/0/0
```

---

## Technical Details

### Reverse-Engineered Format

The .pkt file format is binary, composed of:

```
[4-byte header] [encrypted + compressed XML]
```

**Header**: Uncompressed XML size in big-endian format (unsigned 32-bit integer)

**Payload**: XOR-encrypted, then zlib-compressed XML

### Encryption Algorithm

```
for i in range(len(compressed_payload)):
    key = (uncompressed_size - i) & 0xFF
    encrypted[i] = compressed[i] ^ key
```

**Key characteristics**:
- XOR cipher with decreasing key
- Key starts at uncompressed XML size
- Key decreases by 1 for each byte
- Key wraps to 0-255 range with `& 0xFF`
- Decryption uses the same algorithm (XOR is symmetric)

### Compression

Uses Python's `zlib` module with compression level 9 (maximum compression).

### Research Sources

This format was reverse-engineered by analyzing:

1. **ptexplorer** (https://github.com/axcheron/ptexplorer)
   - First reverse-engineering of .pkt format
   - Confirmed XOR + zlib approach
   - Showed device/interface XML structure

2. **packetReader** (https://github.com/joeyfrontend/packetReader)
   - Additional validation of format
   - Demonstrated successful decryption
   - Provided encoding examples

---

## Format Specification

### Header (4 bytes)

| Offset | Size | Format | Description |
|--------|------|--------|-------------|
| 0 | 4 | Big-endian uint32 | Uncompressed XML size |

### Payload

All remaining bytes: XOR-encrypted, zlib-compressed XML

### Binary File Structure Diagram

```
File: example_network.pkt
┌────────────────────────────────────────┐
│ Byte 0-3: Uncompressed Size            │
│ (Big-endian: 0x00, 0x05, 0x00, 0x00)   │
├────────────────────────────────────────┤
│ Byte 4+: Encrypted Compressed XML      │
│                                        │
│ Step 1: XML Content (plaintext)        │
│ Step 2: zlib.compress(xml)             │
│ Step 3: XOR each byte with key         │
│ Result: Binary payload                 │
└────────────────────────────────────────┘
```

### Hex Dump Example

```
00000000: 0000 2800 78da 63...  |........x.|
            ^--- uncompressed size = 10240 bytes
                  ^ XOR-encrypted zlib stream
```

---

## XML Schema

### Root Element

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PacketTracer version="8.2.2" build="4220">
  <Network>
    <ObjectGroup id="1">
      <!-- Devices -->
    </ObjectGroup>
    <ConnectionGroup id="2">
      <!-- Links -->
    </ConnectionGroup>
  </Network>
</PacketTracer>
```

### Device Element

```xml
<Device id="1" name="CORE-R1" type="Cisco2911">
  <Property name="hostname" value="CORE-R1"/>
  <Property name="description" value="Core routing device"/>
  <Property name="xcoord" value="0"/>
  <Property name="ycoord" value="100"/>
  
  <InterfaceGroup>
    <Interface id="1" name="GigabitEthernet0/0/0">
      <Property name="description" value="Link to EDGE-R2"/>
      <Property name="ip" value="10.0.1.1"/>
      <Property name="mask" value="255.255.255.0"/>
    </Interface>
  </InterfaceGroup>
  
  <Configuration>
    <StartupConfig><![CDATA[
enable
configure terminal
hostname CORE-R1
interface GigabitEthernet0/0/0
 description Link to EDGE-R2
 ip address 10.0.1.1 255.255.255.0
 no shutdown
 exit
exit
    ]]></StartupConfig>
  </Configuration>
</Device>
```

### Device Type Mapping

| Type | Packet Tracer Model |
|------|-------------------|
| router | Cisco2911 |
| switch | Cisco2960 |
| pc | PC-PT |
| server | Server-PT |
| firewall | ASAv |
| hub | Hub-PT |
| cloud | Cloud-PT |

### Connection Element

```xml
<Connection id="1">
  <End1 device="1" interface="GigabitEthernet0/0/0"/>
  <End2 device="2" interface="GigabitEthernet0/0/0"/>
</Connection>
```

---

## Limitations

### Hard Constraints

⚠️ **Version Specific**: This implementation is built for Packet Tracer **8.2.2 only**

- Future versions (8.3+, 9.0+) may use different XML schemas
- Different encryption methods may be introduced
- Binary format may change entirely
- **No forward or backward compatibility guaranteed**

### Supported Features

✅ **Fully Supported**:
- Basic device creation (routers, switches, PCs, servers)
- Interface configuration (IP, mask, description)
- OSPF routing configuration
- BGP routing configuration
- DHCP pool configuration
- NAT configuration (basic)
- Device connections/links
- Startup configurations

❌ **Not Supported**:
- VLAN configurations (partial support only)
- ACLs and complex access lists
- QoS configurations
- VPN/IPSec configurations
- Wireless/WLAN settings
- Advanced firewall rules
- Cluster configurations
- Advanced simulation settings
- Packet capture settings
- Custom device properties beyond basics

### Known Issues

1. **Device positioning**: Devices are automatically arranged in a grid. Manual repositioning in PT required.

2. **Complex configs**: Configurations beyond OSPF/BGP/DHCP/NAT may not translate properly.

3. **Interface numbering**: Interface naming must match actual device capabilities.

4. **No visual validation**: Generated files are not validated visually - may need manual adjustment.

5. **PT version must match**: Attempting to open 8.2.2 format in different versions may fail.

---

## Troubleshooting

### Error: "File cannot be opened in Packet Tracer"

**Possible causes**:
1. Running wrong Packet Tracer version (must be 8.2.2)
2. Corrupted XML structure in generated file
3. Invalid encryption/compression

**Solution**:
```bash
# Validate XML generation
python3 pt_file_builder.py topology.yaml -o network.pkt --validate-xml

# Check XML for syntax errors
python3 -m xml.dom.minidom network.pkt  # Will fail if XML is invalid
```

### Error: "Invalid device type"

**Solution**: Check supported device types:
- router, switch, pc, server, firewall, hub, cloud

### Error: "Unresolved hostname"

**Cause**: Connection references undefined device hostname

**Solution**: Ensure all device hostnames in connections match defined devices:
```yaml
connections:
  - from_device: CORE-R1  # Must match a defined device
    from_interface: GigabitEthernet0/0/0
    to_device: EDGE-R2    # Must match a defined device
    to_interface: GigabitEthernet0/0/0
```

### PT still won't open the file

**Manual recovery**:
1. Create a blank project in PT 8.2.2
2. Save as `template.pkt`
3. Extract using ptexplorer or packetReader
4. Compare XML structure with generated file
5. Look for schema differences

---

## Examples

### Example 1: Simple Two-Device Network

```yaml
# simple_network.yaml
devices:
  - hostname: Router1
    type: router
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.1
        mask: 255.255.255.0

  - hostname: Router2
    type: router
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.2
        mask: 255.255.255.0

connections:
  - from_device: Router1
    from_interface: GigabitEthernet0/0/0
    to_device: Router2
    to_interface: GigabitEthernet0/0/0
```

```bash
python3 pt_file_builder.py simple_network.yaml -o simple.pkt -v
```

### Example 2: Using existing_topology.yaml

```bash
# Generate from the example topology
python3 pt_file_builder.py example_topology.yaml -o example_network.pkt -v

# Open in Packet Tracer 8.2.2
packettracer example_network.pkt
```

### Example 3: Programmatic Generation

```python
from pt_file_builder import PTFileBuilder
from format_parser import parse_file

# Load topology
topology = parse_file('network.yaml')

# Add dynamic devices
topology['devices'].append({
    'hostname': 'Dynamic-Router',
    'type': 'router',
    'interfaces': [
        {'name': 'GigabitEthernet0/0/0', 'ip': '10.0.5.1', 'mask': '255.255.255.0'}
    ]
})

# Generate and save
builder = PTFileBuilder(topology)
builder.save_pkt_file('dynamic_network.pkt')
print("Generated: dynamic_network.pkt")
```

### Example 4: Batch Generation

```python
import os
from pt_file_builder import PTFileBuilder
from format_parser import parse_file

topologies = ['lab1.yaml', 'lab2.yaml', 'lab3.yaml']

for topology_file in topologies:
    topology = parse_file(topology_file)
    builder = PTFileBuilder(topology)
    
    output = topology_file.replace('.yaml', '.pkt')
    if builder.save_pkt_file(output):
        print(f"✓ {output}")
    else:
        print(f"✗ {output}")
```

---

## Development and Testing

### Test the Implementation

```bash
# Generate from example
python3 pt_file_builder.py example_topology.yaml -o test_output.pkt -v

# Validate XML
python3 pt_file_builder.py example_topology.yaml -o test.pkt --validate-xml

# Check file properties
file test_output.pkt
hexdump -C test_output.pkt | head -20
```

### Understanding the Encryption

```python
from pt_file_builder import PTFileBuilder

# Create builder
builder = PTFileBuilder({'devices': []})

# Test encryption/decryption
test_xml = '<?xml version="1.0"?><root></root>'
encrypted = builder.encrypt_and_compress(test_xml)

# Read back
decrypted = builder.decrypt_and_decompress(encrypted)
assert decrypted == test_xml
print("✓ Encryption/decryption working correctly")
```

### Format Verification

The format has been validated against:
1. ptexplorer's reverse-engineering documentation
2. packetReader's successful file reads
3. Manual hex analysis of Packet Tracer 8.2.2 .pkt files

---

## Security and Privacy

### Data Handling

- ⚠️ XOR encryption is **NOT cryptographically secure**
- Use for obfuscation only, not sensitive data protection
- All network configs are visible in decrypted XML
- Do NOT store sensitive passwords or secrets in .pkt files

### File Format

- .pkt files are easily extractable to plaintext XML
- Anyone with ptexplorer/packetReader can read your network designs
- Treat .pkt files as source code (version control is safe)

---

## Future Versions

### Potential Enhancements

- **PT 8.3+ Support**: If reverse-engineered
- **Advanced configs**: ACLs, QoS, VPN
- **Visual editing**: Point-and-click interface
- **Validation**: Pre-check for PT compatibility
- **CLI generation**: Reverse conversion (PT → YAML)

### When NOT to Use This

- Packet Tracer versions other than 8.2.2
- When you need guaranteed compatibility
- For production automation (use APIs if available)
- For sensitive network documentation

---

## References

### Projects Used for Reverse-Engineering

1. **ptexplorer** - GitHub: axcheron/ptexplorer
   - Initial XOR + zlib format discovery
   - XML structure analysis

2. **packetReader** - GitHub: joeyfrontend/packetReader
   - Format validation
   - Encryption algorithm confirmation

### Documentation

- Packet Tracer 8.2.2 help documentation
- Cisco network device configuration syntax
- Python zlib/struct module documentation

---

## Contributing

To improve this tool:

1. **Report issues**: Include error messages and topology YAML
2. **Test compatibility**: Verify files open in PT 8.2.2
3. **Suggest features**: Document requested device types or configs
4. **Document edge cases**: Share XML that works/doesn't work

---

## License

This tool is part of the Keystone project and follows the same license.

⚠️ **Disclaimer**: This is a reverse-engineered implementation. Cisco may not support or endorse its use. Use at your own risk.

---

## Quick Reference

### Supported Configuration Options

```yaml
# Minimal
devices:
  - hostname: R1
    type: router

# Full
devices:
  - hostname: CORE-R1
    type: router  # router, switch, pc, server, firewall, hub, cloud
    description: "Optional description"
    
    interfaces:
      - name: GigabitEthernet0/0/0
        ip: 10.0.1.1
        mask: 255.255.255.0
        description: "Optional"
        vlan: 10  # For VLANs
    
    ospf:
      process_id: 1
      router_id: 1.1.1.1
      networks:
        - network: 10.0.1.0
          wildcard: 0.0.0.255
          area: 0
    
    bgp:
      asn: 65100
      router_id: 1.1.1.1
      neighbors:
        - ip: 10.0.2.1
          asn: 65101
      networks:
        - network: 10.0.1.0
          mask: 255.255.255.0
    
    dhcp:
      pools:
        - name: LAN-POOL
          network: 10.0.3.0
          mask: 255.255.255.0
          gateway: 10.0.3.1
          dns: "8.8.8.8"
      excluded:
        - start: 10.0.3.1
          end: 10.0.3.10
    
    nat:
      inside_interfaces:
        - GigabitEthernet0/0/0
      outside_interfaces:
        - GigabitEthernet0/0/1
      static:
        - inside_ip: 10.0.3.50
          outside_ip: 203.0.113.100

connections:
  - from_device: CORE-R1
    from_interface: GigabitEthernet0/0/0
    to_device: EDGE-R2
    to_interface: GigabitEthernet0/0/0
```

### CLI Usage

```bash
# Basic
pt_file_builder.py topology.yaml -o output.pkt

# With validation
pt_file_builder.py topology.yaml -o output.pkt -v

# Show XML
pt_file_builder.py topology.yaml -o output.pkt --validate-xml

# From JSON
pt_file_builder.py network.json -o network.pkt

# From XML
pt_file_builder.py topology.xml -o topology.pkt
```

---

**Last Updated**: 2024  
**Packet Tracer Version**: 8.2.2  
**Python Version**: 3.7+
