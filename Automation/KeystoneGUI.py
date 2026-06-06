import sys
import os
import subprocess
import tempfile
import yaml
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QLabel, QFileDialog, QSplitter,
    QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtGui import QFont, QColor, QPalette, QGuiApplication
from PyQt6.QtCore import Qt, QTimer, QSize

# --- PERMANENT THEME: Catppuccin Mocha ---
MOCHA = {
    "base": "#1e1e2e", "mantle": "#181825", "crust": "#11111b",
    "text": "#cdd6f4", "subtext1": "#bac2de", "subtext0": "#a6adc8",
    "surface0": "#313244", "surface1": "#45475a", "surface2": "#585b70",
    "mauve": "#cba6f7", "blue": "#89b4fa", "red": "#f38181"
}

# --- TEMPLATES (DUAL-STACK READY) ---
TEMPLATES = {
    "VLAN Weaver": """# VLAN Weaver: Layer 2 Segmentation
- hostname: DSW-1
  vlans:
    - name: Management
      id: 10
    - name: Sales
    - name: Guest
""",
    "OSPF Pathmaker": """# OSPF Pathmaker: Dual-Stack Routing
- hostname: Core-R1
  router_id: 1.1.1.1
  process_id: 1
  ipv6_process_id: 1
  use_interface_config: true
  interfaces:
    - name: GigabitEthernet0/0
      ip_address: 192.168.1.1
      subnet_mask: 255.255.255.0
      ipv6_address: "2001:db8:1::1/64"
      area: 0
      ipv6_area: 0
    - name: GigabitEthernet0/1
      ip_address: 10.0.0.1
      subnet_mask: 255.255.255.252
      ipv6_address: "2001:db8:0:1::1/64"
      area: 0
      ipv6_area: 0
""",
    "ASA Shield": """# ASA Shield: Next-Gen Firewall
- hostname: ASA-FW-01
  interfaces:
    - name: GigabitEthernet0/0
      nameif: inside
      security_level: 100
      ip: 192.168.1.1
      mask: 255.255.255.0
      ipv6: "2001:db8:1::1"
  objects:
    - name: INTERNAL_V4
      subnet: 192.168.1.0
      mask: 255.255.255.0
    - name: INTERNAL_V6
      ipv6_subnet: "2001:db8:1::/64"
  nats:
    - obj_name: INTERNAL_V4
      type: dynamic
      translated_interface: outside
  acls:
    - access_list: OUTSIDE_IN
      action: permit
      protocol: tcp
      source: any
      destination: any
      service: eq 443
  access_groups:
    OUTSIDE_IN: outside
""",
    "BGP Conductor": """# BGP Conductor: Dual-Stack Peering
- hostname: Edge-R1
  as_number: 65001
  router_id: 1.1.1.1
  neighbors:
    - ip: 10.0.0.2
      remote_as: 65002
      description: ISP1_V4
    - ip: "2001:db8:0:1::2"
      remote_as: 65002
      description: ISP1_V6
  networks:
    - network: 192.168.1.0
      mask: 255.255.255.0
    - network: "2001:db8:1::"
      mask: 64
""",
    "DHCP Allocator": """# DHCP Allocator: IPv4 Pools
- hostname: Core-Switch
  excluded:
    - start: 192.168.10.1
      end: 192.168.10.10
  pools:
    - name: DATA_POOL
      network: 192.168.10.0
      mask: 255.255.255.0
      gateway: 192.168.10.1
      dns: 8.8.8.8
""",
    "EIGRP Catalyst": """# EIGRP Catalyst: Dual-Stack
- hostname: R1
  as_number: 100
  ipv6_as_number: 100
  router_id: 1.1.1.1
  networks:
    - network: 192.168.1.0
      mask: 255.255.255.0
  interfaces:
    - name: GigabitEthernet0/0
      ipv6_enabled: true
""",
    "HSRP Sentinel": """# HSRP Sentinel: High Availability
- hostname: Core-R1
  interfaces:
    - name: VLAN 10
      vlan_id: 10
      ip: 192.168.1.2
      mask: 255.255.255.0
      hsrp_ip: 192.168.1.1
      ipv6: "2001:db8:1::2"
      hsrp_ipv6: 2001:db8:1::1
      priority: 110
      preempt: true
""",
    "IP Architect": """# IP Architect: Inventory
- hostname: Core-R1
  interfaces:
    - name: Gi0/0
      ip: 192.168.1.1
      mask: 255.255.255.0
      ipv6: "2001:db8:1::1"
- random_ips:
    count: 5
    ipv6: false
""",
    "NAT Portal": """# NAT Portal: Mapping
- hostname: Gateway-R1
  inside_interfaces: [GigabitEthernet0/1]
  outside_interfaces: [GigabitEthernet0/0]
  static_nats:
    - inside_ip: 192.168.1.50
      outside_ip: 203.0.113.10
""",
    "SSH Locksmith": """# SSH Locksmith: Hardening
- hostname: Core-R1
  domain_name: keystone.local
  username: admin
  password: SecretPassword123
  key_size: 2048
""",
    "Static Anchor": """# Static Anchor: Manual Routes
- hostname: R1
  routes:
    - network: 0.0.0.0
      mask: 0.0.0.0
      next_hop: 10.0.0.1
    - network: "::/0"
      mask: 0
      next_hop: "2001:db8::1"
""",
    "CIDR Architect": """# CIDR Architect: VLSM
- network: 172.16.0.0/16
  subnets:
    - name: MGMT
      size: 50
    - name: PROD
      size: 500
- network: "fc00:cafe::/48"
  subnets:
    - name: MGMT_V6
      size: 1
"""
}

SCRIPTS = {
    "VLAN Weaver": "vlan_weaver.py",
    "OSPF Pathmaker": "ospf_pathmaker.py",
    "ASA Shield": "asa_shield.py",
    "BGP Conductor": "bgp_conductor.py",
    "DHCP Allocator": "dhcp_allocator.py",
    "EIGRP Catalyst": "eigrp_catalyst.py",
    "HSRP Sentinel": "hsrp_sentinel.py",
    "IP Architect": "ip_architect.py",
    "NAT Portal": "nat_portal.py",
    "SSH Locksmith": "ssh_locksmith.py",
    "Static Anchor": "static_anchor.py",
    "CIDR Architect": "cidr_architect.py"
}

CATEGORIES = {
    "ROUTING": ["OSPF Pathmaker", "BGP Conductor", "EIGRP Catalyst", "Static Anchor"],
    "SECURITY": ["ASA Shield", "SSH Locksmith", "NAT Portal"],
    "SERVICES": ["DHCP Allocator", "HSRP Sentinel"],
    "UTILITIES": ["VLAN Weaver", "IP Architect", "CIDR Architect"]
}

class GeneratorTab(QWidget):
    def __init__(self, name, script_name, parent=None):
        super().__init__(parent)
        self.name = name
        self.script_path = os.path.join("generators", script_name)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(1)

        # Editor Area
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(15, 10, 15, 10)
        
        header = QHBoxLayout()
        editor_label = QLabel("YAML CONFIGURATION")
        editor_label.setStyleSheet("font-weight: bold; font-size: 10px; opacity: 0.7;")
        header.addWidget(editor_label)
        header.addStretch()
        
        for action in ["Import", "Export", "Reset"]:
            btn = QPushButton(action)
            btn.setFixedWidth(65)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(getattr(self, f"{action.lower()}_yaml" if action != "Reset" else "reset_template"))
            header.addWidget(btn)
        
        editor_layout.addLayout(header)
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(False)
        self.editor.setPlainText(TEMPLATES.get(self.name, ""))
        self.editor.setFont(QFont("Courier New", 11))
        editor_layout.addWidget(self.editor)

        # Output Area
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        output_layout.setContentsMargins(15, 10, 15, 15)
        
        out_header = QHBoxLayout()
        out_label = QLabel("GENERATED OUTPUT")
        out_label.setStyleSheet("font-weight: bold; font-size: 10px; opacity: 0.7;")
        out_header.addWidget(out_label)
        out_header.addStretch()
        
        self.btn_copy = QPushButton("Copy")
        self.btn_copy.setFixedWidth(65)
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.clicked.connect(self.copy_output)
        out_header.addWidget(self.btn_copy)
        output_layout.addLayout(out_header)
        
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Courier New", 11))
        output_layout.addWidget(self.output_area)

        self.splitter.addWidget(editor_widget)
        self.splitter.addWidget(output_widget)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        layout.addWidget(self.splitter)

        # Run Button
        self.btn_run = QPushButton(f"RUN {self.name.upper()}")
        self.btn_run.setFixedHeight(45)
        self.btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run.clicked.connect(self.run_generator)
        self.btn_run.setStyleSheet(f"background: #007acc; color: white; font-weight: bold; margin: 10px 15px; border-radius: 4px;")
        layout.addWidget(self.btn_run)

    def import_yaml(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open YAML", "", "YAML (*.yaml *.yml)")
        if file:
            with open(file, 'r') as f: self.editor.setPlainText(f.read())

    def export_yaml(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save YAML", "", "YAML (*.yaml *.yml)")
        if file:
            with open(file, 'w') as f: f.write(self.editor.toPlainText())

    def reset_template(self): self.editor.setPlainText(TEMPLATES.get(self.name, ""))

    def copy_output(self):
        QGuiApplication.clipboard().setText(self.output_area.toPlainText())
        self.btn_copy.setText("Copied!")
        QTimer.singleShot(2000, lambda: self.btn_copy.setText("Copy"))

    def run_generator(self):
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode='w') as tmp:
            tmp.write(self.editor.toPlainText())
            path = tmp.name
        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.abspath("tools")
            res = subprocess.run([sys.executable, self.script_path, "--file", path], capture_output=True, text=True, env=env)
            if res.returncode == 0:
                self.output_area.setPlainText(res.stdout)
            else:
                self.output_area.setPlainText(f"ERROR:\n{res.stderr}\n\nSTDOUT:\n{res.stdout}")
        except Exception as e:
            self.output_area.setPlainText(f"EXECUTION ERROR: {str(e)}")
        finally:
            if os.path.exists(path): os.remove(path)

class KeystoneGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keystone Automation")
        self.resize(1150, 900)
        self.tool_widgets = {}
        self.init_ui()

    def init_ui(self):
        cw = QWidget()
        self.setCentralWidget(cw)
        main = QHBoxLayout(cw)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        
        # Sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setObjectName("sidebar")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)
        
        # Sidebar Header
        sb_header = QWidget()
        sb_header.setFixedHeight(70)
        sb_header_layout = QVBoxLayout(sb_header)
        title = QLabel("KEYSTONE")
        title.setStyleSheet(f"font-weight: bold; font-size: 18px; color: {MOCHA['mauve']}; letter-spacing: 1px;")
        subtitle = QLabel("Network Automation Engine")
        subtitle.setStyleSheet(f"font-size: 9px; color: {MOCHA['subtext0']}; text-transform: uppercase;")
        sb_header_layout.addWidget(title)
        sb_header_layout.addWidget(subtitle)
        sb_layout.addWidget(sb_header)

        # Tool List with Categories
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        self.tool_layout = QVBoxLayout(scroll_content)
        self.tool_layout.setContentsMargins(0, 10, 0, 10)
        self.tool_layout.setSpacing(2)

        for cat, tools in CATEGORIES.items():
            cat_label = QLabel(cat)
            cat_label.setStyleSheet("padding: 15px 15px 5px 15px; font-size: 9px; font-weight: bold; color: #585b70;")
            self.tool_layout.addWidget(cat_label)
            
            for tool in tools:
                btn = QPushButton(tool)
                btn.setFixedHeight(38)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setObjectName("tool_btn")
                btn.clicked.connect(lambda ch, t=tool: self.show_tool(t))
                self.tool_layout.addWidget(btn)

        self.tool_layout.addStretch()
        scroll.setWidget(scroll_content)
        sb_layout.addWidget(scroll)
        main.addWidget(sidebar)

        # Content Container (Right Side)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        main.addWidget(self.content_container)

        # Top Bar (Header) - now part of the layout, not floating/overlapping
        self.header = QWidget()
        self.header.setFixedHeight(70)
        self.header.setObjectName("header")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(25, 0, 25, 0)
        
        self.header_title = QLabel("DASHBOARD")
        self.header_title.setStyleSheet(f"font-weight: bold; font-size: 15px; color: {MOCHA['mauve']};")
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        
        # User label instead of dropdowns
        theme_label = QLabel("Catppuccin Mocha")
        theme_label.setStyleSheet(f"font-size: 10px; color: {MOCHA['subtext0']}; border: 1px solid {MOCHA['surface1']}; padding: 5px 10px; border-radius: 4px;")
        header_layout.addWidget(theme_label)

        self.content_layout.addWidget(self.header)

        # Main Tool Area
        self.tool_stack = QWidget()
        self.stack_layout = QVBoxLayout(self.tool_stack)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)
        
        # Welcome Widget
        self.welcome = QWidget()
        welcome_layout = QVBoxLayout(self.welcome)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        w_title = QLabel("KEYSTONE")
        w_title.setStyleSheet(f"font-size: 48px; font-weight: bold; color: {MOCHA['surface0']};")
        w_subtitle = QLabel("Select a protocol from the sidebar to begin automation.")
        w_subtitle.setStyleSheet(f"color: {MOCHA['surface1']}; font-size: 12px;")
        welcome_layout.addWidget(w_title, alignment=Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(w_subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.stack_layout.addWidget(self.welcome)
        self.content_layout.addWidget(self.tool_stack)

        self.apply_style()

    def show_tool(self, name):
        self.header_title.setText(name.upper())
        self.welcome.hide()
        for w in self.tool_widgets.values(): w.hide()
        
        if name not in self.tool_widgets:
            self.tool_widgets[name] = GeneratorTab(name, SCRIPTS[name])
            self.stack_layout.addWidget(self.tool_widgets[name])
        
        self.tool_widgets[name].show()

    def apply_style(self):
        c = MOCHA
        accent = c['mauve']
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background: {c['base']}; color: {c['text']}; }}
            #sidebar {{ background: {c['mantle']}; border-right: 1px solid {c['surface0']}; }}
            #header {{ background: {c['base']}; border-bottom: 2px solid {accent}; }}
            
            QPushButton {{ 
                background: {c['surface0']}; 
                border: 1px solid {c['surface1']}; 
                padding: 6px 12px; 
                border-radius: 4px; 
                color: {c['text']};
            }}
            QPushButton:hover {{ border-color: {accent}; background: {c['surface1']}; }}
            
            #tool_btn {{
                background: transparent;
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
                padding-left: 15px;
                border-radius: 0;
            }}
            #tool_btn:hover {{ background: {c['surface0']}; border-left: 3px solid {accent}; }}
            
            QTextEdit {{ background: {c['mantle']}; border: 1px solid {c['surface0']}; border-radius: 4px; }}
            
            QScrollBar:vertical {{ width: 10px; background: transparent; }}
            QScrollBar::handle:vertical {{ background: {c['surface1']}; border-radius: 5px; }}
        """)

if __name__ == "__main__":
    # Suppress Qt icon theme warnings on Linux
    os.environ["QT_LOGGING_RULES"] = "kf.iconthemes.warning=false"
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    w = KeystoneGUI()
    w.show()
    sys.exit(app.exec())
