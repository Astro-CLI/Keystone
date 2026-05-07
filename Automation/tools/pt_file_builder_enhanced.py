#!/usr/bin/env python3
"""
Enhanced Packet Tracer .pkt File Builder with Debugging and Alternatives

Builds on pt_file_builder.py with:
- Debug logging for all operations
- Multiple encryption algorithm variants  
- Validation and inspection capabilities
- Format verification tools
- Alternative implementations to test
"""

import json
import zlib
import struct
import argparse
import sys
import os
from pathlib import Path
from xml.dom.minidom import parseString
import logging

sys.path.insert(0, os.path.dirname(__file__))
from pt_file_builder import PTFileBuilder

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-8s | %(message)s'
)
log = logging.getLogger(__name__)


class EnhancedPTFileBuilder(PTFileBuilder):
    """Enhanced builder with debugging and validation."""
    
    def __init__(self, topology_data, debug=False):
        super().__init__(topology_data)
        self.debug = debug
        self.debug_info = {}
    
    def encrypt_and_compress_debug(self, xml_content):
        """
        Encrypt and compress with full debugging.
        """
        if self.debug:
            log.debug("=== Encrypt & Compress Debug ===")
        
        # Convert XML to bytes
        xml_bytes = xml_content.encode('utf-8')
        uncompressed_size = len(xml_bytes)
        
        if self.debug:
            log.debug(f"XML size (uncompressed): {uncompressed_size} bytes")
            log.debug(f"XML first 100 chars: {xml_content[:100]}")
        
        # Compress with zlib
        compressed_data = zlib.compress(xml_bytes, 9)
        
        if self.debug:
            log.debug(f"Compressed size: {len(compressed_data)} bytes")
            log.debug(f"Compression ratio: {len(compressed_data) / uncompressed_size:.2%}")
            log.debug(f"First 32 bytes (hex): {' '.join(f'{b:02x}' for b in compressed_data[:32])}")
        
        # Encrypt with XOR using decreasing key
        encrypted_data = bytearray()
        for i, byte in enumerate(compressed_data):
            key = (uncompressed_size - i) & 0xFF
            encrypted_data.append(byte ^ key)
        
        if self.debug:
            log.debug(f"Encrypted size: {len(encrypted_data)} bytes")
            log.debug(f"First 32 bytes (hex): {' '.join(f'{b:02x}' for b in encrypted_data[:32])}")
        
        # Create final binary data: [4-byte size] + [encrypted payload]
        size_bytes = struct.pack('>I', uncompressed_size)
        final_data = size_bytes + bytes(encrypted_data)
        
        if self.debug:
            log.debug(f"Final file size: {len(final_data)} bytes")
            log.debug(f"Header value: {uncompressed_size} (0x{uncompressed_size:08x})")
            log.debug(f"First 32 bytes of final (hex): {' '.join(f'{b:02x}' for b in final_data[:32])}")
        
        # Store debug info
        self.debug_info = {
            'uncompressed_size': uncompressed_size,
            'compressed_size': len(compressed_data),
            'encrypted_size': len(encrypted_data),
            'final_size': len(final_data),
            'compression_ratio': len(compressed_data) / uncompressed_size,
        }
        
        return final_data
    
    def encrypt_and_compress_ptexplorer_style(self, xml_content):
        """
        Encrypt using ptexplorer algorithm (for comparison/testing).
        
        ptexplorer format:
        - ALL bytes encrypted (including 4-byte header)
        - XOR key = (total_file_size - position) & 0xFF
        - First 4 bytes of encrypted data = uncompressed size header
        """
        xml_bytes = xml_content.encode('utf-8')
        uncompressed_size = len(xml_bytes)
        
        # Compress
        compressed_data = zlib.compress(xml_bytes, 9)
        
        # Create data to encrypt: header + compressed
        size_bytes = struct.pack('>I', uncompressed_size)
        data_to_encrypt = size_bytes + compressed_data
        total_size = len(data_to_encrypt)
        
        if self.debug:
            log.debug("=== ptexplorer-style Encryption ===")
            log.debug(f"Total data to encrypt: {total_size} bytes")
        
        # Encrypt everything with file_size-based key
        encrypted_data = bytearray()
        i_size = total_size
        
        for byte in data_to_encrypt:
            key = (i_size % 256)
            encrypted_data.append(byte ^ key)
            i_size -= 1
        
        if self.debug:
            log.debug(f"Encrypted size: {len(encrypted_data)} bytes")
            log.debug(f"First 32 bytes (hex): {' '.join(f'{b:02x}' for b in encrypted_data[:32])}")
        
        return bytes(encrypted_data)
    
    def save_pkt_file_debug(self, output_path, format_type='default'):
        """
        Save .pkt file with debugging info.
        
        Args:
            output_path: Where to save
            format_type: 'default' (our format) or 'ptexplorer'
        """
        try:
            if self.debug:
                log.info(f"Generating .pkt file: {output_path}")
                log.info(f"Format: {format_type}")
            
            # Generate XML structure
            self.build_xml_structure()
            
            if self.debug:
                log.debug(f"XML generated, size: {len(self.xml_content)} bytes")
            
            # Encrypt and compress based on format
            if format_type == 'ptexplorer':
                binary_data = self.encrypt_and_compress_ptexplorer_style(self.xml_content)
            else:
                binary_data = self.encrypt_and_compress_debug(self.xml_content)
            
            # Write binary file
            with open(output_path, 'wb') as f:
                f.write(binary_data)
            
            if self.debug:
                log.info(f"✓ File saved: {output_path} ({len(binary_data)} bytes)")
            
            return True
        except Exception as e:
            log.error(f"Error saving .pkt file: {e}")
            return False
    
    def validate_file(self, filepath):
        """Validate a generated .pkt file."""
        try:
            from pt_file_inspector import PTFileInspector
            
            inspector = PTFileInspector(filepath)
            info = inspector.get_file_info()
            
            log.info("=== File Validation ===")
            log.info(f"File: {info['filepath']}")
            log.info(f"Size: {info['filesize']} bytes")
            log.info(f"Header value: {info['header_value']}")
            log.info(f"Payload size: {info['payload_size']}")
            
            # Try to decrypt
            xml_content = inspector.decrypt_and_decompress()
            if xml_content:
                log.info("✓ Decryption successful")
                
                # Validate XML
                valid, result = inspector.validate_xml()
                if valid:
                    log.info("✓ XML valid")
                    log.info(f"  {result}")
                else:
                    log.warning(f"✗ XML invalid: {result}")
            else:
                log.error("✗ Decryption failed")
            
            return True
        except Exception as e:
            log.error(f"Validation failed: {e}")
            return False


class PTFormatTester:
    """Test different format variants."""
    
    @staticmethod
    def test_all_variants(topology_data, output_dir='./format_tests'):
        """Test all known format variants."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        log.info("=== Testing All Format Variants ===")
        
        variants = [
            ('default', 'Our implementation (header + XOR payload)'),
            ('ptexplorer', 'ptexplorer style (all XOR with file size)'),
        ]
        
        for variant_name, description in variants:
            log.info(f"\nVariant: {variant_name}")
            log.info(f"Description: {description}")
            
            builder = EnhancedPTFileBuilder(topology_data, debug=True)
            output_file = os.path.join(output_dir, f'test_{variant_name}.pkt')
            
            builder.save_pkt_file_debug(output_file, format_type=variant_name)
            builder.validate_file(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='Enhanced Packet Tracer .pkt file builder with debugging'
    )
    
    parser.add_argument('topology', help='Topology file (YAML/JSON/XML)')
    parser.add_argument('-o', '--output', required=True, help='Output .pkt file')
    parser.add_argument('-f', '--format', choices=['default', 'ptexplorer'], 
                       default='default', help='Format variant to use')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('-v', '--validate', action='store_true', help='Validate output')
    parser.add_argument('--test-all', action='store_true', help='Test all format variants')
    
    args = parser.parse_args()
    
    # Load topology
    sys.path.insert(0, 'Automation')
    from format_parser import parse_file
    
    try:
        topology = parse_file(args.topology)
    except Exception as e:
        log.error(f"Failed to load topology: {e}")
        return 1
    
    if args.test_all:
        PTFormatTester.test_all_variants(topology)
    else:
        # Generate single file
        builder = EnhancedPTFileBuilder(topology, debug=args.debug)
        builder.save_pkt_file_debug(args.output, format_type=args.format)
        
        # Validate if requested
        if args.validate:
            builder.validate_file(args.output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
