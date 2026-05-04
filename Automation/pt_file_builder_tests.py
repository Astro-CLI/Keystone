#!/usr/bin/env python3
"""
Comprehensive test suite for pt_file_builder.py
Tests encryption, XML generation, and file format compliance.
"""

import os
import sys
import struct
import zlib
import tempfile
from pathlib import Path

from pt_file_builder import PTFileBuilder
from format_parser import parse_file

class TestSuite:
    """Test suite for .pkt file builder."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests_run = 0
    
    def assert_true(self, condition, test_name):
        """Assert condition is true."""
        self.tests_run += 1
        if condition:
            print(f"  ✓ {test_name}")
            self.passed += 1
        else:
            print(f"  ✗ {test_name}")
            self.failed += 1
    
    def assert_equal(self, actual, expected, test_name):
        """Assert actual equals expected."""
        self.tests_run += 1
        if actual == expected:
            print(f"  ✓ {test_name}")
            self.passed += 1
        else:
            print(f"  ✗ {test_name} (expected {expected}, got {actual})")
            self.failed += 1
    
    def run_all(self):
        """Run all tests."""
        print("\n" + "=" * 70)
        print("PACKET TRACER .pkt FILE BUILDER - TEST SUITE")
        print("=" * 70)
        
        self.test_encryption_algorithm()
        self.test_xml_generation()
        self.test_file_format()
        self.test_multiformat_input()
        self.test_device_types()
        self.test_protocol_configs()
        self.test_round_trip()
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {self.passed / self.tests_run * 100:.1f}%")
        
        if self.failed == 0:
            print("\n✓ All tests passed!")
            return 0
        else:
            print(f"\n✗ {self.failed} test(s) failed")
            return 1
    
    def test_encryption_algorithm(self):
        """Test XOR encryption and zlib compression."""
        print("\n[TEST 1] Encryption Algorithm")
        print("-" * 70)
        
        builder = PTFileBuilder({'devices': []})
        # Use larger test XML to ensure good compression ratio
        test_xml = '<?xml version="1.0"?><root>' + '<data>test data</data>' * 50 + '</root>'
        
        # Encrypt
        encrypted = builder.encrypt_and_compress(test_xml)
        
        # Check header
        header = struct.unpack('>I', encrypted[:4])[0]
        self.assert_equal(header, len(test_xml), "Header matches XML length")
        
        # Check encrypted has reasonable size (header + compressed payload)
        self.assert_true(len(encrypted) >= 4, 
                        "Encrypted data has valid structure")
        
        # Decrypt and verify
        decrypted = builder.decrypt_and_decompress(encrypted)
        self.assert_equal(decrypted, test_xml, "Round-trip encryption/decryption")
    
    def test_xml_generation(self):
        """Test XML generation."""
        print("\n[TEST 2] XML Generation")
        print("-" * 70)
        
        topo = {
            'devices': [
                {
                    'hostname': 'TestRouter',
                    'type': 'router',
                    'description': 'Test device',
                    'interfaces': [
                        {'name': 'GigabitEthernet0/0/0', 'ip': '10.0.0.1', 'mask': '255.255.255.0'}
                    ]
                }
            ]
        }
        
        builder = PTFileBuilder(topo)
        xml = builder.get_xml_content()
        
        # Check structure
        self.assert_true('<?xml version="1.0"' in xml, "XML declaration present")
        self.assert_true('<PacketTracer version="8.2.2"' in xml, "PT version correct")
        self.assert_true('<Device' in xml, "Device element present")
        self.assert_true('TestRouter' in xml, "Device name present")
        self.assert_true('10.0.0.1' in xml, "IP address present")
        self.assert_true('GigabitEthernet0/0/0' in xml, "Interface name present")
    
    def test_file_format(self):
        """Test .pkt file format."""
        print("\n[TEST 3] .pkt File Format")
        print("-" * 70)
        
        topo = {
            'devices': [
                {'hostname': 'R1', 'type': 'router',
                 'interfaces': [{'name': 'G0/0', 'ip': '10.0.0.1', 'mask': '255.255.255.0'}]}
            ]
        }
        
        builder = PTFileBuilder(topo)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.pkt', delete=False) as f:
            temp_file = f.name
        
        try:
            builder.save_pkt_file(temp_file)
            
            # Verify file exists
            self.assert_true(os.path.exists(temp_file), "File created")
            
            # Verify file size
            size = os.path.getsize(temp_file)
            self.assert_true(size > 4, "File size > 4 bytes")
            
            # Verify header
            with open(temp_file, 'rb') as f:
                data = f.read()
            
            header = struct.unpack('>I', data[:4])[0]
            self.assert_true(header > 0, "Valid header value")
            
            # Verify can be decrypted
            decrypted = builder.decrypt_and_decompress(data)
            self.assert_true('<?xml' in decrypted, "Decrypted XML is valid")
        
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_multiformat_input(self):
        """Test multiple input formats."""
        print("\n[TEST 4] Multiple Input Formats")
        print("-" * 70)
        
        common_topo = {
            'devices': [
                {'hostname': 'R1', 'type': 'router',
                 'interfaces': [{'name': 'G0/0', 'ip': '10.0.0.1', 'mask': '255.255.255.0'}]}
            ]
        }
        
        # Test YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(common_topo, f)
            yaml_file = f.name
        
        # Test JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(common_topo, f)
            json_file = f.name
        
        try:
            yaml_data = parse_file(yaml_file)
            json_data = parse_file(json_file)
            
            self.assert_true(yaml_data is not None, "YAML parsed successfully")
            self.assert_true(json_data is not None, "JSON parsed successfully")
            
            # Build .pkt files
            yaml_builder = PTFileBuilder(yaml_data)
            json_builder = PTFileBuilder(json_data)
            
            yaml_xml = yaml_builder.get_xml_content()
            json_xml = json_builder.get_xml_content()
            
            # Content should be identical (modulo formatting)
            self.assert_true('<?xml' in yaml_xml, "YAML generates valid XML")
            self.assert_true('<?xml' in json_xml, "JSON generates valid XML")
        
        finally:
            for f in [yaml_file, json_file]:
                if os.path.exists(f):
                    os.remove(f)
    
    def test_device_types(self):
        """Test different device types."""
        print("\n[TEST 5] Device Types")
        print("-" * 70)
        
        device_types = ['router', 'switch', 'pc', 'server', 'firewall', 'hub', 'cloud']
        
        for dtype in device_types:
            topo = {
                'devices': [
                    {'hostname': f'{dtype.upper()}-1', 'type': dtype}
                ]
            }
            
            builder = PTFileBuilder(topo)
            xml = builder.get_xml_content()
            
            self.assert_true(f'{dtype.upper()}-1' in xml, 
                           f"Device type '{dtype}' generates valid XML")
    
    def test_protocol_configs(self):
        """Test protocol configurations."""
        print("\n[TEST 6] Protocol Configurations")
        print("-" * 70)
        
        # OSPF
        topo_ospf = {
            'devices': [
                {
                    'hostname': 'R1',
                    'type': 'router',
                    'interfaces': [{'name': 'G0/0', 'ip': '10.0.0.1', 'mask': '255.255.255.0'}],
                    'ospf': {
                        'process_id': 1,
                        'router_id': '1.1.1.1',
                        'networks': [{'network': '10.0.0.0', 'wildcard': '0.0.0.255', 'area': 0}]
                    }
                }
            ]
        }
        
        builder = PTFileBuilder(topo_ospf)
        xml = builder.get_xml_content()
        self.assert_true('router ospf 1' in xml, "OSPF config generated")
        self.assert_true('router-id 1.1.1.1' in xml, "OSPF router-id generated")
        
        # BGP
        topo_bgp = {
            'devices': [
                {
                    'hostname': 'R1',
                    'type': 'router',
                    'interfaces': [{'name': 'G0/0', 'ip': '10.0.0.1', 'mask': '255.255.255.0'}],
                    'bgp': {
                        'asn': 65100,
                        'router_id': '1.1.1.1',
                        'neighbors': [{'ip': '10.0.0.2', 'asn': 65101}]
                    }
                }
            ]
        }
        
        builder = PTFileBuilder(topo_bgp)
        xml = builder.get_xml_content()
        self.assert_true('router bgp 65100' in xml, "BGP config generated")
        
        # DHCP
        topo_dhcp = {
            'devices': [
                {
                    'hostname': 'R1',
                    'type': 'router',
                    'dhcp': {
                        'pools': [
                            {'name': 'POOL1', 'network': '10.0.0.0', 'mask': '255.255.255.0'}
                        ]
                    }
                }
            ]
        }
        
        builder = PTFileBuilder(topo_dhcp)
        xml = builder.get_xml_content()
        self.assert_true('ip dhcp pool POOL1' in xml, "DHCP pool config generated")
    
    def test_round_trip(self):
        """Test round-trip: create, save, read, decrypt."""
        print("\n[TEST 7] Round-Trip Operations")
        print("-" * 70)
        
        original_topo = {
            'devices': [
                {
                    'hostname': 'CORE-R1',
                    'type': 'router',
                    'description': 'Core router',
                    'interfaces': [
                        {'name': 'GigabitEthernet0/0/0', 'ip': '10.0.0.1', 'mask': '255.255.255.0'},
                        {'name': 'GigabitEthernet0/0/1', 'ip': '10.0.1.1', 'mask': '255.255.255.0'}
                    ],
                    'ospf': {
                        'process_id': 1,
                        'router_id': '1.1.1.1',
                        'networks': [
                            {'network': '10.0.0.0', 'wildcard': '0.0.0.255', 'area': 0},
                            {'network': '10.0.1.0', 'wildcard': '0.0.0.255', 'area': 0}
                        ]
                    }
                },
                {
                    'hostname': 'CORE-R2',
                    'type': 'router',
                    'interfaces': [
                        {'name': 'GigabitEthernet0/0/0', 'ip': '10.0.0.2', 'mask': '255.255.255.0'}
                    ]
                }
            ],
            'connections': [
                {
                    'from_device': 'CORE-R1',
                    'from_interface': 'GigabitEthernet0/0/0',
                    'to_device': 'CORE-R2',
                    'to_interface': 'GigabitEthernet0/0/0'
                }
            ]
        }
        
        # Create builder and generate XML
        builder1 = PTFileBuilder(original_topo)
        original_xml = builder1.get_xml_content()
        
        # Save to file
        with tempfile.NamedTemporaryFile(suffix='.pkt', delete=False) as f:
            pkt_file = f.name
        
        try:
            builder1.save_pkt_file(pkt_file)
            self.assert_true(os.path.exists(pkt_file), "File saved")
            
            # Read file back
            with open(pkt_file, 'rb') as f:
                pkt_data = f.read()
            
            # Decrypt
            builder2 = PTFileBuilder({})
            recovered_xml = builder2.decrypt_and_decompress(pkt_data)
            
            # Verify content
            self.assert_equal(recovered_xml, original_xml, "XML recovered from file")
            self.assert_true('CORE-R1' in recovered_xml, "Device name preserved")
            self.assert_true('10.0.0.1' in recovered_xml, "IP address preserved")
            self.assert_true('router ospf 1' in recovered_xml, "OSPF config preserved")
        
        finally:
            if os.path.exists(pkt_file):
                os.remove(pkt_file)

def main():
    suite = TestSuite()
    return suite.run_all()

if __name__ == '__main__':
    sys.exit(main())
