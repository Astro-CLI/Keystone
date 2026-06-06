import sys
import os
import subprocess
import tempfile
import yaml
import json
import re
import html
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QFileDialog, QSplitter,
    QFrame, QMessageBox, QScrollArea, QLineEdit, QSizePolicy,
    QStackedWidget
)
from PyQt6.QtGui import QFont, QColor, QPalette, QGuiApplication, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QTimer, QSize, qInstallMessageHandler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))
from pt_builder_gen import generate_pt_builder_script
from pt_analyzer_helper import parse_analyzer_output

# Load pt_analyzer.js content for the Extract workflow
_ANALYZER_JS_PATH = os.path.join(os.path.dirname(__file__), 'scripts', 'pt_analyzer.js')
ANALYZER_JS = ""
if os.path.exists(_ANALYZER_JS_PATH):
    with open(_ANALYZER_JS_PATH) as f:
        ANALYZER_JS = f.read()

# ── Cyber-Obsidian Design Tokens (matching orchestrator.html/app.css) ──
C = {
    "bg_dark": "#0a0b10",
    "bg_surface": "#11121a",
    "bg_surface_light": "#1b1d2a",
    "bg_input": "#141521",
    "bg_terminal": "#07080c",
    "border": "#232637",
    "border_hover": "#353952",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_muted": "#57657a",
    "primary": "#6366f1",
    "primary_hover": "#4f46e5",
    "primary_glow": "rgba(99, 102, 241, 0.18)",
    "success": "#10b981",
    "error": "#ef4444",
    "warning": "#f59e0b",
    # Category colors
    "cat_routing": "#3b82f6",
    "cat_security": "#ec4899",
    "cat_services": "#10b981",
    "cat_utilities": "#f59e0b",
}

CAT_COLORS = {
    "WORKFLOWS": "#a855f7",
    "ROUTING": C["cat_routing"],
    "SECURITY": C["cat_security"],
    "SERVICES": C["cat_services"],
    "UTILITIES": C["cat_utilities"],
}

CAT_ICONS = {
    "WORKFLOWS": "\u2194",
    "ROUTING": "\u25C9",
    "SECURITY": "\u26E8",
    "SERVICES": "\u2699",
    "UTILITIES": "\u229E",
}

CAT_ORDER = ["WORKFLOWS", "ROUTING", "SECURITY", "SERVICES", "UTILITIES"]

TOOL_INFO = {
    "VLAN Weaver":       {"script": "vlan_weaver.py",     "cat": "UTILITIES", "icon": "\u25A7", "short": "VLAN", "desc": "Layer 2 Segmentation with Dual-Stack SVIs"},
    "OSPF Pathmaker":    {"script": "ospf_pathmaker.py",  "cat": "ROUTING",   "icon": "\u25C9", "short": "OSPF", "desc": "Dual-Stack OSPFv2/v3 with Interface Config"},
    "ASA Shield":        {"script": "asa_shield.py",      "cat": "SECURITY",  "icon": "\u25C6", "short": "ASA",  "desc": "Next-Gen Firewall with IPv4/IPv6 Objects"},
    "BGP Conductor":     {"script": "bgp_conductor.py",   "cat": "ROUTING",   "icon": "\u25C8", "short": "BGP",  "desc": "Dual-Stack BGP with Address Families"},
    "DHCP Allocator":    {"script": "dhcp_allocator.py",  "cat": "SERVICES",  "icon": "\u25D1", "short": "DHCP", "desc": "DHCPv4 Pools and DHCPv6 Prefix Delegation"},
    "EIGRP Catalyst":    {"script": "eigrp_catalyst.py",  "cat": "ROUTING",   "icon": "\u25B3", "short": "EIGRP","desc": "Dual-Stack EIGRP Named Mode"},
    "HSRP Sentinel":     {"script": "hsrp_sentinel.py",   "cat": "SERVICES",  "icon": "\u25CB", "short": "HSRP", "desc": "First-Hop Redundancy with Dual-Stack VIPs"},
    "IP Architect":      {"script": "ip_architect.py",    "cat": "UTILITIES", "icon": "\u25A3", "short": "IP",   "desc": "Random IP / Subnet Generation (IPv4 & IPv6)"},
    "NAT Portal":        {"script": "nat_portal.py",      "cat": "SECURITY",  "icon": "\u25B7", "short": "NAT",  "desc": "Static/Dynamic NAT with IPv6 Support"},
    "SSH Locksmith":     {"script": "ssh_locksmith.py",   "cat": "SECURITY",  "icon": "\u25A1", "short": "SSH",  "desc": "SSH Hardening with IPv6 VTY ACLs"},
    "Static Anchor":     {"script": "static_anchor.py",   "cat": "ROUTING",   "icon": "\u25C7", "short": "STAT", "desc": "IPv4 and IPv6 Static Routes"},
    "CIDR Architect":    {"script": "cidr_architect.py",  "cat": "UTILITIES", "icon": "\u25A8", "short": "CIDR", "desc": "VLSM Subnet Planner (IPv4 & IPv6)"},
    "Full Topology":     {"script": "full_topology.py",   "cat": "UTILITIES", "icon": "\u229E", "short": "NET",  "desc": "Multi-Device Network Definition"},
    "Extract from PT":   {"script": "",                   "cat": "WORKFLOWS", "icon": "\u2190", "short": "EXT",  "desc": "Import running configs from Packet Tracer -> YAML"},
}

TEMPLATES = {
    "VLAN Weaver": (
        "# VLAN Weaver: Layer 2 Segmentation (Dual-Stack)\n"
        "- hostname: DSW-1\n"
        "  vlans:\n"
        "    - name: Management\n"
        "      id: 10\n"
        "      ipv6: \"2001:db8:10::1/64\"\n"
        "    - name: Sales\n"
        "      id: 20\n"
        "    - name: Guest\n"
        "      id: 30\n"
    ),
    "OSPF Pathmaker": (
        "# OSPF Pathmaker: Dual-Stack Routing\n"
        "- hostname: Core-R1\n"
        "  router_id: 1.1.1.1\n"
        "  process_id: 1\n"
        "  ipv6_process_id: 1\n"
        "  use_interface_config: true\n"
        "  interfaces:\n"
        "    - name: GigabitEthernet0/0\n"
        "      ip_address: 192.168.1.1\n"
        "      subnet_mask: 255.255.255.0\n"
        "      ipv6_address: \"2001:db8:1::1/64\"\n"
        "      area: 0\n"
        "      ipv6_area: 0\n"
        "    - name: GigabitEthernet0/1\n"
        "      ip_address: 10.0.0.1\n"
        "      subnet_mask: 255.255.255.252\n"
        "      ipv6_address: \"2001:db8:0:1::1/64\"\n"
        "      area: 0\n"
        "      ipv6_area: 0\n"
    ),
    "ASA Shield": (
        "# ASA Shield: Next-Gen Firewall\n"
        "- hostname: ASA-FW-01\n"
        "  interfaces:\n"
        "    - name: GigabitEthernet0/0\n"
        "      nameif: inside\n"
        "      security_level: 100\n"
        "      ip: 192.168.1.1\n"
        "      mask: 255.255.255.0\n"
        "      ipv6: \"2001:db8:1::1\"\n"
        "  objects:\n"
        "    - name: INTERNAL_V4\n"
        "      subnet: 192.168.1.0\n"
        "      mask: 255.255.255.0\n"
        "    - name: INTERNAL_V6\n"
        "      ipv6_subnet: \"2001:db8:1::/64\"\n"
        "  nats:\n"
        "    - obj_name: INTERNAL_V4\n"
        "      type: dynamic\n"
        "      translated_interface: outside\n"
        "  acls:\n"
        "    - access_list: OUTSIDE_IN\n"
        "      action: permit\n"
        "      protocol: tcp\n"
        "      source: any\n"
        "      destination: any\n"
        "      service: eq 443\n"
        "  access_groups:\n"
        "    OUTSIDE_IN: outside\n"
    ),
    "BGP Conductor": (
        "# BGP Conductor: Dual-Stack Peering\n"
        "- hostname: Edge-R1\n"
        "  as_number: 65001\n"
        "  router_id: 1.1.1.1\n"
        "  neighbors:\n"
        "    - ip: 10.0.0.2\n"
        "      remote_as: 65002\n"
        "      description: ISP1_V4\n"
        "    - ip: \"2001:db8:0:1::2\"\n"
        "      remote_as: 65002\n"
        "      description: ISP1_V6\n"
        "  networks:\n"
        "    - network: 192.168.1.0\n"
        "      mask: 255.255.255.0\n"
        "    - network: \"2001:db8:1::\"\n"
        "      mask: 64\n"
    ),
    "DHCP Allocator": (
        "# DHCP Allocator: Dual-Stack Pools\n"
        "- hostname: Core-Switch\n"
        "  excluded:\n"
        "    - start: 192.168.10.1\n"
        "      end: 192.168.10.10\n"
        "  pools:\n"
        "    - name: DATA_POOL\n"
        "      network: 192.168.10.0\n"
        "      mask: 255.255.255.0\n"
        "      gateway: 192.168.10.1\n"
        "      dns: 8.8.8.8\n"
        "  ipv6_pools:\n"
        "    - name: DATA_POOL_V6\n"
        "      prefix: \"2001:db8:10::/64\"\n"
        "      dns: \"2001:db8:20::a\"\n"
    ),
    "EIGRP Catalyst": (
        "# EIGRP Catalyst: Dual-Stack\n"
        "- hostname: R1\n"
        "  as_number: 100\n"
        "  ipv6_as_number: 100\n"
        "  router_id: 1.1.1.1\n"
        "  networks:\n"
        "    - network: 192.168.1.0\n"
        "      mask: 255.255.255.0\n"
        "  interfaces:\n"
        "    - name: GigabitEthernet0/0\n"
        "      ipv6_enabled: true\n"
    ),
    "HSRP Sentinel": (
        "# HSRP Sentinel: High Availability\n"
        "- hostname: Core-R1\n"
        "  interfaces:\n"
        "    - name: VLAN 10\n"
        "      vlan_id: 10\n"
        "      ip: 192.168.1.2\n"
        "      mask: 255.255.255.0\n"
        "      hsrp_ip: 192.168.1.1\n"
        "      ipv6: \"2001:db8:1::2\"\n"
        "      hsrp_ipv6: \"2001:db8:1::1\"\n"
        "      priority: 110\n"
        "      preempt: true\n"
    ),
    "IP Architect": (
        "# IP Architect: Inventory (Dual-Stack)\n"
        "- hostname: Core-R1\n"
        "  interfaces:\n"
        "    - name: Gi0/0\n"
        "      ip: 192.168.1.1\n"
        "      mask: 255.255.255.0\n"
        "      ipv6: \"2001:db8:1::1\"\n"
        "- random_ips:\n"
        "    count: 5\n"
        "    ipv6: false\n"
    ),
    "NAT Portal": (
        "# NAT Portal: IPv4 + IPv6 Mapping\n"
        "- hostname: Gateway-R1\n"
        "  inside_interfaces: [GigabitEthernet0/1]\n"
        "  outside_interfaces: [GigabitEthernet0/0]\n"
        "  static_nats:\n"
        "    - inside_ip: 192.168.1.50\n"
        "      outside_ip: 203.0.113.10\n"
        "  ipv6_nats:\n"
        "    - inside_ip: \"2001:db8:1::50\"\n"
        "      outside_ip: \"2001:db8:ff:f::50\"\n"
    ),
    "SSH Locksmith": (
        "# SSH Locksmith: Hardening (Dual-Stack)\n"
        "- hostname: Core-R1\n"
        "  domain_name: keystone.local\n"
        "  username: admin\n"
        "  password: SecretPassword123\n"
        "  key_size: 2048\n"
        "  ipv6_vty: true\n"
        "  vty_acl_ipv6: \"2001:db8:10::/32\"\n"
    ),
    "Static Anchor": (
        "# Static Anchor: Dual-Stack Routes\n"
        "- hostname: R1\n"
        "  routes:\n"
        "    - network: 0.0.0.0\n"
        "      mask: 0.0.0.0\n"
        "      next_hop: 10.0.0.1\n"
        "    - network: \"::/0\"\n"
        "      mask: 0\n"
        "      next_hop: \"2001:db8::1\"\n"
    ),
    "CIDR Architect": (
        "# CIDR Architect: VLSM (Dual-Stack)\n"
        "- network: 172.16.0.0/16\n"
        "  subnets:\n"
        "    - name: MGMT\n"
        "      size: 50\n"
        "    - name: PROD\n"
        "      size: 500\n"
        "- network: \"fc00:cafe::/48\"\n"
        "  subnets:\n"
        "    - name: MGMT_V6\n"
        "      size: 1\n"
    ),
    "Full Topology": (
        "# Full Topology: Multi-Tier Enterprise Network\n"
        "# Paste your entire network topology here. Generates CLI config for every\n"
        "# device plus a PT-Builder JS script (addDevice, addLink, configureIosDevice).\n"
        "#\n"
        "# Per device: hostname, model, interfaces, vlans, ospf, eigrp, bgp, routes,\n"
        "#   dhcp (pools + ipv6_pools), nat, ssh, domain_name\n"
        "# Per interface: name, ip, mask, ipv6, description, mode, access_vlan,\n"
        "#   trunk_allowed, nameif, security_level, hsrp (group, ip, priority, preempt), dhcp\n"
        "# Links array defines physical connections for PT-Builder output.\n"
        "# This example showcases core / distribution / access layers with BGP, OSPF,\n"
        "# EIGRP, HSRP, static routes, VLANs, SVIs, DHCP, NAT, SSH, and end devices.\n"
        "\n"
        "name: \"Multi-Tier Enterprise Network\"\n"
        "\n"
        "devices:\n"
        "  # ── Core Layer ──────────────────────────────────────────────\n"
        "  - hostname: Core-R1\n"
        "    model: 2911\n"
        "    domain_name: enterprise.local\n"
        "    interfaces:\n"
        "      - name: GigabitEthernet0/0\n"
        "        ip: 10.0.0.1\n"
        "        mask: 255.255.255.252\n"
        "        ipv6: \"2001:db8:ff:1::1/64\"\n"
        "        description: \"P2P to Core-R2\"\n"
        "      - name: GigabitEthernet0/1\n"
        "        ip: 10.0.1.1\n"
        "        mask: 255.255.255.252\n"
        "        ipv6: \"2001:db8:ff:2::1/64\"\n"
        "        description: \"P2P to ASA-FW-01 inside\"\n"
        "      - name: GigabitEthernet0/2\n"
        "        ip: 172.16.0.1\n"
        "        mask: 255.255.255.255\n"
        "        description: \"Loopback0\"\n"
        "      - name: GigabitEthernet1/0\n"
        "        ip: 192.168.10.1\n"
        "        mask: 255.255.255.0\n"
        "        ipv6: \"2001:db8:10::1/64\"\n"
        "        description: \"Management VLAN\"\n"
        "      - name: GigabitEthernet2/0\n"
        "        ip: 203.0.113.1\n"
        "        mask: 255.255.255.252\n"
        "        description: \"WAN to ISP\"\n"
        "    ospf:\n"
        "      process_id: 1\n"
        "      router_id: 1.1.1.1\n"
        "      area: 0\n"
        "    bgp:\n"
        "      as: 65001\n"
        "      router_id: 1.1.1.1\n"
        "      networks:\n"
        "        - network: 192.168.0.0\n"
        "          mask: 255.255.0.0\n"
        "        - network: 172.16.0.0\n"
        "          mask: 255.255.255.0\n"
        "      neighbors:\n"
        "        - ip: 10.0.0.2\n"
        "          remote_as: 65001\n"
        "          update_source: GigabitEthernet0/0\n"
        "          next_hop_self: true\n"
        "        - ip: 203.0.113.2\n"
        "          remote_as: 64515\n"
        "          ebgp_multihop: 2\n"
        "    routes:\n"
        "      - network: 0.0.0.0\n"
        "        mask: 0.0.0.0\n"
        "        next_hop: 203.0.113.2\n"
        "      - network: \"::/0\"\n"
        "        mask: 0\n"
        "        next_hop: \"2001:db8:ff:f::1\"\n"
        "    ssh:\n"
        "      username: netadmin\n"
        "      password: s3cur3P@ss!\n"
        "      key_size: 2048\n"
        "      ipv6_vty: true\n"
        "      vty_acl_ipv6: \"2001:db8:10::/32\"\n"
        "\n"
        "  - hostname: Core-R2\n"
        "    model: 2911\n"
        "    interfaces:\n"
        "      - name: GigabitEthernet0/0\n"
        "        ip: 10.0.0.2\n"
        "        mask: 255.255.255.252\n"
        "        ipv6: \"2001:db8:ff:1::2/64\"\n"
        "        description: \"P2P to Core-R1\"\n"
        "        hsrp:\n"
        "          group: 1\n"
        "          ip: 10.0.0.3\n"
        "          priority: 90\n"
        "      - name: GigabitEthernet0/1\n"
        "        ip: 10.0.2.1\n"
        "        mask: 255.255.255.252\n"
        "        ipv6: \"2001:db8:ff:3::1/64\"\n"
        "        description: \"P2P to ASA-FW-01 dmz\"\n"
        "      - name: GigabitEthernet0/2\n"
        "        ip: 172.16.0.2\n"
        "        mask: 255.255.255.255\n"
        "        description: \"Loopback0\"\n"
        "      - name: GigabitEthernet1/0\n"
        "        ip: 192.168.10.2\n"
        "        mask: 255.255.255.0\n"
        "        ipv6: \"2001:db8:10::2/64\"\n"
        "        description: \"Management VLAN\"\n"
        "        hsrp:\n"
        "          group: 10\n"
        "          ip: 192.168.10.254\n"
        "          priority: 100\n"
        "          preempt: true\n"
        "    ospf:\n"
        "      process_id: 1\n"
        "      router_id: 2.2.2.2\n"
        "      area: 0\n"
        "    bgp:\n"
        "      as: 65001\n"
        "      router_id: 2.2.2.2\n"
        "      neighbors:\n"
        "        - ip: 10.0.0.1\n"
        "          remote_as: 65001\n"
        "          update_source: GigabitEthernet0/0\n"
        "    routes:\n"
        "      - network: 0.0.0.0\n"
        "        mask: 0.0.0.0\n"
        "        next_hop: 10.0.0.1\n"
        "\n"
        "  # ── Distribution Layer ──────────────────────────────────────\n"
        "  - hostname: DSW-1\n"
        "    model: 2960-24TT\n"
        "    vlans:\n"
        "      - id: 10\n"
        "        name: Management\n"
        "        ip: 192.168.10.253\n"
        "        mask: 255.255.255.0\n"
        "        ipv6: \"2001:db8:10::253/64\"\n"
        "      - id: 20\n"
        "        name: Servers\n"
        "        ip: 192.168.20.1\n"
        "        mask: 255.255.255.0\n"
        "        ipv6: \"2001:db8:20::1/64\"\n"
        "      - id: 30\n"
        "        name: Data\n"
        "        ip: 192.168.30.1\n"
        "        mask: 255.255.255.0\n"
        "        ipv6: \"2001:db8:30::1/64\"\n"
        "      - id: 40\n"
        "        name: Voice\n"
        "        ip: 192.168.40.1\n"
        "        mask: 255.255.255.0\n"
        "      - id: 50\n"
        "        name: Guest\n"
        "        ip: 192.168.50.1\n"
        "        mask: 255.255.255.0\n"
        "    interfaces:\n"
        "      - name: GigabitEthernet0/1\n"
        "        ip: 192.168.10.252\n"
        "        mask: 255.255.255.0\n"
        "        description: \"Uplink to Core (SVI transit)\"\n"
        "      - name: GigabitEthernet0/2\n"
        "        mode: trunk\n"
        "        trunk_allowed: \"10,20,30,40,50\"\n"
        "        description: \"Trunk to ASW-1\"\n"
        "    ospf:\n"
        "      process_id: 1\n"
        "      router_id: 3.3.3.3\n"
        "      area: 0\n"
        "    eigrp:\n"
        "      as: 100\n"
        "    dhcp:\n"
        "      pools:\n"
        "        - name: DATA_POOL\n"
        "          network: 192.168.30.0\n"
        "          mask: 255.255.255.0\n"
        "          gateway: 192.168.30.1\n"
        "          dns: 192.168.20.10\n"
        "        - name: VOICE_POOL\n"
        "          network: 192.168.40.0\n"
        "          mask: 255.255.255.0\n"
        "          gateway: 192.168.40.1\n"
        "        - name: GUEST_POOL\n"
        "          network: 192.168.50.0\n"
        "          mask: 255.255.255.0\n"
        "          gateway: 192.168.50.1\n"
        "      ipv6_pools:\n"
        "        - name: DATA_POOL_V6\n"
        "          prefix: \"2001:db8:30::/64\"\n"
        "          dns: \"2001:db8:20::a\"\n"
        "        - name: GUEST_POOL_V6\n"
        "          prefix: \"2001:db8:50::/64\"\n"
        "\n"
        "  - hostname: DSW-2\n"
        "    model: 2960-24TT\n"
        "    vlans:\n"
        "      - id: 10\n"
        "        name: Management\n"
        "        ip: 192.168.10.254\n"
        "        mask: 255.255.255.0\n"
        "        ipv6: \"2001:db8:10::254/64\"\n"
        "      - id: 20\n"
        "        name: Servers\n"
        "        ip: 192.168.20.2\n"
        "        mask: 255.255.255.0\n"
        "        ipv6: \"2001:db8:20::2/64\"\n"
        "      - id: 30\n"
        "        name: Data\n"
        "        ip: 192.168.30.2\n"
        "        mask: 255.255.255.0\n"
        "        ipv6: \"2001:db8:30::2/64\"\n"
        "      - id: 40\n"
        "        name: Voice\n"
        "        ip: 192.168.40.2\n"
        "        mask: 255.255.255.0\n"
        "      - id: 50\n"
        "        name: Guest\n"
        "        ip: 192.168.50.2\n"
        "        mask: 255.255.255.0\n"
        "    interfaces:\n"
        "      - name: GigabitEthernet0/1\n"
        "        ip: 192.168.10.251\n"
        "        mask: 255.255.255.0\n"
        "        description: \"Uplink to Core (SVI transit)\"\n"
        "      - name: GigabitEthernet0/2\n"
        "        mode: trunk\n"
        "        trunk_allowed: \"10,20,30,40,50\"\n"
        "        description: \"Trunk to ASW-2\"\n"
        "    ospf:\n"
        "      process_id: 1\n"
        "      router_id: 4.4.4.4\n"
        "      area: 0\n"
        "    eigrp:\n"
        "      as: 100\n"
        "    dhcp:\n"
        "      pools:\n"
        "        - name: DATA_POOL_2\n"
        "          network: 192.168.31.0\n"
        "          mask: 255.255.255.0\n"
        "          gateway: 192.168.31.1\n"
        "          dns: 192.168.20.10\n"
        "\n"
        "  # ── Access Layer ────────────────────────────────────────────\n"
        "  - hostname: ASW-1\n"
        "    model: 2960-24TT\n"
        "    vlans:\n"
        "      - id: 10\n"
        "        name: Management\n"
        "      - id: 30\n"
        "        name: Data\n"
        "      - id: 40\n"
        "        name: Voice\n"
        "      - id: 50\n"
        "        name: Guest\n"
        "    interfaces:\n"
        "      - name: GigabitEthernet0/1\n"
        "        mode: trunk\n"
        "        trunk_allowed: \"10,30,40,50\"\n"
        "        description: \"Uplink to DSW-1\"\n"
        "      - name: FastEthernet0/1\n"
        "        mode: access\n"
        "        access_vlan: 30\n"
        "        description: \"PC1\"\n"
        "      - name: FastEthernet0/2\n"
        "        mode: access\n"
        "        access_vlan: 30\n"
        "        description: \"PC2\"\n"
        "      - name: FastEthernet0/3\n"
        "        mode: access\n"
        "        access_vlan: 50\n"
        "        description: \"Laptop-1 (Guest)\"\n"
        "\n"
        "  - hostname: ASW-2\n"
        "    model: 2960-24TT\n"
        "    vlans:\n"
        "      - id: 10\n"
        "        name: Management\n"
        "      - id: 20\n"
        "        name: Servers\n"
        "    interfaces:\n"
        "      - name: GigabitEthernet0/1\n"
        "        mode: trunk\n"
        "        trunk_allowed: \"10,20\"\n"
        "        description: \"Uplink to DSW-2\"\n"
        "      - name: FastEthernet0/1\n"
        "        mode: access\n"
        "        access_vlan: 20\n"
        "        description: \"Server-1\"\n"
        "      - name: FastEthernet0/2\n"
        "        mode: access\n"
        "        access_vlan: 20\n"
        "        description: \"Server-2\"\n"
        "\n"
        "  # ── Firewall ────────────────────────────────────────────────\n"
        "  - hostname: ASA-FW-01\n"
        "    model: 5506-X\n"
        "    interfaces:\n"
        "      - name: GigabitEthernet0/0\n"
        "        nameif: inside\n"
        "        security_level: 100\n"
        "        ip: 10.0.1.2\n"
        "        mask: 255.255.255.252\n"
        "        ipv6: \"2001:db8:ff:2::2/64\"\n"
        "        description: \"Inside to Core-R1\"\n"
        "      - name: GigabitEthernet0/1\n"
        "        nameif: dmz\n"
        "        security_level: 50\n"
        "        ip: 10.0.2.2\n"
        "        mask: 255.255.255.252\n"
        "        ipv6: \"2001:db8:ff:3::2/64\"\n"
        "        description: \"DMZ to Core-R2\"\n"
        "      - name: GigabitEthernet0/2\n"
        "        nameif: outside\n"
        "        security_level: 0\n"
        "        ip: 198.51.100.1\n"
        "        mask: 255.255.255.248\n"
        "        description: \"Outside to Internet\"\n"
        "    nat:\n"
        "      - type: dynamic\n"
        "        outside_interface: outside\n"
        "    routes:\n"
        "      - network: 192.168.0.0\n"
        "        mask: 255.255.0.0\n"
        "        next_hop: 10.0.1.1\n"
        "      - network: \"2001:db8::/32\"\n"
        "        mask: 0\n"
        "        next_hop: \"2001:db8:ff:2::1\"\n"
        "    ssh:\n"
        "      username: admin\n"
        "      password: Pa$$w0rd!\n"
        "      key_size: 2048\n"
        "\n"
        "  # ── End Devices ─────────────────────────────────────────────\n"
        "  - hostname: PC1\n"
        "    model: PC-PT\n"
        "    interfaces:\n"
        "      - name: FastEthernet0\n"
        "        dhcp: true\n"
        "\n"
        "  - hostname: PC2\n"
        "    model: PC-PT\n"
        "    interfaces:\n"
        "      - name: FastEthernet0\n"
        "        dhcp: true\n"
        "\n"
        "  - hostname: Laptop-1\n"
        "    model: Laptop-PT\n"
        "    interfaces:\n"
        "      - name: FastEthernet0\n"
        "        dhcp: true\n"
        "\n"
        "  - hostname: Server-1\n"
        "    model: Server-PT\n"
        "    interfaces:\n"
        "      - name: FastEthernet0\n"
        "        ip: 192.168.20.10\n"
        "        mask: 255.255.255.0\n"
        "        gateway: 192.168.20.1\n"
        "\n"
        "  - hostname: Server-2\n"
        "    model: Server-PT\n"
        "    interfaces:\n"
        "      - name: FastEthernet0\n"
        "        ip: 192.168.20.11\n"
        "        mask: 255.255.255.0\n"
        "        gateway: 192.168.20.1\n"
        "\n"
        "links:\n"
        "  - source: Core-R1:GigabitEthernet0/0\n"
        "    target: Core-R2:GigabitEthernet0/0\n"
        "    type: straight\n"
        "  - source: Core-R1:GigabitEthernet0/1\n"
        "    target: ASA-FW-01:GigabitEthernet0/0\n"
        "    type: straight\n"
        "  - source: Core-R1:GigabitEthernet1/0\n"
        "    target: DSW-1:GigabitEthernet0/1\n"
        "    type: straight\n"
        "  - source: Core-R2:GigabitEthernet0/1\n"
        "    target: ASA-FW-01:GigabitEthernet0/1\n"
        "    type: straight\n"
        "  - source: Core-R2:GigabitEthernet1/0\n"
        "    target: DSW-2:GigabitEthernet0/1\n"
        "    type: straight\n"
        "  - source: DSW-1:GigabitEthernet0/2\n"
        "    target: ASW-1:GigabitEthernet0/1\n"
        "    type: straight\n"
        "  - source: DSW-2:GigabitEthernet0/2\n"
        "    target: ASW-2:GigabitEthernet0/1\n"
        "    type: straight\n"
        "  - source: ASW-1:FastEthernet0/1\n"
        "    target: PC1:FastEthernet0\n"
        "    type: straight\n"
        "  - source: ASW-1:FastEthernet0/2\n"
        "    target: PC2:FastEthernet0\n"
        "    type: straight\n"
        "  - source: ASW-1:FastEthernet0/3\n"
        "    target: Laptop-1:FastEthernet0\n"
        "    type: straight\n"
        "  - source: ASW-2:FastEthernet0/1\n"
        "    target: Server-1:FastEthernet0\n"
        "    type: straight\n"
        "  - source: ASW-2:FastEthernet0/2\n"
        "    target: Server-2:FastEthernet0\n"
        "    type: straight\n"
    ),
}


class CategoryGroup(QWidget):
    def __init__(self, cat_name, parent=None):
        super().__init__(parent)
        self.cat_name = cat_name
        self.expanded = True
        self.tool_buttons = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QPushButton()
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.setObjectName("cat_header")
        color = CAT_COLORS.get(cat_name, C["primary"])
        self.header.setStyleSheet(
            f"QPushButton {{ background: rgba(0,0,0,0.1); border: none; "
            f"border-left: 3px solid {color}; text-align: left; padding: 9px 12px; "
            f"font-size: 11px; font-weight: 700; text-transform: uppercase; "
            f"letter-spacing: 0.06em; color: {C['text_secondary']}; }}"
            f"QPushButton:hover {{ color: {C['text_primary']}; }}"
        )
        self.header.setText(f"{CAT_ICONS.get(cat_name, '')}  {cat_name}")
        self.header.clicked.connect(self.toggle)
        layout.addWidget(self.header)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        layout.addWidget(self.body)

    def add_tool(self, name, info):
        btn = QPushButton()
        btn.setText(f"  {info['icon']}  {name}")
        btn.setFixedHeight(34)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setObjectName("tool_btn")
        self.tool_buttons.append(btn)
        self.body_layout.addWidget(btn)
        return btn

    def toggle(self):
        self.expanded = not self.expanded
        self.body.setVisible(self.expanded)
        color = CAT_COLORS.get(self.cat_name, C["primary"])
        arrow = "\u25BC" if self.expanded else "\u25B6"
        self.header.setText(f"{arrow} {CAT_ICONS.get(self.cat_name, '')}  {self.cat_name}")

    def filter_visible(self, query):
        q = query.lower()
        any_visible = False
        for btn in self.tool_buttons:
            match = q in btn.text().lower()
            btn.setVisible(match)
            if match:
                any_visible = True
        self.header.setVisible(any_visible or not q)
        self.body.setVisible(any_visible or not q)
        if not q:
            self.body.setVisible(self.expanded)


class GeneratorTab(QWidget):
    def __init__(self, name, script_name, parent=None):
        super().__init__(parent)
        self.name = name
        self.script_path = os.path.join(os.path.dirname(__file__), "generators", script_name)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.setContentsMargins(14, 14, 16, 14)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(8)

        # ── Editor Pane ──
        editor_widget = QWidget()
        editor_widget.setObjectName("editor_pane")
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        editor_header = QWidget()
        editor_header.setObjectName("pane_header")
        eh = QHBoxLayout(editor_header)
        eh.setContentsMargins(14, 0, 14, 0)
        label = QLabel("Configuration Input")
        label.setObjectName("pane_label")
        eh.addWidget(label)
        dim = QLabel("(YAML / JSON)")
        dim.setObjectName("pane_label_dim")
        eh.addWidget(dim)
        eh.addStretch()

        self.badge_status = QLabel("Empty")
        self.badge_status.setObjectName("badge_status")
        eh.addWidget(self.badge_status)

        self.badge_lines = QLabel("0 lines")
        self.badge_lines.setObjectName("badge_lines")
        eh.addWidget(self.badge_lines)
        editor_layout.addWidget(editor_header)

        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setPlainText(TEMPLATES.get(self.name, ""))
        self.editor.setFont(QFont("Courier New", 12))
        self.editor.setObjectName("input_editor")
        self.editor.textChanged.connect(self.update_badges)
        editor_layout.addWidget(self.editor)

        # ── Output Pane ──
        output_widget = QWidget()
        output_widget.setObjectName("output_pane")
        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(0)

        output_header = QWidget()
        output_header.setObjectName("pane_header")
        oh = QHBoxLayout(output_header)
        oh.setContentsMargins(0, 0, 14, 0)
        oh.setSpacing(0)

        self.tab_btns = {}
        for tab_id, tab_label in [("cli", "Cisco IOS CLI"), ("pt", "PT-Builder JS")]:
            btn = QPushButton(tab_label)
            btn.setObjectName("tab_btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=tab_id: self.switch_tab(t))
            self.tab_btns[tab_id] = btn
            oh.addWidget(btn)
        oh.addStretch()

        self.btn_copy = QPushButton("\U0001F4CB  Copy")
        self.btn_copy.setObjectName("copy_btn")
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.clicked.connect(self.copy_output)
        oh.addWidget(self.btn_copy)
        output_layout.addWidget(output_header)

        self.output_cli = QTextEdit()
        self.output_cli.setReadOnly(True)
        self.output_cli.setFont(QFont("Courier New", 12))
        self.output_cli.setObjectName("output_cli")

        self.output_pt = QTextEdit()
        self.output_pt.setReadOnly(True)
        self.output_pt.setFont(QFont("Courier New", 12))
        self.output_pt.setObjectName("output_pt")

        self.output_stack = QStackedWidget()
        self.output_stack.addWidget(self.output_cli)
        self.output_stack.addWidget(self.output_pt)
        output_layout.addWidget(self.output_stack)

        splitter.addWidget(editor_widget)
        splitter.addWidget(output_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter)

        self.active_tab = "cli"
        self.switch_tab("cli")
        self.update_badges()

    def switch_tab(self, tab_id):
        self.active_tab = tab_id
        self.output_stack.setCurrentIndex(0 if tab_id == "cli" else 1)
        for tid, btn in self.tab_btns.items():
            active = tid == tab_id
            btn.setProperty("active", active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def copy_output(self):
        src = self.output_cli if self.active_tab == "cli" else self.output_pt
        QGuiApplication.clipboard().setText(src.toPlainText())
        self.btn_copy.setText("\u2705  Copied!")
        QTimer.singleShot(2000, lambda: self.btn_copy.setText("\U0001F4CB  Copy"))

    def update_badges(self):
        text = self.editor.toPlainText()
        lines = len(text.splitlines()) if text.strip() else 0
        self.badge_lines.setText(f"{lines} lines")
        if not text.strip():
            self.badge_status.setText("Empty")
            self.badge_status.setProperty("status", "empty")
        else:
            try:
                yaml.safe_load(text)
                self.badge_status.setText("\u2713 Valid")
                self.badge_status.setProperty("status", "valid")
            except Exception:
                self.badge_status.setText("\u2717 Invalid")
                self.badge_status.setProperty("status", "invalid")
        self.badge_status.style().unpolish(self.badge_status)
        self.badge_status.style().polish(self.badge_status)

    def import_yaml(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open YAML", "", "YAML (*.yaml *.yml);;JSON (*.json);;All Files (*)")
        if file:
            with open(file, 'r') as f:
                self.editor.setPlainText(f.read())

    def export_yaml(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save YAML", "", "YAML (*.yaml *.yml);;JSON (*.json);;All Files (*)")
        if file:
            with open(file, 'w') as f:
                f.write(self.editor.toPlainText())

    def reset_template(self):
        self.editor.setPlainText(TEMPLATES.get(self.name, ""))

    def run_generator(self):
        self.output_cli.setPlainText("Generating...")
        self.output_pt.setPlainText("Generating...")
        text = self.editor.toPlainText()
        if not text.strip():
            self.output_cli.setPlainText("! No input provided.\n! Paste YAML/JSON configuration and try again.")
            self.output_pt.setPlainText("// No input provided.")
            return
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode='w') as tmp:
            tmp.write(text)
            path = tmp.name
        try:
            env = os.environ.copy()
            tools_dir = os.path.join(os.path.dirname(__file__), "tools")
            env["PYTHONPATH"] = tools_dir
            res = subprocess.run(
                [sys.executable, self.script_path, "--file", path],
                capture_output=True, text=True, env=env
            )
            if res.returncode == 0:
                cli_out = res.stdout.strip()
                if not cli_out:
                    cli_out = "! Generator produced no output."
                # Render CLI with simple syntax coloring
                try:
                    self.output_cli.setHtml(self.format_cli_html(cli_out))
                except Exception:
                    self.output_cli.setPlainText(cli_out)
                try:
                    data = yaml.safe_load(text)
                    pt_out = generate_pt_builder_script(data, cli_out)
                    if not pt_out.strip():
                        pt_out = "// No PT-Builder script generated."
                    try:
                        self.output_pt.setHtml(self.format_pt_html(pt_out))
                    except Exception:
                        self.output_pt.setPlainText(pt_out)
                except Exception as e:
                    # PT builder error
                    msg = f"// PT-Builder generation error: {e}"
                    try:
                        self.output_pt.setHtml(self.format_pt_html(msg))
                    except Exception:
                        self.output_pt.setPlainText(msg)
            else:
                err = f"! ERROR (exit {res.returncode}):\n{res.stderr.strip()}\n\nSTDOUT:\n{res.stdout.strip()}"
                try:
                    self.output_cli.setHtml(self.format_cli_html(err))
                except Exception:
                    self.output_cli.setPlainText(err)
                self.output_pt.setPlainText(f"// ERROR: see CLI tab for details")
        except Exception as e:
            self.output_cli.setPlainText(f"! EXECUTION ERROR: {str(e)}")
            self.output_pt.setPlainText(f"// EXECUTION ERROR: {str(e)}")
        finally:
            if os.path.exists(path):
                os.remove(path)


class ExtractTab(QWidget):
    """Workflow tab: copy pt_analyzer.js -> run in PT -> paste output -> parse to YAML."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(8)

        # ── Pane 1: Instructions + JS ──
        js_widget = QWidget()
        js_widget.setObjectName("editor_pane")
        js_layout = QVBoxLayout(js_widget)
        js_layout.setContentsMargins(0, 0, 0, 0)
        js_layout.setSpacing(0)

        js_header = QWidget()
        js_header.setObjectName("pane_header")
        jh = QHBoxLayout(js_header)
        jh.setContentsMargins(14, 0, 14, 0)

        label = QLabel("Step 1 \u2014 Copy the Analyzer Script")
        label.setObjectName("pane_label")
        jh.addWidget(label)
        jh.addStretch()

        self.btn_copy_js = QPushButton("\U0001F4CB  Copy JS")
        self.btn_copy_js.setObjectName("copy_btn")
        self.btn_copy_js.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_js.clicked.connect(self.copy_js)
        jh.addWidget(self.btn_copy_js)
        js_layout.addWidget(js_header)

        instructions = QLabel(
            '<div style="padding: 10px 16px; color: #94a3b8; font-size: 12px; line-height: 1.7;">'
            "<b style='color:#f8fafc;'>1.</b> Click <b>Copy JS</b> above to copy <code>pt_analyzer.js</code><br>"
            "<b style='color:#f8fafc;'>2.</b> In Packet Tracer: <b>Extensions \u2192 Scripting \u2192 Edit File Script Module</b><br>"
            "<b style='color:#f8fafc;'>3.</b> Paste the script, click <b>Run</b><br>"
            "<b style='color:#f8fafc;'>4.</b> Copy all output from the PT console (Ctrl+A, Ctrl+C)<br>"
            "<b style='color:#f8fafc;'>5.</b> Paste it into the text area below<br>"
            "<b style='color:#f8fafc;'>6.</b> Click <b>Parse to YAML</b> to extract structured topology"
            "</div>"
        )
        instructions.setWordWrap(True)
        instructions.setObjectName("extract_instructions")
        js_layout.addWidget(instructions)

        self.js_view = QTextEdit()
        self.js_view.setReadOnly(True)
        self.js_view.setFont(QFont("Courier New", 11))
        self.js_view.setObjectName("js_view")
        self.js_view.setPlainText(ANALYZER_JS)
        self.js_view.setMaximumHeight(180)
        js_layout.addWidget(self.js_view)

        # ── Pane 2: Paste area + Parse button ──
        paste_widget = QWidget()
        paste_widget.setObjectName("output_pane")
        paste_layout = QVBoxLayout(paste_widget)
        paste_layout.setContentsMargins(0, 0, 0, 0)
        paste_layout.setSpacing(0)

        paste_header = QWidget()
        paste_header.setObjectName("pane_header")
        ph = QHBoxLayout(paste_header)
        ph.setContentsMargins(14, 0, 14, 0)

        pl = QLabel("Step 2 \u2014 Paste PT Analyzer Output")
        pl.setObjectName("pane_label")
        ph.addWidget(pl)
        ph.addStretch()

        self.badge_paste = QLabel("0 lines")
        self.badge_paste.setObjectName("badge_lines")
        ph.addWidget(self.badge_paste)
        paste_layout.addWidget(paste_header)

        self.input_area = QTextEdit()
        self.input_area.setAcceptRichText(False)
        self.input_area.setFont(QFont("Courier New", 12))
        self.input_area.setObjectName("input_editor")
        self.input_area.setPlaceholderText(
            "Paste the full output from Packet Tracer's pt_analyzer.js here...\n"
            "The output should contain DEVICE: names and running configs."
        )
        self.input_area.textChanged.connect(self._update_paste_badge)
        paste_layout.addWidget(self.input_area)

        # ── Parse button ──
        btn_bar = QWidget()
        btn_bar.setObjectName("btn_bar_extract")
        bb = QHBoxLayout(btn_bar)
        bb.setContentsMargins(14, 8, 14, 8)

        self.btn_parse = QPushButton("\u2699  Parse to YAML")
        self.btn_parse.setObjectName("btn_generate")
        self.btn_parse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_parse.clicked.connect(self.parse_output)
        bb.addWidget(self.btn_parse)

        self.btn_export_yaml = QPushButton("\U0001F4E4  Export YAML")
        self.btn_export_yaml.setObjectName("copy_btn")
        self.btn_export_yaml.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_yaml.clicked.connect(self.export_yaml)
        self.btn_export_yaml.setEnabled(False)
        bb.addWidget(self.btn_export_yaml)

        bb.addStretch()
        paste_layout.addWidget(btn_bar)

        # ── Pane 3: Output ──
        out_widget = QWidget()
        out_widget.setObjectName("output_pane")
        out_layout = QVBoxLayout(out_widget)
        out_layout.setContentsMargins(0, 0, 0, 0)
        out_layout.setSpacing(0)

        out_header = QWidget()
        out_header.setObjectName("pane_header")
        oh = QHBoxLayout(out_header)
        oh.setContentsMargins(14, 0, 14, 0)

        ol = QLabel("Step 3 \u2014 Parsed YAML Topology")
        ol.setObjectName("pane_label")
        oh.addWidget(ol)
        oh.addStretch()

        self.badge_yaml = QLabel("0 lines")
        self.badge_yaml.setObjectName("badge_lines")
        oh.addWidget(self.badge_yaml)

        self.btn_copy_yaml = QPushButton("\U0001F4CB  Copy")
        self.btn_copy_yaml.setObjectName("copy_btn")
        self.btn_copy_yaml.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_yaml.clicked.connect(self.copy_yaml)
        self.btn_copy_yaml.setEnabled(False)
        oh.addWidget(self.btn_copy_yaml)
        out_layout.addWidget(out_header)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Courier New", 12))
        self.output_area.setObjectName("output_cli")
        self.output_area.setPlaceholderText("Parsed YAML topology will appear here after clicking Parse to YAML.")
        out_layout.addWidget(self.output_area)

        splitter.addWidget(js_widget)
        splitter.addWidget(paste_widget)
        splitter.addWidget(out_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 2)
        layout.addWidget(splitter)

    def _update_paste_badge(self):
        text = self.input_area.toPlainText()
        lines = len(text.splitlines()) if text.strip() else 0
        self.badge_paste.setText(f"{lines} lines")

    def copy_js(self):
        QGuiApplication.clipboard().setText(ANALYZER_JS)
        self.btn_copy_js.setText("\u2705  Copied!")
        QTimer.singleShot(2000, lambda: self.btn_copy_js.setText("\U0001F4CB  Copy JS"))

    def parse_output(self):
        text = self.input_area.toPlainText().strip()
        if not text:
            self.output_area.setPlainText("# No input provided.\n# Paste the pt_analyzer.js output from Packet Tracer and try again.")
            return
        try:
            yaml_out = parse_analyzer_output(text)
            try:
                self.output_area.setHtml(self.format_yaml_html(yaml_out))
            except Exception:
                self.output_area.setPlainText(yaml_out)
            lines = len(yaml_out.splitlines()) if yaml_out.strip() else 0
            self.badge_yaml.setText(f"{lines} lines")
            self.btn_export_yaml.setEnabled(True)
            self.btn_copy_yaml.setEnabled(True)
        except Exception as e:
            self.output_area.setPlainText(f"# Parse error: {e}\n# Check that you pasted the full pt_analyzer.js output.")

    def copy_yaml(self):
        QGuiApplication.clipboard().setText(self.output_area.toPlainText())
        self.btn_copy_yaml.setText("\u2705  Copied!")
        QTimer.singleShot(2000, lambda: self.btn_copy_yaml.setText("\U0001F4CB  Copy"))

    def export_yaml(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save YAML", "", "YAML (*.yaml *.yml);;All Files (*)")
        if file:
            with open(file, 'w') as f:
                f.write(self.output_area.toPlainText())

    def import_yaml(self):
        self.input_area.clear()
        self.output_area.clear()
        self.badge_paste.setText("0 lines")
        self.badge_yaml.setText("0 lines")
        self.btn_export_yaml.setEnabled(False)
        self.btn_copy_yaml.setEnabled(False)

    def reset_template(self):
        self.import_yaml()

    def run_generator(self):
        self.parse_output()


class KeystoneGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keystone \u2014 Network Automation")
        self.resize(1280, 920)
        self.tool_widgets = {}
        self.category_groups = []
        self.init_ui()

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        main_v = QVBoxLayout(cw)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.setSpacing(0)

        # ── Top Bar ──
        self.topbar = QWidget()
        self.topbar.setObjectName("topbar")
        self.topbar.setFixedHeight(56)
        tb = QHBoxLayout(self.topbar)
        tb.setContentsMargins(16, 0, 20, 0)
        tb.setSpacing(12)

        self.brand = QLabel("Keystone \u26A1")
        self.brand.setObjectName("brand")
        tb.addWidget(self.brand)

        self.tool_badge = QLabel("\u2014  Loading...")
        self.tool_badge.setObjectName("tool_badge")
        tb.addWidget(self.tool_badge)

        tb.addStretch()

        self.btn_generate = QPushButton("\u25B6  Generate")
        self.btn_generate.setObjectName("btn_generate")
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.clicked.connect(self.run_current)
        tb.addWidget(self.btn_generate)

        self.btn_reset = QPushButton("\u21BB  Reset")
        self.btn_reset.setObjectName("btn_reset")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.reset_current)
        tb.addWidget(self.btn_reset)

        self.btn_import = QPushButton("\U0001F4C2")
        self.btn_import.setFixedWidth(36)
        self.btn_import.setObjectName("icon_btn")
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import.setToolTip("Import YAML/JSON file")
        self.btn_import.clicked.connect(self.import_current)
        tb.addWidget(self.btn_import)

        self.btn_export = QPushButton("\U0001F4E4")
        self.btn_export.setFixedWidth(36)
        self.btn_export.setObjectName("icon_btn")
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.setToolTip("Export YAML/JSON file")
        self.btn_export.clicked.connect(self.export_current)
        tb.addWidget(self.btn_export)

        main_v.addWidget(self.topbar)

        # ── Body: Sidebar + Content ──
        body = QWidget()
        body.setObjectName("body")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        search_widget = QWidget()
        search_widget.setObjectName("search_widget")
        sw = QHBoxLayout(search_widget)
        sw.setContentsMargins(14, 10, 14, 6)
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Search generators...")
        self.search_input.textChanged.connect(self.filter_tools)
        sw.addWidget(self.search_input)

        self.search_clear = QPushButton("\u00D7")
        self.search_clear.setObjectName("search_clear")
        self.search_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_clear.clicked.connect(lambda: self.search_input.clear())
        sw.addWidget(self.search_clear)
        sb.addWidget(search_widget)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("sidebar_scroll")
        scroll_content = QWidget()
        self.sidebar_layout = QVBoxLayout(scroll_content)
        self.sidebar_layout.setContentsMargins(0, 4, 0, 16)
        self.sidebar_layout.setSpacing(0)

        for cat in CAT_ORDER:
            group = CategoryGroup(cat)
            tools_in_cat = [(n, i) for n, i in TOOL_INFO.items() if i["cat"] == cat]
            for name, info in tools_in_cat:
                btn = group.add_tool(name, info)
                btn.clicked.connect(lambda checked, t=name: self.show_tool(t))
            self.sidebar_layout.addWidget(group)
            self.category_groups.append(group)

        self.sidebar_layout.addStretch()
        scroll.setWidget(scroll_content)
        sb.addWidget(scroll)
        body_layout.addWidget(sidebar)

        # ── Content Area ──
        self.content_container = QWidget()
        self.content_container.setObjectName("content")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        self.tool_stack = QStackedWidget()

        # Welcome
        self.welcome = QWidget()
        wl = QVBoxLayout(self.welcome)
        wl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wt = QLabel("Keystone")
        wt.setObjectName("welcome_title")
        ws = QLabel("Select a protocol from the sidebar to begin automation.")
        ws.setObjectName("welcome_subtitle")
        wl.addWidget(wt, alignment=Qt.AlignmentFlag.AlignCenter)
        wl.addWidget(ws, alignment=Qt.AlignmentFlag.AlignCenter)
        self.tool_stack.addWidget(self.welcome)
        self.content_layout.addWidget(self.tool_stack, 1)
        body_layout.addWidget(self.content_container)

        main_v.addWidget(body, 1)

        # ── Status Bar ──
        self.statusbar = QWidget()
        self.statusbar.setObjectName("statusbar_widget")
        self.statusbar.setFixedHeight(30)
        st = QHBoxLayout(self.statusbar)
        st.setContentsMargins(14, 0, 14, 0)
        st.setSpacing(10)

        self.st_tool = QLabel("Keystone")
        self.st_tool.setObjectName("st_tool")
        st.addWidget(self.st_tool)
        sep = QLabel("\u00B7")
        sep.setObjectName("st_sep")
        st.addWidget(sep)
        self.st_cat = QLabel("Automation Engine")
        self.st_cat.setObjectName("st_cat")
        st.addWidget(self.st_cat)
        sep2 = QLabel("\u00B7")
        sep2.setObjectName("st_sep")
        st.addWidget(sep2)
        self.st_keys = QLabel("Press Ctrl+Enter to generate config")
        self.st_keys.setObjectName("st_keys")
        st.addWidget(self.st_keys)
        st.addStretch()
        self.st_saved = QLabel("All states saved in-browser")
        self.st_saved.setObjectName("st_saved")
        st.addWidget(self.st_saved)
        main_v.addWidget(self.statusbar)

        # ── Keyboard shortcut ──
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.run_current)

        self.apply_style()

    def format_cli_html(self, cli_text):
        """Simple HTML formatter for generated Cisco IOS CLI to improve readability."""
        esc = html.escape(cli_text)
        lines = esc.splitlines()
        out_lines = []
        for ln in lines:
            s = ln.lstrip()
            color = C['text_primary']
            # comment
            if s.startswith('!') or s.startswith('#'):
                color = C['text_muted']
            elif s.startswith('hostname'):
                color = C['primary']
            elif s.startswith('interface'):
                color = C['cat_routing']
            elif s.startswith('vlan') or s.strip().startswith('vlan'):
                color = C['cat_services']
            elif s.startswith('ip route') or s.startswith('ipv6 route') or s.startswith('router') or s.startswith('network'):
                color = C['cat_routing']
            elif 'ssh' in s or 'crypto' in s or s.startswith('username'):
                color = C['cat_security']
            out_lines.append(f"<div style='color:{color}; white-space:pre; font-family: monospace;'>{ln}</div>")
        return "<div style='background:%s; padding:8px; border-radius:6px;'>%s</div>" % (C['bg_terminal'], '\n'.join(out_lines))

    def format_pt_html(self, pt_text):
        """Simple HTML formatter for PT-Builder JS output."""
        esc = html.escape(pt_text)
        lines = esc.splitlines()
        out_lines = []
        for ln in lines:
            s = ln.lstrip()
            color = C['text_primary']
            if s.startswith('//') or s.startswith('/*') or s.startswith('*'):
                color = C['text_muted']
            elif s.startswith('addDevice') or 'addDevice(' in s:
                color = '#07d4ff'  # cyan accent for device adds
            elif s.startswith('addLink') or 'addLink(' in s:
                color = C['primary']
            elif s.startswith('configureIosDevice'):
                color = C['cat_utilities']
            out_lines.append(f"<div style='color:{color}; white-space:pre; font-family: monospace;'>{ln}</div>")
        return "<div style='background:%s; padding:8px; border-radius:6px;'>%s</div>" % (C['bg_input'], '\n'.join(out_lines))

    def format_yaml_html(self, yaml_text):
        """Light YAML highlighter: comments, keys, and values."""
        esc = html.escape(yaml_text)
        lines = esc.splitlines()
        out_lines = []
        for ln in lines:
            s = ln.lstrip()
            color = C['text_primary']
            if s.startswith('#'):
                color = C['text_muted']
            else:
                # bold keys (simple heuristic: lines containing ':' before any '#')
                if ':' in s and not s.startswith('-'):
                    parts = s.split(':', 1)
                    key = parts[0]
                    val = parts[1]
                    out_lines.append(f"<div style='white-space:pre; font-family: monospace;'><span style='color:{C['primary']}; font-weight:700;'>{key}:</span><span style='color:{C['text_secondary']};'>{val}</span></div>")
                    continue
                elif s.startswith('- '):
                    out_lines.append(f"<div style='color:{C['cat_services']}; white-space:pre; font-family: monospace;'>{ln}</div>")
                    continue
            out_lines.append(f"<div style='color:{color}; white-space:pre; font-family: monospace;'>{ln}</div>")
        return "<div style='background:%s; padding:8px; border-radius:6px;'>%s</div>" % (C['bg_input'], '\n'.join(out_lines))

    def show_tool(self, name):
        self.tool_badge.setText(f"\u2014  {name}")
        info = TOOL_INFO.get(name, {})
        self.st_cat.setText(info.get("cat", "Automation Engine"))
        if name not in self.tool_widgets:
            if name == "Extract from PT":
                self.tool_widgets[name] = ExtractTab()
            else:
                self.tool_widgets[name] = GeneratorTab(name, info.get("script", ""))
            self.tool_stack.addWidget(self.tool_widgets[name])
        self.tool_stack.setCurrentWidget(self.tool_widgets[name])

    def run_current(self):
        w = self.tool_stack.currentWidget()
        if w and w != self.welcome:
            w.run_generator()

    def reset_current(self):
        w = self.tool_stack.currentWidget()
        if w and w != self.welcome:
            w.reset_template()

    def import_current(self):
        w = self.tool_stack.currentWidget()
        if w and w != self.welcome:
            w.import_yaml()

    def export_current(self):
        w = self.tool_stack.currentWidget()
        if w and w != self.welcome:
            w.export_yaml()

    def filter_tools(self, query):
        for group in self.category_groups:
            group.filter_visible(query)
        self.search_clear.setVisible(bool(query.strip()))

    def apply_style(self):
        c = C
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background: {c['bg_dark']}; color: {c['text_primary']}; }}
            
            /* ── Top Bar ── */
            #topbar {{
                background: {c['bg_surface']}; border-bottom: 1px solid {c['border']};
                min-height: 56px;
            }}
            #brand {{
                font-size: 20px; font-weight: 800; letter-spacing: -0.04em;
                color: {c['primary']}; padding: 0;
            }}
            #tool_badge {{
                font-size: 13px; font-weight: 600; color: {c['text_secondary']};
                background: {c['bg_surface_light']}; padding: 4px 12px;
                border: 1px solid {c['border']}; border-radius: 4px;
            }}
            
            /* ── Top Bar Buttons ── */
            #btn_generate {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #818cf8);
                border: none; color: #ffffff; font-weight: 600; font-size: 13px;
                padding: 0 18px; border-radius: 6px; height: 36px;
            }}
            #btn_generate:hover {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #6366f1); }}
            #btn_reset {{
                background: transparent; border: 1px solid {c['primary']};
                color: {c['primary']}; font-weight: 600; font-size: 13px;
                padding: 0 16px; border-radius: 6px; height: 36px;
            }}
            #btn_reset:hover {{ background: rgba(99,102,241,0.12); color: {c['text_primary']}; }}
            #icon_btn {{
                background: {c['bg_surface_light']}; border: 1px solid {c['border']};
                color: {c['text_secondary']}; border-radius: 6px; height: 36px; font-size: 15px;
            }}
            #icon_btn:hover {{ border-color: {c['border_hover']}; color: {c['text_primary']}; }}
            
            /* ── Sidebar ── */
            #sidebar {{
                background: {c['bg_surface']}; border-right: 1px solid {c['border']};
            }}
            #search_widget {{ background: transparent; }}
            #search_input {{
                background: {c['bg_input']}; border: 1px solid {c['border']};
                border-radius: 6px; padding: 7px 10px; color: {c['text_primary']};
                font-size: 12.5px; outline: none;
            }}
            #search_input:focus {{ border-color: {c['primary']}; }}
            #search_clear {{
                background: transparent; border: none; color: {c['text_muted']};
                font-size: 18px; padding: 0 4px; min-width: 20px;
            }}
            #search_clear:hover {{ color: {c['text_primary']}; }}
            
            /* ── Tool Buttons ── */
            #tool_btn {{
                background: transparent; border: none; border-left: 3px solid transparent;
                text-align: left; padding-left: 18px; border-radius: 0;
                font-size: 13px; color: {c['text_secondary']}; font-weight: 450;
            }}
            #tool_btn:hover {{
                background: rgba(255,255,255,0.02); color: {c['text_primary']};
                padding-left: 20px;
            }}
            #sidebar_scroll {{ background: transparent; }}
            
            #content {{ background: {c['bg_dark']}; }}

            /* ── Editor & Output Panes ── */
            #editor_pane, #output_pane {{
                border-radius: 10px; border: 1px solid {c['border']};
            }}
            #editor_pane {{ border-top: 3px solid {c['primary']}; background: {c['bg_surface']}; }}
            #output_pane {{ border-top: 3px solid {c['success']}; background: {c['bg_surface']}; }}
            
            #pane_header {{
                background: rgba(0,0,0,0.08); border-bottom: 1px solid {c['border']};
                min-height: 44px;
            }}
            #pane_label {{
                font-size: 13.5px; font-weight: 600; color: {c['text_primary']};
            }}
            #pane_label_dim {{
                font-size: 11px; color: {c['text_muted']}; font-weight: 400;
            }}
            
            /* ── Badges ── */
            #badge_status, #badge_lines {{
                font-size: 10.5px; font-weight: 600; font-family: 'Courier New', monospace;
                padding: 2px 10px; border-radius: 20px; border: 1px solid {c['border']};
                margin-left: 6px;
            }}
            #badge_status {{
                background: rgba(0,0,0,0.15); color: {c['text_muted']};
            }}
            #badge_status[status="valid"] {{
                background: rgba(16,185,129,0.15); color: {c['success']};
                border-color: rgba(16,185,129,0.3);
            }}
            #badge_status[status="invalid"] {{
                background: rgba(239,68,68,0.15); color: {c['error']};
                border-color: rgba(239,68,68,0.3);
            }}
            #badge_lines {{
                background: {c['bg_dark']}; color: {c['text_secondary']};
            }}
            
            /* ── Tab Buttons ── */
            #tab_btn {{
                background: transparent; border: none; border-bottom: 2px solid transparent;
                color: {c['text_secondary']}; font-size: 13px; font-weight: 600;
                padding: 0 16px; height: 100%; min-height: 44px;
            }}
            #tab_btn:hover {{ color: {c['text_primary']}; }}
            #tab_btn[active="true"] {{
                color: {c['primary']}; border-bottom-color: {c['primary']};
            }}
            
            /* ── Copy Button ── */
            #copy_btn {{
                background: {c['bg_surface_light']}; border: 1px solid {c['border']};
                color: {c['text_primary']}; font-size: 12px; font-weight: 600;
                padding: 0 14px; border-radius: 6px; height: 32px;
            }}
            #copy_btn:hover {{ border-color: {c['text_muted']}; }}
            
            /* ── Input/Output Textareas ── */
            #input_editor {{
                background: {c['bg_input']}; color: {c['text_primary']};
                border: none; padding: 16px; font-size: 13px; line-height: 1.6;
            }}
            #output_cli {{
                background: {c['bg_terminal']}; color: #10b981;
                border: none; padding: 16px; font-size: 13px; line-height: 1.6;
            }}
            #output_pt {{
                background: {c['bg_input']}; color: {c['text_primary']};
                border: none; padding: 16px; font-size: 13px; line-height: 1.6;
            }}
            
            /* ── Splitter ── */
            QSplitter::handle {{
                background: transparent; margin: 0; height: 8px;
            }}
            QSplitter::handle:vertical {{
                image: none; border: none;
            }}
            
            /* ── Scrollbar ── */
            QScrollBar:vertical {{
                width: 8px; background: {c['bg_dark']};
            }}
            QScrollBar::handle:vertical {{
                background: {c['border']}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {c['border_hover']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            
            /* ── Status Bar ── */
            #statusbar_widget {{
                background: {c['bg_surface']}; border-top: 1px solid {c['border']};
            }}
            #st_tool {{ font-weight: 600; color: {c['text_primary']}; }}
            #st_sep {{ color: {c['text_muted']}; }}
            #st_cat {{ color: {c['primary']}; font-weight: 600; }}
            #st_keys {{ color: {c['text_muted']}; }}
            #st_saved {{ color: {c['text_secondary']}; font-size: 12px; }}
            
            /* ── Welcome ── */
            #welcome_title {{
                font-size: 48px; font-weight: 800; color: {c['border']};
            }}
            #welcome_subtitle {{
                color: {c['border_hover']}; font-size: 13px;
            }}
            
            /* ── Extract Tab ── */
            #js_view {{
                background: {c['bg_terminal']}; color: #e2e8f0;
                border: none; padding: 12px; font-size: 12px; line-height: 1.6;
            }}
            #extract_instructions {{
                background: {c['bg_surface']}; border-bottom: 1px solid {c['border']};
            }}
            #btn_bar_extract {{
                background: {c['bg_dark']}; border-top: 1px solid {c['border']};
            }}
            
            /* ── Tooltips ── */
            QToolTip {{
                background: {c['bg_surface_light']}; color: {c['text_primary']};
                border: 1px solid {c['border']}; padding: 4px 8px; border-radius: 4px;
                font-size: 12px;
            }}
        """)


def _silent_qt_msg(msg_type, context, msg):
    msg = str(msg)
    if "Unknown property" in msg or "kf.iconthemes" in msg:
        return
    _silent_qt_msg.prev(msg_type, context, msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    _silent_qt_msg.prev = qInstallMessageHandler(_silent_qt_msg)
    app.setStyle("Fusion")
    w = KeystoneGUI()
    w.show()
    sys.exit(app.exec())
