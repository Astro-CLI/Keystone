#!/usr/bin/env python3
"""
Comprehensive Packet Tracer .pkt File Debugger

Systematically investigates why generated .pkt files are rejected by PT 8.2.2
Tests all hypotheses about:
- File signature/magic bytes
- Checksums & validation
- XML structure requirements
- ZLIB compression details
- XOR encryption details
"""

import struct
import zlib
import binascii
import sys
import os
import hashlib
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from pt_file_builder import PTFileBuilder


class PTDebugger:
    """Debug Packet Tracer file format issues."""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = None
        self.load_file()
    
    def load_file(self):
        """Load binary data from .pkt file."""
        with open(self.filepath, 'rb') as f:
            self.data = f.read()
    
    def analyze_signature(self):
        """Analyze file signature/magic bytes."""
        print("\n" + "="*80)
        print("HYPOTHESIS 1: FILE SIGNATURE / MAGIC BYTES")
        print("="*80)
        
        print(f"\nFile size: {len(self.data)} bytes")
        print(f"First 16 bytes (hex): {binascii.hexlify(self.data[:16]).decode()}")
        print(f"First 16 bytes (ascii): {repr(self.data[:16])}")
        
        # Extract header
        if len(self.data) >= 4:
            header = struct.unpack('>I', self.data[:4])[0]
            print(f"\nHeader (big-endian): {header} (0x{header:08x})")
            print(f"Header (little-endian): {struct.unpack('<I', self.data[:4])[0]}")
            
            # Try different interpretations
            print("\nAlternative header interpretations:")
            print(f"  - As 4 bytes: {list(self.data[:4])}")
            print(f"  - As string (utf-8): {repr(self.data[:4].decode('latin-1'))}")
            
            # Check if header seems reasonable
            payload_size = len(self.data) - 4
            print(f"\nPayload size: {payload_size} bytes")
            print(f"Header claims uncompressed size: {header}")
            print(f"Ratio: {payload_size / header if header > 0 else 'N/A':.2f} (typical zlib ratio: 0.1-0.9)")
        
        # Check for known signatures
        print("\nChecking for known magic bytes...")
        possible_sigs = {
            b'PK\x03\x04': 'ZIP file',
            b'\x78\x9c': 'zlib stream (no wrapper)',
            b'\x78\x01': 'zlib stream (no compression)',
            b'\x1f\x8b': 'GZIP stream',
            b'<?xml': 'XML document (unencrypted)',
            b'\x78\xda': 'zlib stream (default compression)',
        }
        
        for sig, desc in possible_sigs.items():
            if self.data.startswith(sig):
                print(f"  ✓ Found: {desc}")
            if self.data[4:].startswith(sig):
                print(f"  ✓ Found (after header): {desc}")
    
    def test_xor_variations(self):
        """Test different XOR key calculations."""
        print("\n" + "="*80)
        print("HYPOTHESIS 5: XOR ENCRYPTION KEY CALCULATION")
        print("="*80)
        
        if len(self.data) < 4:
            print("File too small")
            return
        
        header = struct.unpack('>I', self.data[:4])[0]
        payload = self.data[4:]
        
        print(f"\nUncompressed size: {header}")
        print(f"Payload size: {len(payload)}")
        
        # Test different key variations
        variations = [
            ("Original: key = (size - i) & 0xFF", lambda i, size: (size - i) & 0xFF),
            ("Alternative: key = (size - i) % 256", lambda i, size: (size - i) % 256),
            ("No masking: key = size - i", lambda i, size: size - i),
            ("Reversed: key = (i + 1) & 0xFF", lambda i, size: (i + 1) & 0xFF),
            ("Full size: key = size - i (no & 0xFF)", lambda i, size: (size - i) if (size - i) > 0 else 0),
            ("Modulo 256: key = (size - i - 1) % 256", lambda i, size: (size - i - 1) % 256),
        ]
        
        for desc, key_func in variations:
            try:
                decrypted = bytearray()
                for i, byte in enumerate(payload):
                    key = key_func(i, header)
                    decrypted.append(byte ^ key)
                
                # Try to decompress
                try:
                    xml = zlib.decompress(bytes(decrypted))
                    status = "✓ SUCCESS"
                    xml_preview = xml[:100].decode('utf-8', errors='ignore')
                except:
                    status = "✗ Failed decompression"
                    xml_preview = ""
                
                print(f"\n{desc}")
                print(f"  Result: {status}")
                if xml_preview:
                    print(f"  Preview: {xml_preview}...")
            except Exception as e:
                print(f"\n{desc}")
                print(f"  Error: {e}")
    
    def test_zlib_variations(self):
        """Test different zlib compression approaches."""
        print("\n" + "="*80)
        print("HYPOTHESIS 4: ZLIB COMPRESSION DETAILS")
        print("="*80)
        
        if len(self.data) < 4:
            print("File too small")
            return
        
        header = struct.unpack('>I', self.data[:4])[0]
        payload = self.data[4:]
        
        # First, decrypt with original method
        decrypted = bytearray()
        for i, byte in enumerate(payload):
            key = (header - i) & 0xFF
            decrypted.append(byte ^ key)
        
        print(f"\nPayload (first 20 bytes, hex): {binascii.hexlify(payload[:20]).decode()}")
        print(f"Decrypted (first 20 bytes, hex): {binascii.hexlify(decrypted[:20]).decode()}")
        
        # Check zlib magic bytes
        print(f"\nFirst two bytes of decrypted data: {binascii.hexlify(bytes(decrypted[:2])).decode()}")
        
        zlib_headers = {
            b'\x78\x01': 'No compression',
            b'\x78\x5e': 'Fast compression',
            b'\x78\x9c': 'Default compression',
            b'\x78\xda': 'Best compression',
            b'\x78\x20': 'Raw deflate',
        }
        
        for header_bytes, desc in zlib_headers.items():
            if bytes(decrypted[:2]) == header_bytes:
                print(f"  ✓ Detected: {desc} ({binascii.hexlify(header_bytes).decode()})")
        
        # Try raw deflate (without zlib wrapper)
        print("\nTrying raw deflate decompression...")
        try:
            xml = zlib.decompress(bytes(decrypted), -zlib.MAX_WBITS)
            print(f"  ✓ Raw deflate works!")
            print(f"  First 100 chars: {xml[:100].decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"  ✗ Raw deflate failed: {e}")
        
        # Try regular zlib
        print("\nTrying regular zlib decompression...")
        try:
            xml = zlib.decompress(bytes(decrypted))
            print(f"  ✓ Regular zlib works!")
            print(f"  First 100 chars: {xml[:100].decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"  ✗ Regular zlib failed: {e}")
    
    def check_checksums(self):
        """Check for possible checksums/validation."""
        print("\n" + "="*80)
        print("HYPOTHESIS 2: CHECKSUMS & VALIDATION")
        print("="*80)
        
        if len(self.data) < 4:
            print("File too small")
            return
        
        header = struct.unpack('>I', self.data[:4])[0]
        payload = self.data[4:]
        
        print(f"\nFile size: {len(self.data)}")
        print(f"Header value: {header}")
        print(f"Payload size: {len(payload)}")
        
        # Look for checksum patterns in header or trailer
        print("\nChecking last bytes of file for possible checksums...")
        print(f"Last 16 bytes (hex): {binascii.hexlify(self.data[-16:]).decode()}")
        
        # Try to decrypt and look for patterns
        decrypted = bytearray()
        for i, byte in enumerate(payload):
            key = (header - i) & 0xFF
            decrypted.append(byte ^ key)
        
        # Check last bytes
        print(f"Last 16 bytes of decrypted (hex): {binascii.hexlify(bytes(decrypted[-16:])).decode()}")
        
        # Calculate various checksums of the original data
        print("\nChecksums of header+payload:")
        print(f"  CRC32: {binascii.hexlify(struct.pack('>I', zlib.crc32(self.data) & 0xffffffff)).decode()}")
        print(f"  MD5: {hashlib.md5(self.data).hexdigest()[:8]}")
        
        print("\nChecksums of unencrypted/uncompressed data:")
        try:
            decrypted_data = bytearray()
            for i, byte in enumerate(payload):
                key = (header - i) & 0xFF
                decrypted_data.append(byte ^ key)
            
            xml = zlib.decompress(bytes(decrypted_data))
            print(f"  CRC32 of XML: {binascii.hexlify(struct.pack('>I', zlib.crc32(xml) & 0xffffffff)).decode()}")
            print(f"  MD5 of XML: {hashlib.md5(xml).hexdigest()[:8]}")
        except:
            pass
    
    def analyze_xml_structure(self):
        """Analyze extracted XML structure."""
        print("\n" + "="*80)
        print("HYPOTHESIS 3: XML STRUCTURE REQUIREMENTS")
        print("="*80)
        
        # Decrypt and decompress
        try:
            header = struct.unpack('>I', self.data[:4])[0]
            payload = self.data[4:]
            
            decrypted = bytearray()
            for i, byte in enumerate(payload):
                key = (header - i) & 0xFF
                decrypted.append(byte ^ key)
            
            xml_bytes = zlib.decompress(bytes(decrypted))
            xml_str = xml_bytes.decode('utf-8')
            
            print("\nExtracted XML (first 500 chars):")
            print(xml_str[:500])
            
            # Parse and check structure
            import xml.etree.ElementTree as ET
            try:
                root = ET.fromstring(xml_str)
                print(f"\n✓ Valid XML found!")
                print(f"  Root tag: {root.tag}")
                
                # Check version
                version = root.get('version', 'MISSING')
                build = root.get('build', 'MISSING')
                print(f"  Version: {version}")
                print(f"  Build: {build}")
                
                # Check required elements
                required_elements = ['Network', 'ObjectGroup', 'ConnectionGroup', 'Device']
                for elem in required_elements:
                    found = root.find(f'.//{elem}')
                    status = "✓" if found is not None else "✗"
                    print(f"  {status} {elem}: {found is not None}")
                
                # Count devices
                devices = root.findall('.//Device')
                print(f"\n  Device count: {len(devices)}")
                for i, dev in enumerate(devices[:3]):
                    print(f"    Device {i+1}: {dev.get('name', 'unnamed')} (type: {dev.get('type', 'unknown')})")
                
            except Exception as e:
                print(f"\n✗ XML parsing error: {e}")
        
        except Exception as e:
            print(f"Error extracting XML: {e}")
    
    def test_byte_order(self):
        """Test different byte order interpretations."""
        print("\n" + "="*80)
        print("HYPOTHESIS: BYTE ORDER / ENDIANNESS")
        print("="*80)
        
        if len(self.data) < 4:
            print("File too small")
            return
        
        print(f"\nFirst 4 bytes (raw): {list(self.data[:4])}")
        
        # Big-endian
        be = struct.unpack('>I', self.data[:4])[0]
        print(f"Big-endian (>I): {be} (0x{be:08x})")
        
        # Little-endian
        le = struct.unpack('<I', self.data[:4])[0]
        print(f"Little-endian (<I): {le} (0x{le:08x})")
        
        # Try each as payload size
        payload_actual = len(self.data) - 4
        print(f"\nActual payload size: {payload_actual}")
        print(f"Big-endian header / payload ratio: {payload_actual / be if be > 0 else 'inf':.3f}")
        print(f"Little-endian header / payload ratio: {payload_actual / le if le > 0 else 'inf':.3f}")
        
        # Reasonable ratio for compressed data is 0.1-0.9
        print("\nReasable ratios for zlib compression: 0.1-0.9")
    
    def generate_report(self):
        """Generate complete debug report."""
        print("\n" + "="*80)
        print("PACKET TRACER .PKT FILE DEBUG REPORT")
        print("="*80)
        print(f"File: {self.filepath}")
        print(f"Size: {len(self.data)} bytes")
        
        self.analyze_signature()
        self.test_byte_order()
        self.check_checksums()
        self.analyze_xml_structure()
        self.test_zlib_variations()
        self.test_xor_variations()
        
        print("\n" + "="*80)
        print("NEXT STEPS")
        print("="*80)
        print("""
1. Check if any XOR variation worked (not just original)
2. Compare with ptexplorer source if available
3. Look for PT version-specific differences in 8.2.2
4. Test if XML structure needs additional elements
5. Try creating minimal valid .pkt with known-good data
6. Compare generated files with sample PT files byte-by-byte
        """)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Debug Packet Tracer .pkt file format issues'
    )
    parser.add_argument('pkt_file', help='Path to .pkt file to analyze')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pkt_file):
        print(f"Error: File not found: {args.pkt_file}")
        sys.exit(1)
    
    debugger = PTDebugger(args.pkt_file)
    debugger.generate_report()


if __name__ == '__main__':
    main()
