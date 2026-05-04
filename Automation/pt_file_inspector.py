#!/usr/bin/env python3
"""
Packet Tracer .pkt File Inspector

Utility to inspect, verify, and decrypt Packet Tracer 8.2.2 .pkt files.
Useful for debugging and understanding .pkt file structure.
"""

import argparse
import sys
import struct
import zlib
import os
from pathlib import Path

# Import the builder for decryption
sys.path.insert(0, os.path.dirname(__file__))
from pt_file_builder import PTFileBuilder


class PTFileInspector:
    """Inspect and analyze Packet Tracer .pkt files."""
    
    def __init__(self, filepath):
        """Initialize inspector with a .pkt file."""
        self.filepath = filepath
        self.data = None
        self.header = None
        self.payload = None
        self.xml_content = None
        
        self._load_file()
    
    def _load_file(self):
        """Load and parse .pkt file."""
        try:
            with open(self.filepath, 'rb') as f:
                self.data = f.read()
            
            if len(self.data) < 4:
                raise ValueError("File too small - minimum 4 bytes required")
            
            # Parse header
            self.header = struct.unpack('>I', self.data[:4])[0]
            self.payload = self.data[4:]
        except Exception as e:
            print(f"Error loading file: {e}", file=sys.stderr)
            raise
    
    def get_file_info(self):
        """Get basic file information."""
        info = {
            'filepath': self.filepath,
            'filesize': len(self.data),
            'header_value': self.header,
            'payload_size': len(self.payload),
            'exists': os.path.exists(self.filepath),
            'readable': os.access(self.filepath, os.R_OK),
        }
        return info
    
    def decrypt_and_decompress(self):
        """Decrypt and decompress the .pkt file."""
        try:
            builder = PTFileBuilder({})
            self.xml_content = builder.decrypt_and_decompress(self.data)
            return self.xml_content
        except Exception as e:
            print(f"Error decrypting/decompressing: {e}", file=sys.stderr)
            return None
    
    def validate_xml(self):
        """Validate XML structure."""
        if not self.xml_content:
            self.decrypt_and_decompress()
        
        if not self.xml_content:
            return False, "Failed to decompress XML"
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(self.xml_content)
            
            # Check basic structure
            if root.tag != 'PacketTracer':
                return False, f"Invalid root tag: {root.tag}"
            
            version = root.get('version', '')
            build = root.get('build', '')
            
            checks = {
                'has_network': root.find('Network') is not None,
                'has_devices': len(root.findall('.//Device')) > 0,
                'version_822': version == '8.2.2',
            }
            
            return True, checks
        except Exception as e:
            return False, str(e)
    
    def print_summary(self):
        """Print summary information."""
        info = self.get_file_info()
        
        print("\n" + "=" * 60)
        print("Packet Tracer .pkt File Inspector")
        print("=" * 60)
        
        print(f"\nFile: {info['filepath']}")
        print(f"Size: {info['filesize']} bytes")
        print(f"Header (uncompressed XML size): {info['header_value']} bytes")
        print(f"Payload (compressed): {info['payload_size']} bytes")
        print(f"Compression ratio: {info['payload_size'] / info['header_value'] * 100:.1f}%")
        
        # Try to decompress
        if self.decrypt_and_decompress():
            print(f"\n✓ Successfully decrypted and decompressed")
            print(f"  XML size: {len(self.xml_content)} bytes")
            
            # Validate XML
            valid, result = self.validate_xml()
            if valid:
                print(f"✓ XML is valid")
                if isinstance(result, dict):
                    print(f"  - Has Network: {result['has_network']}")
                    print(f"  - Has Devices: {result['has_devices']}")
                    print(f"  - PT Version 8.2.2: {result['version_822']}")
            else:
                print(f"✗ XML validation failed: {result}")
        else:
            print(f"✗ Failed to decrypt/decompress file")
        
        print("=" * 60 + "\n")
    
    def print_hex_dump(self, lines=10):
        """Print hex dump of the file."""
        print("\nHex Dump (first {} bytes):".format(lines * 16))
        print("-" * 60)
        
        for i in range(0, min(len(self.data), lines * 16), 16):
            hex_part = ' '.join(f'{b:02x}' for b in self.data[i:i+16])
            ascii_part = ''.join(
                chr(b) if 32 <= b < 127 else '.'
                for b in self.data[i:i+16]
            )
            print(f"{i:08x}: {hex_part:<48} {ascii_part}")
        
        print("-" * 60 + "\n")
    
    def print_xml(self, pretty=True):
        """Print the decrypted XML content."""
        if not self.xml_content:
            if not self.decrypt_and_decompress():
                print("Failed to decompress XML")
                return
        
        if pretty:
            try:
                from xml.dom.minidom import parseString
                dom = parseString(self.xml_content)
                formatted = dom.toprettyxml(indent="  ")
                # Remove the XML declaration (first line)
                formatted = '\n'.join(formatted.split('\n')[1:])
                print(formatted)
            except Exception:
                print(self.xml_content)
        else:
            print(self.xml_content)
    
    def get_device_count(self):
        """Get number of devices in the topology."""
        if not self.xml_content:
            self.decrypt_and_decompress()
        
        if not self.xml_content:
            return 0
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(self.xml_content)
            devices = root.findall('.//Device')
            return len(devices)
        except Exception:
            return 0
    
    def list_devices(self):
        """List all devices in the .pkt file."""
        if not self.xml_content:
            self.decrypt_and_decompress()
        
        if not self.xml_content:
            print("Cannot decompress file")
            return
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(self.xml_content)
            devices = root.findall('.//Device')
            
            print("\nDevices in topology:")
            print("-" * 60)
            
            if not devices:
                print("  (no devices found)")
                return
            
            for device in devices:
                device_id = device.get('id', '?')
                device_name = device.get('name', 'Unknown')
                device_type = device.get('type', 'Unknown')
                
                print(f"  [{device_id}] {device_name:20} ({device_type})")
            
            print("-" * 60 + "\n")
        except Exception as e:
            print(f"Error listing devices: {e}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Inspect and analyze Packet Tracer .pkt files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic file information
  %(prog)s network.pkt
  
  # Show hex dump
  %(prog)s network.pkt --hex 20
  
  # Extract and display XML
  %(prog)s network.pkt --xml
  
  # Pretty-print XML
  %(prog)s network.pkt --xml --pretty
  
  # List devices only
  %(prog)s network.pkt --list-devices
        """
    )
    
    parser.add_argument('pkt_file', help='Path to .pkt file')
    parser.add_argument('--hex', type=int, metavar='LINES', 
                       help='Show hex dump (number of 16-byte lines)')
    parser.add_argument('--xml', action='store_true', help='Show decrypted XML')
    parser.add_argument('--pretty', action='store_true', 
                       help='Pretty-print XML (use with --xml)')
    parser.add_argument('--list-devices', action='store_true', 
                       help='List all devices in topology')
    
    args = parser.parse_args()
    
    # Check file exists
    if not os.path.exists(args.pkt_file):
        print(f"Error: File not found: {args.pkt_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        inspector = PTFileInspector(args.pkt_file)
    except Exception as e:
        sys.exit(1)
    
    # Print summary by default
    inspector.print_summary()
    
    # Show hex dump if requested
    if args.hex:
        inspector.print_hex_dump(lines=args.hex)
    
    # List devices if requested
    if args.list_devices:
        inspector.list_devices()
    
    # Show XML if requested
    if args.xml:
        inspector.print_xml(pretty=args.pretty)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
