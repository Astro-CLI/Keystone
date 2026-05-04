#!/usr/bin/env python3
"""
Packet Tracer .pkt File Generator

Converts topology definitions (YAML/JSON/XML) into valid Packet Tracer 8.2.2 .pkt files.
Implements reverse-engineered .pkt format: XOR encryption + zlib compression.

The .pkt format (reverse-engineered from ptexplorer and packetReader projects):
  - [4 bytes: uncompressed XML size (big-endian)] + [zlib-compressed XML payload]
  - Encryption: XOR each byte with decreasing key = (uncompressed_size - i)
  where i is the byte position (0-based)

Warning: This implementation is version-specific to Packet Tracer 8.2.2.
Future versions may use different XML schemas or encryption methods.
"""

import json
import zlib
import struct
import argparse
import sys
import os
from pathlib import Path
from xml.dom.minidom import parseString
from collections import OrderedDict
from datetime import datetime

# Import shared utilities
sys.path.insert(0, os.path.dirname(__file__))
from format_parser import parse_file, detect_format


class PTFileBuilder:
    """Generates Packet Tracer .pkt files from topology definitions."""
    
    # Packet Tracer 8.2.2 XML structure constants
    PT_VERSION = "8.2.2"
    PT_BUILD = "4220"  # Version code for PT 8.2.2
    
    def __init__(self, topology_data):
        """
        Initialize the builder with topology data.
        
        Args:
            topology_data (dict): Parsed topology definition
        """
        self.topology = topology_data
        self.xml_content = None
        self.devices = {}
        self.connections = []
        self.next_device_id = 1
        self.next_port_id = 1
    
    def build_xml_structure(self):
        """Generate the internal PT XML structure from topology."""
        self._generate_packet_tracer_xml()
        return self.xml_content
    
    def _generate_packet_tracer_xml(self):
        """Generate complete Packet Tracer XML document."""
        xml_parts = []
        
        # XML declaration
        xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        
        # Root element
        xml_parts.append(f'<PacketTracer version="{self.PT_VERSION}" build="{self.PT_BUILD}">')
        
        # Network structure
        xml_parts.append('  <Network>')
        xml_parts.append('    <ObjectGroup id="1">')
        
        # Process devices
        if 'devices' in self.topology:
            for idx, device in enumerate(self.topology['devices'], start=1):
                device_xml = self._create_device_xml(device, idx)
                xml_parts.append(device_xml)
        
        xml_parts.append('    </ObjectGroup>')
        
        # Connections/links
        if 'connections' in self.topology or self.connections:
            xml_parts.append('    <ConnectionGroup id="2">')
            connections = self.topology.get('connections', self.connections)
            for conn_idx, connection in enumerate(connections, start=1):
                conn_xml = self._create_connection_xml(connection, conn_idx)
                xml_parts.append(conn_xml)
            xml_parts.append('    </ConnectionGroup>')
        
        xml_parts.append('  </Network>')
        xml_parts.append('</PacketTracer>')
        
        self.xml_content = '\n'.join(xml_parts)
    
    def _create_device_xml(self, device, device_id):
        """Create XML for a single device."""
        hostname = device.get('hostname', f'Router{device_id}')
        device_type = device.get('type', 'router').lower()
        description = device.get('description', '')
        
        # Map device types to PT device models
        type_model_map = {
            'router': 'Cisco2911',
            'switch': 'Cisco2960',
            'pc': 'PC-PT',
            'server': 'Server-PT',
            'firewall': 'ASAv',
            'hub': 'Hub-PT',
            'cloud': 'Cloud-PT',
        }
        
        model = type_model_map.get(device_type, 'Cisco2911')
        
        xml_lines = []
        xml_lines.append(f'      <Device id="{device_id}" name="{hostname}" type="{model}">')
        xml_lines.append(f'        <Property name="hostname" value="{hostname}"/>')
        
        if description:
            xml_lines.append(f'        <Property name="description" value="{description}"/>')
        
        # Position (simplified - arrange devices in a grid)
        x_pos = (device_id - 1) * 200
        y_pos = 100
        xml_lines.append(f'        <Property name="xcoord" value="{x_pos}"/>')
        xml_lines.append(f'        <Property name="ycoord" value="{y_pos}"/>')
        
        # Interfaces
        if 'interfaces' in device:
            xml_lines.append('        <InterfaceGroup>')
            for iface_idx, iface in enumerate(device['interfaces']):
                iface_xml = self._create_interface_xml(iface, iface_idx + 1)
                xml_lines.append(iface_xml)
            xml_lines.append('        </InterfaceGroup>')
        
        # Router configurations
        if device_type == 'router':
            config_xml = self._create_router_config_xml(device)
            if config_xml:
                xml_lines.append(config_xml)
        
        xml_lines.append('      </Device>')
        
        self.devices[hostname] = device_id
        return '\n'.join(xml_lines)
    
    def _create_interface_xml(self, interface, iface_id):
        """Create XML for a device interface."""
        name = interface.get('name', f'GigabitEthernet0/0/{iface_id - 1}')
        ip = interface.get('ip', '')
        mask = interface.get('mask', '255.255.255.0')
        description = interface.get('description', '')
        
        xml_lines = []
        xml_lines.append(f'          <Interface id="{iface_id}" name="{name}">')
        xml_lines.append(f'            <Property name="description" value="{description}"/>')
        
        if ip:
            xml_lines.append(f'            <Property name="ip" value="{ip}"/>')
            xml_lines.append(f'            <Property name="mask" value="{mask}"/>')
        
        xml_lines.append('          </Interface>')
        
        return '\n'.join(xml_lines)
    
    def _create_router_config_xml(self, device):
        """Create XML configuration element for router."""
        config_lines = []
        
        # Build startup config from device settings
        startup_config = ['enable', 'configure terminal']
        
        hostname = device.get('hostname', 'Router')
        startup_config.append(f'hostname {hostname}')
        
        # Basic interface configuration
        if 'interfaces' in device:
            for iface in device['interfaces']:
                iface_name = iface.get('name', '')
                ip = iface.get('ip')
                mask = iface.get('mask')
                description = iface.get('description', '')
                
                if iface_name:
                    startup_config.append(f'interface {iface_name}')
                    
                    if description:
                        startup_config.append(f' description {description}')
                    
                    if ip and mask:
                        startup_config.append(f' ip address {ip} {mask}')
                    
                    startup_config.append(' no shutdown')
                    startup_config.append(' exit')
        
        # OSPF
        if 'ospf' in device:
            ospf = device['ospf']
            pid = ospf.get('process_id', 1)
            rid = ospf.get('router_id', '')
            
            startup_config.append(f'router ospf {pid}')
            
            if rid:
                startup_config.append(f' router-id {rid}')
            
            if 'networks' in ospf:
                for net in ospf['networks']:
                    network = net.get('network')
                    wildcard = net.get('wildcard')
                    area = net.get('area', 0)
                    if network and wildcard:
                        startup_config.append(f' network {network} {wildcard} area {area}')
            
            startup_config.append(' exit')
        
        # BGP
        if 'bgp' in device:
            bgp = device['bgp']
            asn = bgp.get('asn')
            rid = bgp.get('router_id', '')
            
            if asn:
                startup_config.append(f'router bgp {asn}')
                
                if rid:
                    startup_config.append(f' bgp router-id {rid}')
                
                if 'neighbors' in bgp:
                    for neighbor in bgp['neighbors']:
                        neighbor_ip = neighbor.get('ip')
                        neighbor_asn = neighbor.get('asn')
                        if neighbor_ip and neighbor_asn:
                            startup_config.append(f' neighbor {neighbor_ip} remote-as {neighbor_asn}')
                
                if 'networks' in bgp:
                    for net in bgp['networks']:
                        network = net.get('network')
                        mask = net.get('mask')
                        if network and mask:
                            startup_config.append(f' network {network} mask {mask}')
                
                startup_config.append(' exit')
        
        # DHCP
        if 'dhcp' in device:
            dhcp = device['dhcp']
            if 'pools' in dhcp:
                for pool in dhcp['pools']:
                    pool_name = pool.get('name', 'DEFAULT')
                    network = pool.get('network', '')
                    mask = pool.get('mask', '255.255.255.0')
                    gateway = pool.get('gateway', '')
                    
                    startup_config.append(f'ip dhcp pool {pool_name}')
                    startup_config.append(f' network {network} {mask}')
                    
                    if gateway:
                        startup_config.append(f' default-router {gateway}')
                    
                    startup_config.append(' exit')
            
            if 'excluded' in dhcp:
                for excluded in dhcp['excluded']:
                    start_ip = excluded.get('start')
                    end_ip = excluded.get('end')
                    if start_ip and end_ip:
                        startup_config.append(f'ip dhcp excluded-address {start_ip} {end_ip}')
        
        # NAT
        if 'nat' in device:
            nat = device['nat']
            
            if 'inside_interfaces' in nat:
                for iface in nat['inside_interfaces']:
                    startup_config.append(f'interface {iface}')
                    startup_config.append(' ip nat inside')
                    startup_config.append(' exit')
            
            if 'outside_interfaces' in nat:
                for iface in nat['outside_interfaces']:
                    startup_config.append(f'interface {iface}')
                    startup_config.append(' ip nat outside')
                    startup_config.append(' exit')
        
        startup_config.append('exit')
        
        config_xml = '        <Configuration>'
        config_xml += '\n          <StartupConfig><![CDATA['
        config_xml += '\n' + '\n'.join(startup_config)
        config_xml += '\n        ]]></StartupConfig>'
        config_xml += '\n        </Configuration>'
        
        return config_xml
    
    def _create_connection_xml(self, connection, conn_id):
        """Create XML for a network connection/link."""
        src_device = connection.get('from_device', '')
        src_interface = connection.get('from_interface', '')
        dst_device = connection.get('to_device', '')
        dst_interface = connection.get('to_interface', '')
        
        src_id = self.devices.get(src_device, 1)
        dst_id = self.devices.get(dst_device, 2)
        
        xml_lines = []
        xml_lines.append(f'      <Connection id="{conn_id}">')
        xml_lines.append(f'        <End1 device="{src_id}" interface="{src_interface}"/>')
        xml_lines.append(f'        <End2 device="{dst_id}" interface="{dst_interface}"/>')
        xml_lines.append('      </Connection>')
        
        return '\n'.join(xml_lines)
    
    def encrypt_and_compress(self, xml_content):
        """
        Encrypt and compress XML content using Packet Tracer format.
        
        Format: [4 bytes: uncompressed size] + [zlib-compressed + XOR-encrypted XML]
        
        Args:
            xml_content (str): The XML content to encrypt
            
        Returns:
            bytes: Encrypted and compressed binary data
        """
        # Convert XML to bytes
        xml_bytes = xml_content.encode('utf-8')
        uncompressed_size = len(xml_bytes)
        
        # Compress with zlib
        compressed_data = zlib.compress(xml_bytes, 9)
        
        # Encrypt with XOR using decreasing key
        encrypted_data = bytearray()
        for i, byte in enumerate(compressed_data):
            # XOR key decreases: starts at uncompressed_size, decreases to 1
            key = (uncompressed_size - i) & 0xFF
            encrypted_data.append(byte ^ key)
        
        # Create final binary data: [4-byte size] + [encrypted payload]
        # Size is in big-endian format
        size_bytes = struct.pack('>I', uncompressed_size)
        
        return size_bytes + bytes(encrypted_data)
    
    def decrypt_and_decompress(self, binary_data):
        """
        Decrypt and decompress Packet Tracer .pkt file data.
        
        Args:
            binary_data (bytes): The binary data from a .pkt file
            
        Returns:
            str: The decompressed XML content
        """
        # Extract uncompressed size (first 4 bytes, big-endian)
        uncompressed_size = struct.unpack('>I', binary_data[:4])[0]
        
        # Extract encrypted payload
        encrypted_data = binary_data[4:]
        
        # Decrypt with XOR using decreasing key
        decrypted_data = bytearray()
        for i, byte in enumerate(encrypted_data):
            # XOR key decreases: starts at uncompressed_size, decreases to 1
            key = (uncompressed_size - i) & 0xFF
            decrypted_data.append(byte ^ key)
        
        # Decompress
        decompressed_data = zlib.decompress(bytes(decrypted_data))
        
        return decompressed_data.decode('utf-8')
    
    def save_pkt_file(self, output_path):
        """
        Generate and save a .pkt file.
        
        Args:
            output_path (str): Path where the .pkt file should be saved
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate XML structure
            self.build_xml_structure()
            
            # Encrypt and compress
            binary_data = self.encrypt_and_compress(self.xml_content)
            
            # Write binary file
            with open(output_path, 'wb') as f:
                f.write(binary_data)
            
            return True
        except Exception as e:
            print(f"Error saving .pkt file: {e}", file=sys.stderr)
            return False
    
    def get_xml_content(self):
        """Get the generated XML content."""
        if not self.xml_content:
            self.build_xml_structure()
        return self.xml_content


def load_topology(filepath):
    """Load topology from YAML/JSON/XML file."""
    try:
        return parse_file(filepath)
    except Exception as e:
        print(f"Error loading topology file: {e}", file=sys.stderr)
        return None


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate Packet Tracer 8.2.2 .pkt files from topology definitions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate .pkt from YAML topology
  %(prog)s example_topology.yaml -o my_network.pkt
  
  # Generate from JSON
  %(prog)s network.json -o network.pkt
  
  # Generate and verify
  %(prog)s topology.yaml -o output.pkt -v
        """
    )
    
    parser.add_argument('topology', help='Topology definition file (YAML/JSON/XML)')
    parser.add_argument('-o', '--output', required=True, help='Output .pkt file path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--validate-xml', action='store_true', help='Output generated XML for inspection')
    
    args = parser.parse_args()
    
    # Load topology
    if args.verbose:
        print(f"Loading topology from: {args.topology}")
    
    topology = load_topology(args.topology)
    if not topology:
        sys.exit(1)
    
    # Build .pkt file
    if args.verbose:
        print("Building .pkt file structure...")
    
    builder = PTFileBuilder(topology)
    
    # Output XML if requested
    if args.validate_xml:
        xml_content = builder.get_xml_content()
        print("\n=== Generated XML ===")
        print(xml_content)
        print("=== End XML ===\n")
    
    # Generate and save
    if args.verbose:
        print(f"Generating .pkt file: {args.output}")
    
    if builder.save_pkt_file(args.output):
        file_size = os.path.getsize(args.output)
        if args.verbose:
            print(f"✓ Successfully created: {args.output} ({file_size} bytes)")
        else:
            print(f"✓ {args.output}")
        return 0
    else:
        print("✗ Failed to create .pkt file", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
