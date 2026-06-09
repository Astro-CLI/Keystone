import sys
import os
import subprocess
import tempfile
import yaml
import json
import re
import html
import signal
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

_ANALYZER_JS_PATH = os.path.join(os.path.dirname(__file__), 'scripts', 'pt_analyzer.js')
ANALYZER_JS = ""
if os.path.exists(_ANALYZER_JS_PATH):
    with open(_ANALYZER_JS_PATH) as f:
        ANALYZER_JS = f.read()


def fix_yaml_list_indentation(text: str) -> str:
    """Attempt to fix common list-item indentation errors.
    For list items like:
      - hostname: ASW10
       type: switch
    where subsequent lines are under-indented, this function increases their indent
    to dash_indent + 2 so YAML parsers accept them.
    """
    lines = text.splitlines()
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        out.append(line)
        stripped = line.lstrip(' ')
        if stripped.startswith('- '):
            dash_indent = len(line) - len(stripped)
            expected = dash_indent + 2
            j = i + 1
            while j < n:
                next_line = lines[j]
                if next_line.strip() == '':
                    out.append(next_line)
                    j += 1
                    continue
                next_stripped = next_line.lstrip(' ')
                next_indent = len(next_line) - len(next_stripped)
                # if this is a new list item at same or lesser indent, stop
                if next_stripped.startswith('- ') and next_indent <= dash_indent:
                    break
                # otherwise, ensure it's indented at least expected
                if next_indent < expected:
                    fixed = ' ' * expected + next_stripped
                    out.append(fixed)
                else:
                    out.append(next_line)
                j += 1
            i = j
            continue
        i += 1
    return '\n'.join(out)

# ── Catppuccin Mocha Palette ──
C = {
    "bg_dark": "#11111b", "bg_surface": "#181825", "bg_surface_light": "#1e1e2e",
    "bg_input": "#1e1e2e", "bg_terminal": "#11111b", "border": "#313244",
    "border_hover": "#45475a", "text_primary": "#cdd6f4", "text_secondary": "#a6adc8",
    "text_muted": "#6c7086", "primary": "#cba6f7", "primary_hover": "#b4befe",
    "primary_glow": "rgba(203, 166, 247, 0.15)", "success": "#a6e3a1", "error": "#f38ba8",
    "warning": "#f9e2af", "syn_comment": "#6c7086", "syn_string": "#a6e3a1",
    "syn_number": "#fab387", "syn_ip": "#89dceb", "syn_keyword": "#cba6f7",
    "syn_cmd": "#89b4fa", "syn_desc": "#bac2de", "syn_func": "#74c7ec",
    "syn_js_kw": "#94e2d5", "syn_error": "#f38ba8",
}

CAT_COLORS = {
    "WORKFLOWS": "#f5c2e7", "ROUTING": "#89b4fa", "SECURITY": "#f38ba8",
    "SERVICES": "#a6e3a1", "UTILITIES": "#f9e2af",
}

CAT_ICONS = {
    "WORKFLOWS": "\u2194", "ROUTING": "\u25C9", "SECURITY": "\u26E8",
    "SERVICES": "\u2699", "UTILITIES": "\u229E",
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
        """# Full Topology: Enterprise 3-Tier Network Mesh
# Exact placement: R1(100,100) R2(200,200) R3(300,100)
# MLS per router: left/right (±25, +125)
# Access switches (2 per MLS): left/right (±50, +150)
# End devices (2 PCs + 1 Server per ASW): spread horizontally below
# IPv4 host defaults are auto-derived by subnet when omitted; IPv6 examples follow the same pattern

name: "Enterprise 3-Tier Mesh"

devices:
  # CORE LAYER
  - hostname: R1
    type: router
    ospf: { process_id: 1, router_id: 1.1.1.1, area: 0 }
  - hostname: R2
    type: router
    ospf: { process_id: 1, router_id: 2.2.2.2, area: 0 }
  - hostname: R3
    type: router
    ospf: { process_id: 1, router_id: 3.3.3.3, area: 0 }

  # DISTRIBUTION (MLS)
  - hostname: MLS1
    type: switch_l3
    router: R1
    side: left
  - hostname: MLS2
    type: switch_l3
    router: R1
    side: right
  - hostname: MLS3
    type: switch_l3
    router: R2
    side: left
  - hostname: MLS4
    type: switch_l3
    router: R2
    side: right
  - hostname: MLS5
    type: switch_l3
    router: R3
    side: left
  - hostname: MLS6
    type: switch_l3
    router: R3
    side: right

  # ACCESS (2 per MLS)
  - hostname: ASW1
    type: switch
    mls: MLS1
    sub: left
  - hostname: ASW2
    type: switch
    mls: MLS1
    sub: right
  - hostname: ASW3
    type: switch
    mls: MLS2
    sub: left
  - hostname: ASW4
    type: switch
    mls: MLS2
    sub: right
  - hostname: ASW5
    type: switch
    mls: MLS3
    sub: left
  - hostname: ASW6
    type: switch
    mls: MLS3
    sub: right
  - hostname: ASW7
    type: switch
    mls: MLS4
    sub: left
  - hostname: ASW8
    type: switch
    mls: MLS4
    sub: right
  - hostname: ASW9
    type: switch
    mls: MLS5
    sub: left
  - hostname: ASW10
    type: switch
    mls: MLS5
    sub: right
  - hostname: ASW11
    type: switch
    mls: MLS6
    sub: left
  - hostname: ASW12
    type: switch
    mls: MLS6
    sub: right

  # END DEVICES (2 PCs + 1 Server per ASW)
  - hostname: PC1_1
    type: pc
    ip: 192.168.1.11
    group: ASW1
    pos: 0
  - hostname: PC2_1
    type: pc
    group: ASW1
    pos: 1
  - hostname: SRV1_1
    type: server
    ip: 192.168.1.100
    group: ASW1
    pos: 2
  - hostname: PC1_2
    type: pc
    ip: 192.168.1.12
    group: ASW2
    pos: 0
  - hostname: PC2_2
    type: pc
    group: ASW2
    pos: 1
  - hostname: SRV1_2
    type: server
    ip: 192.168.1.101
    group: ASW2
    pos: 2
  - hostname: PC1_3
    type: pc
    ip: 192.168.1.13
    group: ASW3
    pos: 0
  - hostname: PC2_3
    type: pc
    group: ASW3
    pos: 1
  - hostname: SRV1_3
    type: server
    ip: 192.168.1.102
    group: ASW3
    pos: 2
  - hostname: PC1_4
    type: pc
    ip: 192.168.1.14
    group: ASW4
    pos: 0
  - hostname: PC2_4
    type: pc
    group: ASW4
    pos: 1
  - hostname: SRV1_4
    type: server
    ip: 192.168.1.103
    group: ASW4
    pos: 2
  - hostname: PC1_5
    type: pc
    ip: 192.168.2.11
    group: ASW5
    pos: 0
  - hostname: PC2_5
    type: pc
    group: ASW5
    pos: 1
  - hostname: SRV1_5
    type: server
    ip: 192.168.2.100
    group: ASW5
    pos: 2
  - hostname: PC1_6
    type: pc
    ip: 192.168.2.12
    group: ASW6
    pos: 0
  - hostname: PC2_6
    type: pc
    group: ASW6
    pos: 1
  - hostname: SRV1_6
    type: server
    ip: 192.168.2.101
    group: ASW6
    pos: 2
  - hostname: PC1_7
    type: pc
    ip: 192.168.2.13
    group: ASW7
    pos: 0
  - hostname: PC2_7
    type: pc
    group: ASW7
    pos: 1
  - hostname: SRV1_7
    type: server
    ip: 192.168.2.102
    group: ASW7
    pos: 2
  - hostname: PC1_8
    type: pc
    ip: 192.168.2.14
    group: ASW8
    pos: 0
  - hostname: PC2_8
    type: pc
    group: ASW8
    pos: 1
  - hostname: SRV1_8
    type: server
    ip: 192.168.2.103
    group: ASW8
    pos: 2
  - hostname: PC1_9
    type: pc
    ip: 192.168.3.11
    group: ASW9
    pos: 0
  - hostname: PC2_9
    type: pc
    group: ASW9
    pos: 1
  - hostname: SRV1_9
    type: server
    ip: 192.168.3.100
    group: ASW9
    pos: 2
  - hostname: PC1_10
    type: pc
    ip: 192.168.3.12
    group: ASW10
    pos: 0
  - hostname: PC2_10
    type: pc
    group: ASW10
    pos: 1
  - hostname: SRV1_10
    type: server
    ip: 192.168.3.101
    group: ASW10
    pos: 2
  - hostname: PC1_11
    type: pc
    ip: 192.168.3.13
    group: ASW11
    pos: 0
  - hostname: PC2_11
    type: pc
    group: ASW11
    pos: 1
  - hostname: SRV1_11
    type: server
    ip: 192.168.3.102
    group: ASW11
    pos: 2
  - hostname: PC1_12
    type: pc
    ip: 192.168.3.14
    group: ASW12
    pos: 0
  - hostname: PC2_12
    type: pc
    group: ASW12
    pos: 1
  - hostname: SRV1_12
    type: server
    ip: 192.168.3.103
    group: ASW12
    pos: 2

links:
  # Core Triangle (Serial)
  - { source: "R1:Serial0/0/0", target: "R2:Serial0/0/0" }
  - { source: "R1:Serial0/1/0", target: "R3:Serial0/1/0" }
  - { source: "R2:Serial0/1/0", target: "R3:Serial0/2/0" }

  # Core to Distribution (Ethernet)
  - { source: "R1:GigabitEthernet0/0", target: "MLS1:GigabitEthernet0/1" }
  - { source: "R1:GigabitEthernet0/1", target: "MLS2:GigabitEthernet0/1" }
  - { source: "R2:GigabitEthernet0/0", target: "MLS3:GigabitEthernet0/1" }
  - { source: "R2:GigabitEthernet0/1", target: "MLS4:GigabitEthernet0/1" }
  - { source: "R3:GigabitEthernet0/0", target: "MLS5:GigabitEthernet0/1" }
  - { source: "R3:GigabitEthernet0/1", target: "MLS6:GigabitEthernet0/1" }

  # EtherChannel Pair Links
  - { source: "MLS1:GigabitEthernet0/23", target: "MLS2:GigabitEthernet0/23" }
  - { source: "MLS1:GigabitEthernet0/24", target: "MLS2:GigabitEthernet0/24" }
  - { source: "MLS3:GigabitEthernet0/23", target: "MLS4:GigabitEthernet0/23" }
  - { source: "MLS3:GigabitEthernet0/24", target: "MLS4:GigabitEthernet0/24" }
  - { source: "MLS5:GigabitEthernet0/23", target: "MLS6:GigabitEthernet0/23" }
  - { source: "MLS5:GigabitEthernet0/24", target: "MLS6:GigabitEthernet0/24" }

  # Distribution to Access
  - { source: "MLS1:GigabitEthernet0/2", target: "ASW1:GigabitEthernet0/1" }
  - { source: "MLS1:GigabitEthernet0/3", target: "ASW2:GigabitEthernet0/1" }
  - { source: "MLS2:GigabitEthernet0/2", target: "ASW3:GigabitEthernet0/1" }
  - { source: "MLS2:GigabitEthernet0/3", target: "ASW4:GigabitEthernet0/1" }
  - { source: "MLS3:GigabitEthernet0/2", target: "ASW5:GigabitEthernet0/1" }
  - { source: "MLS3:GigabitEthernet0/3", target: "ASW6:GigabitEthernet0/1" }
  - { source: "MLS4:GigabitEthernet0/2", target: "ASW7:GigabitEthernet0/1" }
  - { source: "MLS4:GigabitEthernet0/3", target: "ASW8:GigabitEthernet0/1" }
  - { source: "MLS5:GigabitEthernet0/2", target: "ASW9:GigabitEthernet0/1" }
  - { source: "MLS5:GigabitEthernet0/3", target: "ASW10:GigabitEthernet0/1" }
  - { source: "MLS6:GigabitEthernet0/2", target: "ASW11:GigabitEthernet0/1" }
  - { source: "MLS6:GigabitEthernet0/3", target: "ASW12:GigabitEthernet0/1" }

  # Access to End Devices
  - { source: "ASW1:FastEthernet0/1", target: "PC1_1:FastEthernet0" }
  - { source: "ASW1:FastEthernet0/2", target: "PC2_1:FastEthernet0" }
  - { source: "ASW1:FastEthernet0/3", target: "SRV1_1:FastEthernet0" }
  - { source: "ASW2:FastEthernet0/1", target: "PC1_2:FastEthernet0" }
  - { source: "ASW2:FastEthernet0/2", target: "PC2_2:FastEthernet0" }
  - { source: "ASW2:FastEthernet0/3", target: "SRV1_2:FastEthernet0" }
  - { source: "ASW3:FastEthernet0/1", target: "PC1_3:FastEthernet0" }
  - { source: "ASW3:FastEthernet0/2", target: "PC2_3:FastEthernet0" }
  - { source: "ASW3:FastEthernet0/3", target: "SRV1_3:FastEthernet0" }
  - { source: "ASW4:FastEthernet0/1", target: "PC1_4:FastEthernet0" }
  - { source: "ASW4:FastEthernet0/2", target: "PC2_4:FastEthernet0" }
  - { source: "ASW4:FastEthernet0/3", target: "SRV1_4:FastEthernet0" }
  - { source: "ASW5:FastEthernet0/1", target: "PC1_5:FastEthernet0" }
  - { source: "ASW5:FastEthernet0/2", target: "PC2_5:FastEthernet0" }
  - { source: "ASW5:FastEthernet0/3", target: "SRV1_5:FastEthernet0" }
  - { source: "ASW6:FastEthernet0/1", target: "PC1_6:FastEthernet0" }
  - { source: "ASW6:FastEthernet0/2", target: "PC2_6:FastEthernet0" }
  - { source: "ASW6:FastEthernet0/3", target: "SRV1_6:FastEthernet0" }
  - { source: "ASW7:FastEthernet0/1", target: "PC1_7:FastEthernet0" }
  - { source: "ASW7:FastEthernet0/2", target: "PC2_7:FastEthernet0" }
  - { source: "ASW7:FastEthernet0/3", target: "SRV1_7:FastEthernet0" }
  - { source: "ASW8:FastEthernet0/1", target: "PC1_8:FastEthernet0" }
  - { source: "ASW8:FastEthernet0/2", target: "PC2_8:FastEthernet0" }
  - { source: "ASW8:FastEthernet0/3", target: "SRV1_8:FastEthernet0" }
  - { source: "ASW9:FastEthernet0/1", target: "PC1_9:FastEthernet0" }
  - { source: "ASW9:FastEthernet0/2", target: "PC2_9:FastEthernet0" }
  - { source: "ASW9:FastEthernet0/3", target: "SRV1_9:FastEthernet0" }
  - { source: "ASW10:FastEthernet0/1", target: "PC1_10:FastEthernet0" }
  - { source: "ASW10:FastEthernet0/2", target: "PC2_10:FastEthernet0" }
  - { source: "ASW10:FastEthernet0/3", target: "SRV1_10:FastEthernet0" }
  - { source: "ASW11:FastEthernet0/1", target: "PC1_11:FastEthernet0" }
  - { source: "ASW11:FastEthernet0/2", target: "PC2_11:FastEthernet0" }
  - { source: "ASW11:FastEthernet0/3", target: "SRV1_11:FastEthernet0" }
  - { source: "ASW12:FastEthernet0/1", target: "PC1_12:FastEthernet0" }
  - { source: "ASW12:FastEthernet0/2", target: "PC2_12:FastEthernet0" }
  - { source: "ASW12:FastEthernet0/3", target: "SRV1_12:FastEthernet0" }
"""),
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
        btn.setToolTip(info.get("desc", ""))
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
        layout.setContentsMargins(14, 14, 16, 14)
        layout.setSpacing(0)

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

        if self.name == "Full Topology":
            # Better YAML parse error reporting for user clarity
            try:
                data = yaml.safe_load(text)
            except yaml.YAMLError as ye:
                # Try an automatic, conservative fix for common list indentation issues
                fixed = fix_yaml_list_indentation(text)
                if fixed != text:
                    try:
                        data = yaml.safe_load(fixed)
                        # parsed successfully after auto-fix
                        note = "! YAML PARSE: minor indentation issues were auto-fixed."
                        self.output_cli.setPlainText(note)
                        # proceed with the fixed data
                    except Exception:
                        # fall through to show original error below
                        pass
                # if data not set yet, show the original parse error with context
                if 'data' not in locals() or data is None:
                    msg = str(ye)
                    mark = getattr(ye, 'problem_mark', None)
                    snippet = ''
                    if mark is not None:
                        line = getattr(mark, 'line', None)
                        col = getattr(mark, 'column', None)
                        if line is not None:
                            lines = text.splitlines()
                            start = max(0, line - 3)
                            end = min(len(lines), line + 3)
                            snippet = '\n'.join(f"{i+1:4}: {lines[i]}" for i in range(start, end))
                            pointer = ' ' * (6 + (col or 0)) + '^'
                            err_msg = f"! YAML PARSE ERROR: {msg}\n\nContext:\n{snippet}\n{pointer}"
                        else:
                            err_msg = f"! YAML PARSE ERROR: {msg}"
                    else:
                        err_msg = f"! YAML PARSE ERROR: {msg}"
                    self.output_cli.setPlainText(err_msg)
                    self.output_pt.setPlainText("// YAML parse error: fix the input and try again.")
                    return
                # else data exists from auto-fix; continue

            except Exception as e:
                self.output_cli.setPlainText(f"! ERROR: {str(e)}")
                self.output_pt.setPlainText(f"// ERROR: {str(e)}")
                return

            try:
                pt_out = self.generate_full_topology_pt(data)
                # guard large outputs from setHtml crashes
                if len(pt_out) > 200000:
                    self.output_pt.setPlainText(pt_out)
                else:
                    self.output_pt.setHtml(self.format_pt_html(pt_out))
                cli_out = self.generate_full_topology_cli(data)
                if len(cli_out) > 200000:
                    self.output_cli.setPlainText(cli_out)
                else:
                    self.output_cli.setHtml(self.format_cli_html(cli_out))
            except Exception as e:
                self.output_cli.setPlainText(f"! GENERATION ERROR: {str(e)}")
                self.output_pt.setPlainText(f"// GENERATION ERROR: {str(e)}")
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
                self.output_cli.setHtml(self.format_cli_html(cli_out))
                try:
                    data = yaml.safe_load(text)
                    pt_out = generate_pt_builder_script(data, cli_out)
                    if not pt_out.strip():
                        pt_out = "// No PT-Builder script generated."
                    self.output_pt.setHtml(self.format_pt_html(pt_out))
                except Exception as e:
                    msg = f"// PT-Builder generation error: {e}"
                    self.output_pt.setHtml(self.format_pt_html(msg))
            else:
                err = f"! ERROR (exit {res.returncode}):\n{res.stderr.strip()}\n\nSTDOUT:\n{res.stdout.strip()}"
                self.output_cli.setHtml(self.format_cli_html(err))
                self.output_pt.setPlainText(f"// ERROR: see CLI tab for details")
        except Exception as e:
            self.output_cli.setPlainText(f"! EXECUTION ERROR: {str(e)}")
            self.output_pt.setPlainText(f"// EXECUTION ERROR: {str(e)}")
        finally:
            if os.path.exists(path):
                os.remove(path)

    # ── Custom Full Topology PT-Builder Generator ──
    def generate_full_topology_pt(self, data):
        """Generate PT-Builder script defensively.
        Normalizes device input, auto-creates defaults where missing, and skips malformed entries.
        Returns a string with comments explaining any fixes or warnings.
        """
        lines = []
        warnings = []
        pos = {}

        # Normalize input to a devices list
        devices = []
        if isinstance(data, list):
            devices = data
        elif isinstance(data, dict):
            dv = data.get('devices')
            if isinstance(dv, list):
                devices = dv
            else:
                # try to find the first list of dicts in the structure
                for v in data.values():
                    if isinstance(v, list) and v and all(isinstance(it, dict) for it in v):
                        devices = v
                        break
        if not devices:
            warnings.append("No 'devices' list found in input; synthesizing defaults.")

        # --- Fixed router positions ---
        routers = {"R1": (100, 100), "R2": (200, 200), "R3": (300, 100)}
        for r, (x, y) in routers.items():
            pos[r] = (x, y)

        # Clean device entries and index unnamed devices
        clean_devices = []
        missing_indices = []
        unnamed_counter = 1
        for i, d in enumerate(devices):
            if not isinstance(d, dict):
                warnings.append(f"Skipping non-dict device at index {i}.")
                continue
            hostname = d.get('hostname')
            if not hostname:
                hostname = f"unnamed_{unnamed_counter}"
                unnamed_counter += 1
                missing_indices.append((i, hostname))
            d.setdefault('_hostname', hostname)  # internal stable name
            clean_devices.append(d)
        devices = clean_devices
        # Collapse long lists of missing-hostname warnings for readability
        if missing_indices:
            if len(missing_indices) <= 8:
                for i, hn in missing_indices:
                    warnings.append(f"Device at index {i} missing hostname; assigned {hn}.")
            else:
                for i, hn in missing_indices[:6]:
                    warnings.append(f"Device at index {i} missing hostname; assigned {hn}.")
                warnings.append(f"{len(missing_indices)-6} more devices missing hostname were auto-named (unnamed_*).")

        # --- MLS list ---
        mls_list = [d for d in devices if d.get('type') == 'switch_l3']
        if not mls_list:
            # synthesize MLS1..MLS6
            for idx, (rname) in enumerate(['R1','R1','R2','R2','R3','R3'], start=1):
                side = 'left' if idx % 2 == 1 else 'right'
                mls_list.append({'hostname': f'MLS{idx}', 'type': 'switch_l3', 'router': rname, 'side': side})
            warnings.append('Synthesized MLS switches (MLS1..MLS6).')

        # helper: normalize interface names (expand G -> GigabitEthernet, F -> FastEthernet)
        def normalize_iface(ifname):
            if not ifname:
                return ifname
            s = str(ifname)
            if 'GigabitEthernet' in s or 'FastEthernet' in s or 'Serial' in s:
                return s
            # strip whitespace
            s = s.strip()
            m = re.match(r'^(?:G|Gi|Gig|g|gi)(.+)$', s)
            if m:
                return 'GigabitEthernet' + m.group(1)
            m = re.match(r'^(?:F|Fa|Fast|f|fa)(.+)$', s)
            if m:
                return 'FastEthernet' + m.group(1)
            return s

        # compute MLS positions (spaced wider)
        for mls in mls_list:
            hn = mls.get('hostname') or mls.get('_hostname')
            router = mls.get('router', '')
            side = mls.get('side', 'left')
            if router in routers:
                rx, ry = routers[router]
                if side == 'left':
                    pos[hn] = (rx - 50, ry + 150)
                else:
                    pos[hn] = (rx + 50, ry + 150)

        # --- ASW list ---
        asw_list = [d for d in devices if d.get('type') == 'switch']
        if not asw_list:
            asw_idx = 1
            for mls in mls_list:
                asw_list.append({'hostname': f'ASW{asw_idx}', 'type': 'switch', 'mls': mls.get('hostname') or mls.get('_hostname'), 'sub': 'left'})
                asw_idx += 1
                asw_list.append({'hostname': f'ASW{asw_idx}', 'type': 'switch', 'mls': mls.get('hostname') or mls.get('_hostname'), 'sub': 'right'})
                asw_idx += 1
            warnings.append('Synthesized ASW switches (2 per MLS).')

        # compute ASW positions (more spread)
        for asw in asw_list:
            hn = asw.get('hostname')
            mls_name = asw.get('mls')
            sub = asw.get('sub', 'left')
            if mls_name in pos:
                mx, my = pos[mls_name]
                if sub == 'left':
                    pos[hn] = (mx - 120, my + 250)
                else:
                    pos[hn] = (mx + 120, my + 250)

        # --- End devices ---
        end_devices = [d for d in devices if d.get('type') in ('pc','server')]
        if not end_devices:
            for asw in asw_list:
                idx = asw.get('hostname').replace('ASW','')
                end_devices.extend([
                    {'hostname': f'PC1_{idx}', 'type': 'pc', 'group': asw.get('hostname'), 'pos': 0},
                    {'hostname': f'PC2_{idx}', 'type': 'pc', 'group': asw.get('hostname'), 'pos': 1},
                    {'hostname': f'SRV1_{idx}', 'type': 'server', 'group': asw.get('hostname'), 'pos': 2},
                ])
            warnings.append('Synthesized end devices (2 PCs + 1 Server per ASW).')

        for d in end_devices:
            grp = d.get('group')
            offset = int(d.get('pos', 0)) if isinstance(d.get('pos', 0), int) or (isinstance(d.get('pos', 0), str) and str(d.get('pos',0)).isdigit()) else 0
            if grp in pos:
                bx, by = pos[grp]
                # spread end devices further and avoid negative coordinates
                x = max(20, bx - 110 + offset * 110)
                y = by + 150
                pos[d['hostname']] = (x, y)

        # Header warnings
        for w in warnings:
            lines.append(f'// WARNING: {w}')
        lines.append('')

        # Topology coordinates
        lines.append('// TOPOLOGY COORDINATES')
        lines.append(f"// Routers: {', '.join([f'{k} ({v[0]},{v[1]})' for k,v in routers.items()])}")
        lines.append('// MLS positions:')
        for mls in mls_list:
            hn = mls.get('hostname') or mls.get('_hostname')
            if hn in pos:
                x,y = pos[hn]
                lines.append(f'//   {hn}: ({x},{y})  // connects to {mls.get("router","?")} side={mls.get("side","?")}')
        lines.append('// ASW positions:')
        for asw in asw_list:
            hn = asw.get('hostname')
            if hn in pos:
                x,y = pos[hn]
                lines.append(f'//   {hn}: ({x},{y})  // mls={asw.get("mls","?")} sub={asw.get("sub","?")}')
        lines.append('')

        # STEP 1: Core Router Mesh
        lines.append('// STEP 1: Core Router Mesh\\n')
        for r in ['R1','R2','R3']:
            x,y = pos.get(r, routers.get(r,(0,0)))
            lines.append(f'addDevice("{r}", "2911", {x}, {y});')
        lines.append('')

        # STEP 2: Expansion Modules
        lines.append('// STEP 2: Expansion Modules\\n')
        for r in ['R1','R2','R3']:
            lines.append(f'addModule("{r}", 0, "HWIC-2T");')
            lines.append(f'addModule("{r}", 1, "HWIC-2T");')
        lines.append('addModule("R2", 2, "HWIC-2T");')
        lines.append('addModule("R3", 2, "HWIC-2T");')
        lines.append('')

        # STEP 3: Distribution Switches (MLS)
        lines.append('// STEP 3: Distribution Switches\\n')
        for mls in mls_list:
            hn = mls.get('hostname') or mls.get('_hostname')
            if hn in pos:
                x,y = pos[hn]
                lines.append(f'addDevice("{hn}", "3560-24PS", {x}, {y});')
        lines.append('')

        # Core to Distribution Links
        lines.append('// Core to Distribution Links\\n')
        links = data.get('links', []) if isinstance(data, dict) else []
        used_links = False
        for link in links:
            try:
                s = link.get('source')
                t = link.get('target')
                sdev, sIf = s.split(':')
                tdev, tIf = t.split(':')
                sIf = normalize_iface(sIf)
                tIf = normalize_iface(tIf)
                if sdev in routers and tdev.startswith('MLS'):
                    lines.append(f'addLink("{sdev}", "{sIf}", "{tdev}", "{tIf}", "straight");')
                    used_links = True
            except Exception:
                continue
        if not used_links:
            for mls in mls_list:
                r = mls.get('router')
                if r in routers:
                    lines.append(f'addLink("{r}", "{normalize_iface("G0/0")}", "{mls.get("hostname","?")}", "{normalize_iface("G0/1")}", "straight");')
        lines.append('')

        # STEP 4: EtherChannel Pair Links
        lines.append('// STEP 4: EtherChannel Pair Links\\n')
        for r in ['R1','R2','R3']:
            left = next((m.get('hostname') for m in mls_list if m.get('router')==r and m.get('side')=='left'), None)
            right = next((m.get('hostname') for m in mls_list if m.get('router')==r and m.get('side')=='right'), None)
            if left and right:
                lines.append(f'addLink("{left}", "{normalize_iface("G0/23")}", "{right}", "{normalize_iface("G0/23")}", "straight");')
                lines.append(f'addLink("{left}", "{normalize_iface("G0/24")}", "{right}", "{normalize_iface("G0/24")}", "straight");')
        lines.append('')

        # STEP 5: Access Switches & End Devices
        lines.append('// STEP 5: Access Switches & End Devices\\n')
        for asw in asw_list:
            hn = asw.get('hostname')
            if hn in pos:
                x,y = pos[hn]
                lines.append(f'addDevice("{hn}", "2960-24TT", {x}, {y});')
        for dev in end_devices:
            hn = dev.get('hostname')
            if hn in pos:
                x,y = pos[hn]
                if dev.get('type') == 'pc':
                    lines.append(f'addDevice("{hn}", "PC-PT", {x}, {y});')
                else:
                    lines.append(f'addDevice("{hn}", "Server-PT", {x}, {y});')
        lines.append('')

        # Distribution to Access Links
        lines.append('// Distribution to Access Links\\n')
        used = False
        for link in links:
            try:
                sdev = link.get('source').split(':')[0]
                tdev = link.get('target').split(':')[0]
                if sdev.startswith('MLS') and tdev.startswith('ASW'):
                    sIf = normalize_iface(link['source'].split(':')[1])
                    tIf = normalize_iface(link['target'].split(':')[1])
                    lines.append(f'addLink("{sdev}", "{sIf}", "{tdev}", "{tIf}", "straight");')
                    used = True
            except Exception:
                continue
        if not used:
            for asw in asw_list:
                m = asw.get('mls')
                if m:
                    lines.append(f'addLink("{m}", "{normalize_iface("G0/2")}", "{asw.get("hostname","?")}", "{normalize_iface("G0/1")}", "straight");')
        lines.append('')

        # Access to End Devices Links
        lines.append('// Access to End Devices Links\\n')
        used = False
        for link in links:
            try:
                sdev = link.get('source').split(':')[0]
                tdev = link.get('target').split(':')[0]
                if sdev.startswith('ASW') and not tdev.startswith('DSW'):
                    s_if = normalize_iface(link.get('source').split(":")[1])
                    t_if = normalize_iface(link.get('target').split(":")[1])
                    lines.append(f'addLink("{sdev}", "{s_if}", "{tdev}", "{t_if}", "straight");')
                    used = True
            except Exception:
                continue
        if not used:
            for dev in end_devices:
                grp = dev.get('group')
                if grp:
                    lines.append(f'addLink("{grp}", "{normalize_iface("F0/1")}", "{dev.get("hostname","?")}", "{normalize_iface("F0")}", "straight");')
        lines.append('')

        # STEP 6: Host Configuration
        lines.append('// STEP 6: Host Configuration\\n')
        def subnet_index(dev):
            grp = str(dev.get('group') or dev.get('hostname') or '')
            m = re.search(r'(\d+)', grp)
            if not m:
                return 1
            n = int(m.group(1))
            return min(3, max(1, ((n - 1) // 4) + 1))

        def host_suffix(dev):
            hn = str(dev.get('hostname') or '')
            m = re.search(r'_(\d+)$', hn)
            if m and dev.get('type') == 'server':
                return 100
            if m and hn.startswith('PC1_'):
                return 11
            if m and hn.startswith('PC2_'):
                return 12
            pos = dev.get('pos')
            if str(pos) == '0':
                return 11
            if str(pos) == '1':
                return 12
            return 100

        for dev in end_devices:
            if dev.get('type') in ('pc', 'server', 'laptop'):
                subnet = subnet_index(dev)
                suffix = host_suffix(dev)
                ip = dev.get('ip') or f"192.168.{subnet}.{suffix}"
                mask = dev.get('mask', '255.255.255.0')
                gateway = dev.get('gateway') or f"192.168.{subnet}.1"
                dns = dev.get('dns') or f"192.168.{subnet}.100"
                lines.append(f'configurePcIp("{dev.get("hostname","?")}", false, "{ip}", "{mask}", "{gateway}", "{dns}");')
                ipv6 = dev.get('ipv6') or dev.get('ipv6_address') or f"2001:db8:{subnet}::{suffix}/64"
                ipv6_gw = dev.get('ipv6_gateway') or f"2001:db8:{subnet}::1"
                ipv6_dns = dev.get('ipv6_dns') or f"2001:db8:{subnet}::100"
                lines.append(f'// IPv6: {ipv6} | gw {ipv6_gw} | dns {ipv6_dns}')
        lines.append('')

        # STEP 7: Router CLI Injection
        lines.append('// STEP 7: Router CLI Injection\\n')
        for d in devices:
            if d.get('type') == 'router':
                hostname = d.get('hostname') or d.get('_hostname')
                ospf = d.get('ospf', {})
                pid = ospf.get('process_id', 1)
                rid = ospf.get('router_id', '1.1.1.1')
                # assemble CLI lines and serialize for safe JS embedding
                cli_lines = ['no', 'enable', 'conf t', f'hostname {hostname}', f'router ospf {pid}', f'router-id {rid}', 'exit', 'end', 'write mem']
                cli = '\\n'.join(cli_lines)
                js_cli = json.dumps(cli)
                lines.append(f'configureIosDevice("{hostname}", {js_cli});')
        lines.append('')

        # STEP 8: Switch CLI Injection
        lines.append('// STEP 8: Switch CLI Injection\\n')
        for d in devices:
            if d.get('type') in ('switch', 'switch_l3'):
                hostname = d.get('hostname') or d.get('_hostname')
                vlans = d.get('vlans', [])
                cli_lines = ['no', 'enable', 'conf t', f'hostname {hostname}']
                for vlan in vlans:
                    vid = vlan.get('id', '')
                    vname = vlan.get('name', '')
                    if vid:
                        cli_lines.append(f'vlan {vid}')
                        if vname:
                            cli_lines.append(f'name {vname}')
                        cli_lines.append('exit')
                cli_lines.extend(['end', 'write mem'])
                cli = '\\n'.join(cli_lines)
                js_cli = json.dumps(cli)
                lines.append(f'configureIosDevice("{hostname}", {js_cli});')

        return "\n".join(lines)

    def generate_full_topology_cli(self, data):
        # Defensive CLI summary: handle malformed inputs gracefully
        devices = []
        if isinstance(data, list):
            devices = data
        elif isinstance(data, dict):
            dv = data.get('devices')
            if isinstance(dv, list):
                devices = dv
            else:
                # try to find a list of device dicts
                for v in data.values():
                    if isinstance(v, list) and v and all(isinstance(it, dict) for it in v):
                        devices = v
                        break
        lines = ["! Full Topology CLI Summary"]
        for i, d in enumerate(devices):
            if not isinstance(d, dict):
                lines.append(f"! Skipping malformed device at index {i}")
                continue
            hn = d.get('hostname', f'unnamed_{i}')
            dtype = d.get('type', 'unknown')
            lines.append(f"! {hn} ({dtype})")
        return "\n".join(lines)

    # Syntax highlighting (unchanged)
    def format_cli_html(self, cli_text):
        esc = html.escape(cli_text)
        placeholders = []
        def store(html_snip):
            idx = len(placeholders)
            placeholders.append(html_snip)
            return f"@@PH{idx}@@"
        text = esc
        text = re.sub(r'(^|\n)([ \t]*[!#].*)',
                      lambda m: m.group(1) + store(f"<span style='color:{C['syn_comment']};'>{m.group(2)}</span>"), text)
        text = re.sub(r'(&quot;.*?&quot;|&#x27;.*?&#x27;)',
                      lambda m: store(f"<span style='color:{C['syn_string']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)',
                      lambda m: store(f"<span style='color:{C['syn_ip']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'([0-9a-fA-F:]+:+[0-9a-fA-F:\/]+)',
                      lambda m: store(f"<span style='color:{C['syn_ip']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'(\b\d+\b)',
                      lambda m: store(f"<span style='color:{C['syn_number']};'>{m.group(1)}</span>"), text)
        keywords = ['hostname','interface','vlan','router','network','ip route','ipv6 route',
                    'crypto key generate rsa','ip ssh version','username','line vty',
                    'standby','switchport','no shutdown','exit','ip dhcp pool','ipv6 dhcp pool','ip nat']
        for kw in sorted(keywords, key=lambda x: -len(x)):
            pattern = re.escape(kw)
            text = re.sub(r'(?i)(' + pattern + r')',
                          lambda m: store(f"<span style='color:{C['syn_cmd']}; font-weight:700;'>{m.group(1)}</span>"), text)
        text = re.sub(r'(?m)^([ \t]*description\b)',
                      lambda m: store(f"<span style='color:{C['syn_desc']}; font-weight:600;'>{m.group(1)}</span>"), text)
        text = re.sub(r'(ERROR|FAIL|INVALID)',
                      lambda m: store(f"<span style='color:{C['syn_error']}; font-weight:700;'>{m.group(1)}</span>"), text)
        def restore(match):
            idx = int(match.group(1))
            return placeholders[idx]
        html_out = re.sub(r'@@PH(\d+)@@', restore, text)
        return f"<div style='background:{C['bg_terminal']}; padding:8px; border-radius:6px; font-family: monospace; white-space:pre;'>{html_out}</div>"

    def format_pt_html(self, pt_text):
        esc = html.escape(pt_text)
        placeholders = []
        def store(html_snip):
            idx = len(placeholders)
            placeholders.append(html_snip)
            return f"@@PH{idx}@@"
        text = esc
        text = re.sub(r'(^|\n)([ \t]*//.*)',
                      lambda m: m.group(1) + store(f"<span style='color:{C['syn_comment']};'>{m.group(2)}</span>"), text)
        text = re.sub(r'(/\*.*?\*/)',
                      lambda m: store(f"<span style='color:{C['syn_comment']};'>{m.group(1)}</span>"), text, flags=re.S)
        text = re.sub(r'(&quot;.*?&quot;|&#x27;.*?&#x27;)',
                      lambda m: store(f"<span style='color:{C['syn_string']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'(\b\d+\b)',
                      lambda m: store(f"<span style='color:{C['syn_number']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)',
                      lambda m: store(f"<span style='color:{C['syn_ip']};'>{m.group(1)}</span>"), text)
        for fn_color, fn_list in [(C['syn_ip'], ['addDevice']), (C['primary'], ['addLink']), (C['syn_func'], ['configureIosDevice'])]:
            for fn in fn_list:
                text = re.sub(r'(' + re.escape(fn) + r')(?=\s*\()',
                              lambda m, col=fn_color: store(f"<span style='color:{col}; font-weight:700;'>{m.group(1)}</span>"), text)
        js_kw = ['var','let','const','function','return']
        for kw in js_kw:
            text = re.sub(r'\b' + kw + r'\b',
                          lambda m: store(f"<span style='color:{C['syn_js_kw']}; font-weight:600;'>{m.group(0)}</span>"), text)
        text = re.sub(r'(Error|Exception)',
                      lambda m: store(f"<span style='color:{C['syn_error']}; font-weight:700;'>{m.group(1)}</span>"), text)
        def restore(match):
            idx = int(match.group(1))
            return placeholders[idx]
        html_out = re.sub(r'@@PH(\d+)@@', restore, text)
        return f"<div style='background:{C['bg_input']}; padding:8px; border-radius:6px; font-family: monospace; white-space:pre;'>{html_out}</div>"

    def format_yaml_html(self, yaml_text):
        esc = html.escape(yaml_text)
        placeholders = []
        def store(html_snip):
            idx = len(placeholders)
            placeholders.append(html_snip)
            return f"@@PH{idx}@@"
        text = esc
        text = re.sub(r'(^|\n)([ \t]*#.*)',
                      lambda m: m.group(1) + store(f"<span style='color:{C['syn_comment']};'>{m.group(2)}</span>"), text)
        text = re.sub(r'(&quot;.*?&quot;|&#x27;.*?&#x27;)',
                      lambda m: store(f"<span style='color:{C['syn_string']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'(?m)^(\s*)([\w\-\.\/:]+):',
                      lambda m: m.group(1) + store(f"<span style='color:{C['primary']}; font-weight:700;'>{m.group(2)}</span>") + ":", text)
        text = re.sub(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)',
                      lambda m: store(f"<span style='color:{C['syn_ip']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'(\b\d+\b)',
                      lambda m: store(f"<span style='color:{C['syn_number']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'\b(true|false|null|yes|no)\b',
                      lambda m: store(f"<span style='color:{C['syn_func']}; font-weight:600;'>{m.group(1)}</span>"), text)
        text = re.sub(r'\b(error|fail|invalid)\b',
                      lambda m: store(f"<span style='color:{C['syn_error']}; font-weight:700;'>{m.group(1)}</span>"), text)
        def restore(match):
            idx = int(match.group(1))
            return placeholders[idx]
        html_out = re.sub(r'@@PH(\d+)@@', restore, text)
        return f"<div style='background:{C['bg_input']}; padding:8px; border-radius:6px; font-family: monospace; white-space:pre;'>{html_out}</div>"


class ExtractTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(8)

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
            '<div style="padding: 10px 16px; color: #a6adc8; font-size: 12px; line-height: 1.7;">'
            "<b style='color:#cdd6f4;'>1.</b> Click <b>Copy JS</b> to copy <code>pt_analyzer.js</code><br>"
            "<b style='color:#cdd6f4;'>2.</b> In Packet Tracer: <b>Extensions \u2192 Scripting \u2192 Edit File Script Module</b><br>"
            "<b style='color:#cdd6f4;'>3.</b> Paste the script, click <b>Run</b><br>"
            "<b style='color:#cdd6f4;'>4.</b> Copy all output from the PT console (Ctrl+A, Ctrl+C)<br>"
            "<b style='color:#cdd6f4;'>5.</b> Paste it into the text area below<br>"
            "<b style='color:#cdd6f4;'>6.</b> Click <b>Parse to YAML</b> to extract structured topology"
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

        btn_bar = QWidget()
        btn_bar.setObjectName("btn_bar_extract")
        bb = QHBoxLayout(btn_bar)
        bb.setContentsMargins(14, 8, 14, 8)
        self.btn_parse = QPushButton("\u2699  Parse to YAML")
        self.btn_parse.setObjectName("btn_generate")
        self.btn_parse.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_parse.clicked.connect(self.parse_output)
        bb.addWidget(self.btn_parse)
        self.btn_clear = QPushButton("\u21BA  Clear")
        self.btn_clear.setObjectName("btn_reset")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self.clear_all)
        bb.addWidget(self.btn_clear)
        self.btn_export_yaml = QPushButton("\U0001F4E4  Export YAML")
        self.btn_export_yaml.setObjectName("copy_btn")
        self.btn_export_yaml.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_yaml.clicked.connect(self.export_yaml)
        self.btn_export_yaml.setEnabled(False)
        bb.addWidget(self.btn_export_yaml)
        bb.addStretch()
        paste_layout.addWidget(btn_bar)

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
            self.output_area.setHtml(self.format_yaml_html(yaml_out))
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

    def clear_all(self):
        self.input_area.clear()
        self.output_area.clear()
        self.badge_paste.setText("0 lines")
        self.badge_yaml.setText("0 lines")
        self.btn_export_yaml.setEnabled(False)
        self.btn_copy_yaml.setEnabled(False)

    def import_yaml(self):
        self.clear_all()

    def reset_template(self):
        self.clear_all()

    def run_generator(self):
        self.parse_output()

    def format_yaml_html(self, yaml_text):
        esc = html.escape(yaml_text)
        placeholders = []
        def store(html_snip):
            idx = len(placeholders)
            placeholders.append(html_snip)
            return f"@@PH{idx}@@"
        text = esc
        text = re.sub(r'(^|\n)([ \t]*#.*)',
                      lambda m: m.group(1) + store(f"<span style='color:{C['syn_comment']};'>{m.group(2)}</span>"), text)
        text = re.sub(r'(&quot;.*?&quot;|&#x27;.*?&#x27;)',
                      lambda m: store(f"<span style='color:{C['syn_string']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'(?m)^(\s*)([\w\-\.\/:]+):',
                      lambda m: m.group(1) + store(f"<span style='color:{C['primary']}; font-weight:700;'>{m.group(2)}</span>") + ":", text)
        text = re.sub(r'(\b(?:\d{1,3}\.){3}\d{1,3}\b)',
                      lambda m: store(f"<span style='color:{C['syn_ip']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'(\b\d+\b)',
                      lambda m: store(f"<span style='color:{C['syn_number']};'>{m.group(1)}</span>"), text)
        text = re.sub(r'\b(true|false|null|yes|no)\b',
                      lambda m: store(f"<span style='color:{C['syn_func']}; font-weight:600;'>{m.group(1)}</span>"), text)
        text = re.sub(r'\b(error|fail|invalid)\b',
                      lambda m: store(f"<span style='color:{C['syn_error']}; font-weight:700;'>{m.group(1)}</span>"), text)
        def restore(match):
            idx = int(match.group(1))
            return placeholders[idx]
        html_out = re.sub(r'@@PH(\d+)@@', restore, text)
        return f"<div style='background:{C['bg_input']}; padding:8px; border-radius:6px; font-family: monospace; white-space:pre;'>{html_out}</div>"


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

        body = QWidget()
        body.setObjectName("body")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

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

        self.content_container = QWidget()
        self.content_container.setObjectName("content")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.tool_stack = QStackedWidget()
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

        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.run_current)
        self.apply_style()

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

            #btn_generate {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c['primary']}, stop:1 {c['primary_hover']});
                border: none; color: {c['bg_dark']}; font-weight: 600; font-size: 13px;
                padding: 0 18px; border-radius: 6px; height: 36px;
            }}
            #btn_generate:hover {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c['primary_hover']}, stop:1 {c['primary']}); }}
            #btn_reset {{
                background: transparent; border: 1px solid {c['primary']};
                color: {c['primary']}; font-weight: 600; font-size: 13px;
                padding: 0 16px; border-radius: 6px; height: 36px;
            }}
            #btn_reset:hover {{ background: rgba(203,166,247,0.12); color: {c['text_primary']}; }}
            #icon_btn {{
                background: {c['bg_surface_light']}; border: 1px solid {c['border']};
                color: {c['text_secondary']}; border-radius: 6px; height: 36px; font-size: 15px;
            }}
            #icon_btn:hover {{ border-color: {c['border_hover']}; color: {c['text_primary']}; }}

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

            #badge_status, #badge_lines {{
                font-size: 10.5px; font-weight: 600; font-family: 'Courier New', monospace;
                padding: 2px 10px; border-radius: 20px; border: 1px solid {c['border']};
                margin-left: 6px;
            }}
            #badge_status {{
                background: rgba(0,0,0,0.15); color: {c['text_muted']};
            }}
            #badge_status[status="valid"] {{
                background: rgba(166,227,161,0.15); color: {c['success']};
                border-color: rgba(166,227,161,0.3);
            }}
            #badge_status[status="invalid"] {{
                background: rgba(243,139,168,0.15); color: {c['error']};
                border-color: rgba(243,139,168,0.3);
            }}
            #badge_lines {{
                background: {c['bg_dark']}; color: {c['text_secondary']};
            }}

            #tab_btn {{
                background: transparent; border: none; border-bottom: 2px solid transparent;
                color: {c['text_secondary']}; font-size: 13px; font-weight: 600;
                padding: 0 16px; height: 100%; min-height: 44px;
            }}
            #tab_btn:hover {{ color: {c['text_primary']}; }}
            #tab_btn[active="true"] {{
                color: {c['primary']}; border-bottom-color: {c['primary']};
            }}

            #copy_btn {{
                background: {c['bg_surface_light']}; border: 1px solid {c['border']};
                color: {c['text_primary']}; font-size: 12px; font-weight: 600;
                padding: 0 14px; border-radius: 6px; height: 32px;
            }}
            #copy_btn:hover {{ border-color: {c['text_muted']}; }}

            #input_editor {{
                background: {c['bg_input']}; color: {c['text_primary']};
                border: none; padding: 16px; font-size: 13px; line-height: 1.6;
            }}
            #output_cli {{
                background: {c['bg_terminal']}; color: {c['success']};
                border: none; padding: 16px; font-size: 13px; line-height: 1.6;
            }}
            #output_pt {{
                background: {c['bg_input']}; color: {c['text_primary']};
                border: none; padding: 16px; font-size: 13px; line-height: 1.6;
            }}

            QSplitter::handle {{
                background: transparent; margin: 0; height: 8px;
            }}
            QSplitter::handle:vertical {{
                image: none; border: none;
            }}

            QScrollBar:vertical {{
                width: 8px; background: {c['bg_dark']};
            }}
            QScrollBar::handle:vertical {{
                background: {c['border']}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {c['border_hover']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

            #statusbar_widget {{
                background: {c['bg_surface']}; border-top: 1px solid {c['border']};
            }}
            #st_tool {{ font-weight: 600; color: {c['text_primary']}; }}
            #st_sep {{ color: {c['text_muted']}; }}
            #st_cat {{ color: {c['primary']}; font-weight: 600; }}
            #st_keys {{ color: {c['text_muted']}; }}
            #st_saved {{ color: {c['text_secondary']}; font-size: 12px; }}

            #welcome_title {{
                font-size: 48px; font-weight: 800; color: {c['border']};
            }}
            #welcome_subtitle {{
                color: {c['border_hover']}; font-size: 13px;
            }}

            #js_view {{
                background: {c['bg_terminal']}; color: {c['text_primary']};
                border: none; padding: 12px; font-size: 12px; line-height: 1.6;
            }}
            #extract_instructions {{
                background: {c['bg_surface']}; border-bottom: 1px solid {c['border']};
            }}
            #btn_bar_extract {{
                background: {c['bg_dark']}; border-top: 1px solid {c['border']};
            }}

            QToolTip {{
                background: {c['bg_surface_light']}; color: {c['text_primary']};
                border: 1px solid {c['border']}; padding: 4px 8px; border-radius: 4px;
                font-size: 12px;
            }}
        """)


def _silent_qt_msg(msg_type, context, msg):
    msg = str(msg)
    # suppress noisy Qt messages we don't care about
    if "Unknown property" in msg or "kf.iconthemes" in msg:
        return
    # call previous handler if it exists
    prev = getattr(_silent_qt_msg, 'prev', None)
    if callable(prev):
        try:
            prev(msg_type, context, msg)
        except Exception:
            # never let the message handler crash the app
            pass

def _sigint_handler(signum, frame):
    """Handle Ctrl+C (SIGINT) in the terminal and quit the Qt application gracefully."""
    app = QApplication.instance()
    if app is not None:
        QTimer.singleShot(0, app.quit)
    else:
        sys.exit(0)


if __name__ == "__main__":
    # Install quiet Qt message filter
    _silent_qt_msg.prev = qInstallMessageHandler(_silent_qt_msg)
    # Enable SIGINT -> quit behavior
    signal.signal(signal.SIGINT, _sigint_handler)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = KeystoneGUI()
    w.show()
    # Run the Qt event loop; Ctrl+C in terminal will now close the app
    sys.exit(app.exec())
