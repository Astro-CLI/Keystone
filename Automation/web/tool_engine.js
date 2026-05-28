(function () {
  const TOOLS = {
    "vlan-weaver": {
      title: "VLAN Weaver",
      category: "Utilities",
      icon: "═",
      short: "VLAN",
      template: `# VLAN Weaver: Layer 2 Segmentation with IPv6 SVI
- hostname: DSW-1
  vlans:
    - name: Management
      id: 10
      ipv6: "2001:db8:10::1/64"
    - name: Sales
    - name: Guest
`,
      generate: genVlanWeaver
    },
    "ospf-pathmaker": {
      title: "OSPF Pathmaker",
      category: "Routing",
      icon: "○",
      short: "OSPF",
      template: `# OSPF Pathmaker: Dual-Stack Routing
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
`,
      generate: genOspfPathmaker
    },
    "asa-shield": {
      title: "ASA Shield",
      category: "Security",
      icon: "◆",
      short: "ASA",
      template: `# ASA Shield: Next-Gen Firewall
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
  nats:
    - obj_name: INTERNAL_V4
      type: dynamic
      translated_interface: outside
`,
      generate: genAsaShield
    },
    "bgp-conductor": {
      title: "BGP Conductor",
      category: "Routing",
      icon: "○",
      short: "BGP",
      template: `# BGP Conductor: Dual-Stack Peering
- hostname: Edge-R1
  as_number: 65001
  router_id: 1.1.1.1
  neighbors:
    - ip: 10.0.0.2
      remote_as: 65002
    - ip: "2001:db8:0:1::2"
      remote_as: 65002
  networks:
    - network: 192.168.1.0
      mask: 255.255.255.0
    - network: "2001:db8:1::"
      mask: 64
`,
      generate: genBgpConductor
    },
    "dhcp-allocator": {
      title: "DHCP Allocator",
      category: "Services",
      icon: "▣",
      short: "DHCP",
      template: `# DHCP Allocator: IPv4 + DHCPv6 Pools
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
  ipv6_pools:
    - name: DATA_POOL_V6
      prefix: "2001:db8:10::/64"
      dns: "2001:4860:4860::8888"
`,
      generate: genDhcpAllocator
    },
    "eigrp-catalyst": {
      title: "EIGRP Catalyst",
      category: "Routing",
      icon: "○",
      short: "EIGRP",
      template: `# EIGRP Catalyst: Dual-Stack
- hostname: R1
  as_number: 100
  ipv6_as_number: 100
  router_id: 1.1.1.1
  interfaces:
    - name: GigabitEthernet0/0
      ip_address: 192.168.1.1
      subnet_mask: 255.255.255.0
      ipv6_enabled: true
`,
      generate: genEigrpCatalyst
    },
    "hsrp-sentinel": {
      title: "HSRP Sentinel",
      category: "Services",
      icon: "▣",
      short: "HSRP",
      template: `# HSRP Sentinel: High Availability
- hostname: Core-R1
  interfaces:
    - vlan_id: 10
      ip: 192.168.1.2
      mask: 255.255.255.0
      hsrp_ip: 192.168.1.1
      ipv6: "2001:db8:1::2"
      hsrp_ipv6: "2001:db8:1::1"
      priority: 110
`,
      generate: genHsrpSentinel
    },
    "ip-architect": {
      title: "IP Architect",
      category: "Utilities",
      icon: "═",
      short: "IP",
      template: `# IP Architect: Interfaces + Random (IPv4 + IPv6)
- hostname: R1
  interfaces:
    - name: GigabitEthernet0/0
      ip: 192.168.1.1
      mask: 255.255.255.0
    - name: GigabitEthernet0/1
      ip: "fc00::1"
      mask: 64

- random_ips:
    count: 5
    classes: [C, B, A]
    ipv6: false
`,
      generate: genIpArchitect
    },
    "nat-portal": {
      title: "NAT Portal",
      category: "Security",
      icon: "◆",
      short: "NAT",
      template: `# NAT Portal: IPv4/IPv6 Translation
- hostname: Gateway-R1
  inside_interfaces: [GigabitEthernet0/1]
  outside_interfaces: [GigabitEthernet0/0]
  rules:
    - rule_type: static
      local_ip: 192.168.1.50
      global_ip: 203.0.113.10
  ipv6_nats:
    - rule_type: static
      local_ipv6: "2001:db8:1::100"
      global_ipv6: "2001:db8:ffff::100"
`,
      generate: genNatPortal
    },
    "ssh-locksmith": {
      title: "SSH Locksmith",
      category: "Security",
      icon: "◆",
      short: "SSH",
      template: `# SSH Locksmith: Hardening (IPv4 + IPv6)
- hostname: Core-R1
  domain_name: keystone.local
  username: admin
  password: SecretPassword123
  key_size: 2048
  ipv6_vty: true
  vty_acl_ipv6: "2001:db8::/32"
`,
      generate: genSshLocksmith
    },
    "static-anchor": {
      title: "Static Anchor",
      category: "Routing",
      icon: "○",
      short: "STATIC",
      template: `# Static Anchor: Dual-Stack Static Routing
# Logic:
# 1) Same protocol talks to same protocol (IPv4->IPv4, IPv6->IPv6).
# 2) If a router must reach remote IPv6 networks, it needs IPv6 routes too.
# 3) So in dual-stack designs, configure both IPv4 and IPv6 routes on each router.

- hostname: R1
  routes:
    # IPv4 default + specific route
    - network: 0.0.0.0
      mask: 0.0.0.0
      next_hop: 10.0.0.1
    - network: 192.168.2.0
      mask: 255.255.255.0
      next_hop: 10.0.0.5

    # IPv6 default + specific route
    - network: "::/0"
      mask: 0
      next_hop: "2001:db8::1"
    - network: "2001:db8:2::"
      mask: 64
      next_hop: "2001:db8::5"

- hostname: R2
  routes:
    - network: 0.0.0.0
      mask: 0.0.0.0
      next_hop: 10.0.0.2
    - network: "::/0"
      mask: 0
      next_hop: "2001:db8::2"
`,
      generate: genStaticAnchor
    },
    "cidr-architect": {
      title: "CIDR Architect",
      category: "Utilities",
      icon: "═",
      short: "CIDR",
      template: `# CIDR Architect: VLSM
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
    - name: PROD_V6
      size: 2
`,
      generate: genCidrArchitect
    },
    "extract-from-pt": {
      title: "Extract from PT",
      category: "Workflows",
      icon: "\u2190",
      short: "EXT",
      template: `# Extract Topology from Packet Tracer
#
# === INSTRUCTIONS ===
#
# Step 1: Click GENERATE to copy the pt_analyzer.js script
#         (it will be placed in the PT-Builder output tab)
#
# Step 2: In Packet Tracer, paste the script and run it via one of:
#   A) Extensions -> Scripting -> Manage ExApps -> Add -> Paste -> Run
#   B) Extensions -> Scripting -> Edit File Script Module -> Paste -> Run
#      (if Edit File Script Module fails, try Options -> Preferences ->
#       Miscellaneous -> Enable External Network Access from Device Scripts)
#   C) Extensions -> Scripting -> New PT Script Module -> Paste -> Run
#
# Step 3: Copy ALL output from the PT console (Ctrl+A, Ctrl+C)
#
# Step 4: Paste the output here, replacing this template text,
#         then click GENERATE again to parse it into YAML.
#
# --- Paste PT analyzer output below this line ---
`,
      generate: genExtractFromPt
    },
    "full-topology": {
      title: "Full Topology",
      category: "Utilities",
      icon: "⊞",
      short: "NET",
      template: `# Full Topology: Multi-Tier Enterprise Network
# Paste your entire network topology here. Generates CLI config for every
# device plus a PT-Builder JS script (addDevice, addLink, configureIosDevice).
#
# Per device: hostname, model, interfaces, vlans, ospf, eigrp, bgp, routes,
#   dhcp (pools + ipv6_pools), nat, ssh, domain_name
# Per interface: name, ip, mask, ipv6, description, mode, access_vlan,
#   trunk_allowed, nameif, security_level, hsrp (group, ip, priority, preempt), dhcp
# Links array defines physical connections for PT-Builder output.
# This example showcases core / distribution / access layers with BGP, OSPF,
# EIGRP, HSRP, static routes, VLANs, SVIs, DHCP, NAT, SSH, and end devices.

name: "Multi-Tier Enterprise Network"

devices:
  # ── Core Layer ──────────────────────────────────────────────
  - hostname: Core-R1
    model: 2911
    domain_name: enterprise.local
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.0.1
        mask: 255.255.255.252
        ipv6: "2001:db8:ff:1::1/64"
        description: "P2P to Core-R2"
      - name: GigabitEthernet0/1
        ip: 10.0.1.1
        mask: 255.255.255.252
        ipv6: "2001:db8:ff:2::1/64"
        description: "P2P to ASA-FW-01 inside"
      - name: GigabitEthernet0/2
        ip: 172.16.0.1
        mask: 255.255.255.255
        description: "Loopback0"
      - name: GigabitEthernet1/0
        ip: 192.168.10.1
        mask: 255.255.255.0
        ipv6: "2001:db8:10::1/64"
        description: "Management VLAN"
      - name: GigabitEthernet2/0
        ip: 203.0.113.1
        mask: 255.255.255.252
        description: "WAN to ISP"
    ospf:
      process_id: 1
      router_id: 1.1.1.1
      area: 0
    bgp:
      as: 65001
      router_id: 1.1.1.1
      networks:
        - network: 192.168.0.0
          mask: 255.255.0.0
        - network: 172.16.0.0
          mask: 255.255.255.0
      neighbors:
        - ip: 10.0.0.2
          remote_as: 65001
          update_source: GigabitEthernet0/0
          next_hop_self: true
        - ip: 203.0.113.2
          remote_as: 64515
          ebgp_multihop: 2
    routes:
      - network: 0.0.0.0
        mask: 0.0.0.0
        next_hop: 203.0.113.2
      - network: "::/0"
        mask: 0
        next_hop: "2001:db8:ff:f::1"
    ssh:
      username: netadmin
      password: s3cur3P@ss!
      key_size: 2048
      ipv6_vty: true
      vty_acl_ipv6: "2001:db8:10::/32"

  - hostname: Core-R2
    model: 2911
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.0.2
        mask: 255.255.255.252
        ipv6: "2001:db8:ff:1::2/64"
        description: "P2P to Core-R1"
        hsrp:
          group: 1
          ip: 10.0.0.3
          priority: 90
      - name: GigabitEthernet0/1
        ip: 10.0.2.1
        mask: 255.255.255.252
        ipv6: "2001:db8:ff:3::1/64"
        description: "P2P to ASA-FW-01 dmz"
      - name: GigabitEthernet0/2
        ip: 172.16.0.2
        mask: 255.255.255.255
        description: "Loopback0"
      - name: GigabitEthernet1/0
        ip: 192.168.10.2
        mask: 255.255.255.0
        ipv6: "2001:db8:10::2/64"
        description: "Management VLAN"
        hsrp:
          group: 10
          ip: 192.168.10.254
          priority: 100
          preempt: true
    ospf:
      process_id: 1
      router_id: 2.2.2.2
      area: 0
    bgp:
      as: 65001
      router_id: 2.2.2.2
      neighbors:
        - ip: 10.0.0.1
          remote_as: 65001
          update_source: GigabitEthernet0/0
    routes:
      - network: 0.0.0.0
        mask: 0.0.0.0
        next_hop: 10.0.0.1

  # ── Distribution Layer ──────────────────────────────────────
  - hostname: DSW-1
    model: 2960-24TT
    vlans:
      - id: 10
        name: Management
        ip: 192.168.10.253
        mask: 255.255.255.0
        ipv6: "2001:db8:10::253/64"
      - id: 20
        name: Servers
        ip: 192.168.20.1
        mask: 255.255.255.0
        ipv6: "2001:db8:20::1/64"
      - id: 30
        name: Data
        ip: 192.168.30.1
        mask: 255.255.255.0
        ipv6: "2001:db8:30::1/64"
      - id: 40
        name: Voice
        ip: 192.168.40.1
        mask: 255.255.255.0
      - id: 50
        name: Guest
        ip: 192.168.50.1
        mask: 255.255.255.0
    interfaces:
      - name: GigabitEthernet0/1
        ip: 192.168.10.252
        mask: 255.255.255.0
        description: "Uplink to Core (SVI transit)"
      - name: GigabitEthernet0/2
        mode: trunk
        trunk_allowed: "10,20,30,40,50"
        description: "Trunk to ASW-1"
    ospf:
      process_id: 1
      router_id: 3.3.3.3
      area: 0
    eigrp:
      as: 100
    dhcp:
      pools:
        - name: DATA_POOL
          network: 192.168.30.0
          mask: 255.255.255.0
          gateway: 192.168.30.1
          dns: 192.168.20.10
        - name: VOICE_POOL
          network: 192.168.40.0
          mask: 255.255.255.0
          gateway: 192.168.40.1
        - name: GUEST_POOL
          network: 192.168.50.0
          mask: 255.255.255.0
          gateway: 192.168.50.1
      ipv6_pools:
        - name: DATA_POOL_V6
          prefix: "2001:db8:30::/64"
          dns: "2001:db8:20::a"
        - name: GUEST_POOL_V6
          prefix: "2001:db8:50::/64"

  - hostname: DSW-2
    model: 2960-24TT
    vlans:
      - id: 10
        name: Management
        ip: 192.168.10.254
        mask: 255.255.255.0
        ipv6: "2001:db8:10::254/64"
      - id: 20
        name: Servers
        ip: 192.168.20.2
        mask: 255.255.255.0
        ipv6: "2001:db8:20::2/64"
      - id: 30
        name: Data
        ip: 192.168.30.2
        mask: 255.255.255.0
        ipv6: "2001:db8:30::2/64"
      - id: 40
        name: Voice
        ip: 192.168.40.2
        mask: 255.255.255.0
      - id: 50
        name: Guest
        ip: 192.168.50.2
        mask: 255.255.255.0
    interfaces:
      - name: GigabitEthernet0/1
        ip: 192.168.10.251
        mask: 255.255.255.0
        description: "Uplink to Core (SVI transit)"
      - name: GigabitEthernet0/2
        mode: trunk
        trunk_allowed: "10,20,30,40,50"
        description: "Trunk to ASW-2"
    ospf:
      process_id: 1
      router_id: 4.4.4.4
      area: 0
    eigrp:
      as: 100
    dhcp:
      pools:
        - name: DATA_POOL_2
          network: 192.168.31.0
          mask: 255.255.255.0
          gateway: 192.168.31.1
          dns: 192.168.20.10

  # ── Access Layer ────────────────────────────────────────────
  - hostname: ASW-1
    model: 2960-24TT
    vlans:
      - id: 10
        name: Management
      - id: 30
        name: Data
      - id: 40
        name: Voice
      - id: 50
        name: Guest
    interfaces:
      - name: GigabitEthernet0/1
        mode: trunk
        trunk_allowed: "10,30,40,50"
        description: "Uplink to DSW-1"
      - name: FastEthernet0/1
        mode: access
        access_vlan: 30
        description: "PC1"
      - name: FastEthernet0/2
        mode: access
        access_vlan: 30
        description: "PC2"
      - name: FastEthernet0/3
        mode: access
        access_vlan: 50
        description: "Laptop-1 (Guest)"

  - hostname: ASW-2
    model: 2960-24TT
    vlans:
      - id: 10
        name: Management
      - id: 20
        name: Servers
    interfaces:
      - name: GigabitEthernet0/1
        mode: trunk
        trunk_allowed: "10,20"
        description: "Uplink to DSW-2"
      - name: FastEthernet0/1
        mode: access
        access_vlan: 20
        description: "Server-1"
      - name: FastEthernet0/2
        mode: access
        access_vlan: 20
        description: "Server-2"

  # ── Firewall ────────────────────────────────────────────────
  - hostname: ASA-FW-01
    model: 5506-X
    interfaces:
      - name: GigabitEthernet0/0
        nameif: inside
        security_level: 100
        ip: 10.0.1.2
        mask: 255.255.255.252
        ipv6: "2001:db8:ff:2::2/64"
        description: "Inside to Core-R1"
      - name: GigabitEthernet0/1
        nameif: dmz
        security_level: 50
        ip: 10.0.2.2
        mask: 255.255.255.252
        ipv6: "2001:db8:ff:3::2/64"
        description: "DMZ to Core-R2"
      - name: GigabitEthernet0/2
        nameif: outside
        security_level: 0
        ip: 198.51.100.1
        mask: 255.255.255.248
        description: "Outside to Internet"
    nat:
      - type: dynamic
        outside_interface: outside
    routes:
      - network: 192.168.0.0
        mask: 255.255.0.0
        next_hop: 10.0.1.1
      - network: "2001:db8::/32"
        mask: 0
        next_hop: "2001:db8:ff:2::1"
    ssh:
      username: admin
      password: Pa$$w0rd!
      key_size: 2048

  # ── End Devices ─────────────────────────────────────────────
  - hostname: PC1
    model: PC-PT
    interfaces:
      - name: FastEthernet0
        dhcp: true

  - hostname: PC2
    model: PC-PT
    interfaces:
      - name: FastEthernet0
        dhcp: true

  - hostname: Laptop-1
    model: Laptop-PT
    interfaces:
      - name: FastEthernet0
        dhcp: true

  - hostname: Server-1
    model: Server-PT
    interfaces:
      - name: FastEthernet0
        ip: 192.168.20.10
        mask: 255.255.255.0
        gateway: 192.168.20.1

  - hostname: Server-2
    model: Server-PT
    interfaces:
      - name: FastEthernet0
        ip: 192.168.20.11
        mask: 255.255.255.0
        gateway: 192.168.20.1

links:
  - source: Core-R1:GigabitEthernet0/0
    target: Core-R2:GigabitEthernet0/0
    type: straight
  - source: Core-R1:GigabitEthernet0/1
    target: ASA-FW-01:GigabitEthernet0/0
    type: straight
  - source: Core-R1:GigabitEthernet1/0
    target: DSW-1:GigabitEthernet0/1
    type: straight
  - source: Core-R2:GigabitEthernet0/1
    target: ASA-FW-01:GigabitEthernet0/1
    type: straight
  - source: Core-R2:GigabitEthernet1/0
    target: DSW-2:GigabitEthernet0/1
    type: straight
  - source: DSW-1:GigabitEthernet0/2
    target: ASW-1:GigabitEthernet0/1
    type: straight
  - source: DSW-2:GigabitEthernet0/2
    target: ASW-2:GigabitEthernet0/1
    type: straight
  - source: ASW-1:FastEthernet0/1
    target: PC1:FastEthernet0
    type: straight
  - source: ASW-1:FastEthernet0/2
    target: PC2:FastEthernet0
    type: straight
  - source: ASW-1:FastEthernet0/3
    target: Laptop-1:FastEthernet0
    type: straight
  - source: ASW-2:FastEthernet0/1
    target: Server-1:FastEthernet0
    type: straight
  - source: ASW-2:FastEthernet0/2
    target: Server-2:FastEthernet0
    type: straight
`,
      generate: genFullTopology
    }
  };

  var CAT_ORDER = ["Workflows", "Routing", "Security", "Services", "Utilities"];
  var activeSlug = null;

  function showToast(msg, type) {
    var c = document.getElementById("toast-container");
    if (!c) return;
    var el = document.createElement("div");
    el.className = "toast" + (type ? " " + type : "");
    el.innerHTML = '<span class="toast-icon">' + (type === "success" ? "✓" : type === "error" ? "✗" : "ℹ") + '</span>' + msg + '<span class="toast-progress"></span>';
    c.appendChild(el);
    setTimeout(function () {
      el.classList.add("toast-out");
      setTimeout(function () { el.remove(); }, 250);
    }, 2800);
  }

  var lineTimer = null;
  function scheduleLineCount() {
    if (lineTimer) clearTimeout(lineTimer);
    lineTimer = setTimeout(updateLineCount, 50);
  }

  function updateLineCount() {
    var input = document.getElementById("input");
    var badge = document.getElementById("line-count");
    if (!input || !badge) return;
    var n = input.value.split("\n").length;
    badge.textContent = n + " line" + (n !== 1 ? "s" : "");
    scheduleSave();
  }

  var saveTimer = null;
  function scheduleSave() {
    if (saveTimer) clearTimeout(saveTimer);
    saveTimer = setTimeout(doSaveState, 300);
  }

  function storageKey(slug, kind) {
    return "keystone_" + slug + "_" + kind;
  }

  function readSaved(slug, kind) {
    try {
      return localStorage.getItem(storageKey(slug, kind));
    } catch (e) { return null; }
  }

  function doSaveState() {
    if (!activeSlug) return;
    var input = document.getElementById("input");
    var output = document.getElementById("output");
    var outputPt = document.getElementById("output-ptbuilder");
    if (!input || !output) return;
    try {
      localStorage.setItem(storageKey(activeSlug, "input"), input.value);
      localStorage.setItem(storageKey(activeSlug, "output"), output.value);
      if (outputPt) {
        localStorage.setItem(storageKey(activeSlug, "output_ptbuilder"), outputPt.value);
      }
      localStorage.setItem("keystone_active_slug", activeSlug);
      var savedEl = document.getElementById("status-saved");
      if (savedEl) savedEl.textContent = "Saved";
    } catch (e) { /* Storage full — silently ignore */ }
  }

  function renderSidebar(active) {
    var list = document.getElementById("tool-list");
    if (!list) return;
    list.innerHTML = "";
    var grouped = {};
    for (var slug in TOOLS) {
      if (!TOOLS.hasOwnProperty(slug)) continue;
      var t = TOOLS[slug];
      if (!grouped[t.category]) grouped[t.category] = [];
      grouped[t.category].push({ slug: slug, tool: t });
    }
    for (var ci = 0; ci < CAT_ORDER.length; ci++) {
      var cat = CAT_ORDER[ci];
      var items = grouped[cat];
      if (!items || !items.length) continue;
      
      var grp = document.createElement("div");
      grp.className = "sidebar-group cat-" + cat.toLowerCase();
      
      var hdr = document.createElement("div");
      hdr.className = "sidebar-group-header cat-" + cat.toLowerCase();
      hdr.innerHTML = '<span class="collapse-arrow">&#x25BC;</span> ' + cat;
      hdr.addEventListener("click", function (e) {
        var arrow = this.querySelector(".collapse-arrow");
        var body = this.nextElementSibling;
        if (body) {
          body.style.display = body.style.display === "none" ? "" : "none";
          arrow.classList.toggle("collapsed");
        }
      });
      grp.appendChild(hdr);
      
      var grpBody = document.createElement("div");
      grpBody.className = "sidebar-group-body";
      
      for (var si = 0; si < items.length; si++) {
        var it = items[si];
        var el = document.createElement("div");
        el.className = "sidebar-item cat-" + cat.toLowerCase() + (it.slug === active ? " active" : "");
        el.setAttribute("data-slug", it.slug);
        el.innerHTML = '<span class="tool-icon">' + (it.tool.icon || "■") + '</span>' +
          it.tool.title +
          '<span class="tool-short">' + it.tool.short + "</span>";
        el.addEventListener("click", (function (s) {
          return function () { selectTool(s); };
        })(it.slug));
        grpBody.appendChild(el);
      }
      grp.appendChild(grpBody);
      list.appendChild(grp);
    }
  }

  function selectTool(slug) {
    var tool = TOOLS[slug];
    if (!tool) {
      showDashboard();
      return;
    }
    if (slug === activeSlug) return;
    if (activeSlug) doSaveState();
    activeSlug = slug;
    if (window.location.hash !== "#" + slug) {
      window.location.hash = slug;
    }
    
    // Toggle editor displays
    var dbView = document.getElementById("dashboard-view");
    var edPane = document.getElementById("editor-pane");
    var div = document.getElementById("divider");
    var outPane = document.getElementById("output-pane");
    var topbarActions = document.getElementById("topbar-actions");
    
    if (dbView) dbView.style.display = "none";
    if (edPane) edPane.style.display = "flex";
    if (div) div.style.display = "flex";
    if (outPane) outPane.style.display = "flex";
    
    if (topbarActions) {
      var buttons = topbarActions.querySelectorAll("button:not(#theme-toggle)");
      buttons.forEach(function (btn) { btn.style.display = ""; });
    }

    var items = document.querySelectorAll(".sidebar-item");
    for (var i = 0; i < items.length; i++) {
      items[i].classList.toggle("active", items[i].getAttribute("data-slug") === slug);
    }
    document.title = tool.title + " \u2014 Keystone";
    var tn = document.getElementById("topbar-toolname");
    if (tn) tn.textContent = "\u2014 " + tool.title;
    var st = document.getElementById("status-tool");
    if (st) st.textContent = tool.title;
    var sc = document.getElementById("status-category");
    if (sc) sc.textContent = tool.category;
    
    var input = document.getElementById("input");
    var output = document.getElementById("output");
    var outputPt = document.getElementById("output-ptbuilder");
    if (!input || !output) return;
    var savedInput = readSaved(slug, "input");
    var savedOutput = readSaved(slug, "output");
    var savedOutputPt = readSaved(slug, "output_ptbuilder");
    input.value = savedInput != null ? savedInput : tool.template;
    output.value = savedOutput != null ? savedOutput : "";
    if (outputPt) {
      outputPt.value = savedOutputPt != null ? savedOutputPt : "";
    }
    
    updateLineCount();
    validateInput();
    scheduleSave();
  }

  function showDashboard() {
    activeSlug = null;
    try {
      if (window.location.hash !== "#dashboard" && window.location.hash !== "") {
        window.location.hash = "dashboard";
      }
    } catch (e) {}

    var items = document.querySelectorAll(".sidebar-item");
    for (var i = 0; i < items.length; i++) {
      items[i].classList.remove("active");
    }
    
    document.title = "Keystone \u2014 Network Automation Dashboard";
    var tn = document.getElementById("topbar-toolname");
    if (tn) tn.textContent = "\u2014 Dashboard";
    var st = document.getElementById("status-tool");
    if (st) st.textContent = "Dashboard";
    var sc = document.getElementById("status-category");
    if (sc) sc.textContent = "Overview";
    
    var dbView = document.getElementById("dashboard-view");
    var edPane = document.getElementById("editor-pane");
    var div = document.getElementById("divider");
    var outPane = document.getElementById("output-pane");
    var topbarActions = document.getElementById("topbar-actions");
    
    if (dbView) dbView.style.display = "block";
    if (edPane) edPane.style.display = "none";
    if (div) div.style.display = "none";
    if (outPane) outPane.style.display = "none";
    
    if (topbarActions) {
      var buttons = topbarActions.querySelectorAll("button:not(#theme-toggle)");
      buttons.forEach(function (btn) { btn.style.display = "none"; });
    }
    
    renderDashboardCards();
  }

  function getShortDesc(slug) {
    const descs = {
      "vlan-weaver": "Generate VLAN database allocations and SVI name configurations for Layer 2 segmentation.",
      "ospf-pathmaker": "Configure OSPFv2/OSPFv3 multi-area routing with automated network/wildcard commands.",
      "asa-shield": "Build Cisco ASA firewall configurations including security levels, object groups, static/dynamic NAT, and access lists.",
      "bgp-conductor": "Generate border gateway protocol configurations for external peering, neighbor groups, and network statements.",
      "dhcp-allocator": "Define DHCP pools, exclude gateway ranges, and customize DNS servers for automated client addressing.",
      "eigrp-catalyst": "Configure EIGRP dual-stack routing processes, router IDs, stub settings, and passive interfaces.",
      "hsrp-sentinel": "Create high-availability hot standby router protocol interfaces with virtual IP failover priorities.",
      "ip-architect": "Generate static IP addressing schemes or random batches of private (RFC 1918) and public IPv4/IPv6 nodes.",
      "nat-portal": "Deploy static port forwarding, dynamic pool maps, or PAT overload rules across internal/external interfaces.",
      "ssh-locksmith": "Harden Cisco switches and routers using RSA crypto-key pairs, VTY lockouts, and domain configurations.",
      "static-anchor": "Generate static destination routes and backup floating static paths for complex dual-stack setups.",
      "cidr-architect": "Compute VLSM allocations or subnet breakdowns with broadcast addresses, gateways, and utilization summaries.",
      "full-topology": "Define an entire network in one YAML — devices, VLANs, interfaces, routing protocols, DHCP, NAT, SSH, and physical links. Generates unified CLI + PT-Builder script.",
      "extract-from-pt": "Import running configs from an existing Packet Tracer topology. Run the analyzer JS in PT, paste the output, and get structured YAML."
    };
    return descs[slug] || "Generate standard Cisco IOS configurations instantly.";
  }

  function renderDashboardCards() {
    var container = document.getElementById("dashboard-cards-container");
    if (!container) return;
    container.innerHTML = "";
    
    var grouped = {};
    for (var slug in TOOLS) {
      if (!TOOLS.hasOwnProperty(slug)) continue;
      var t = TOOLS[slug];
      if (!grouped[t.category]) grouped[t.category] = [];
      grouped[t.category].push({ slug: slug, tool: t });
    }
    
    for (var ci = 0; ci < CAT_ORDER.length; ci++) {
      var cat = CAT_ORDER[ci];
      var items = grouped[cat];
      if (!items || !items.length) continue;
      
      var catSection = document.createElement("div");
      catSection.className = "dashboard-category-section";
      
      var catTitle = document.createElement("h2");
      catTitle.className = "dashboard-category-title cat-" + cat.toLowerCase();
      catTitle.textContent = cat;
      catSection.appendChild(catTitle);
      
      var cardsGrid = document.createElement("div");
      cardsGrid.className = "dashboard-cards-grid";
      
      for (var si = 0; si < items.length; si++) {
        var it = items[si];
        var card = document.createElement("div");
        card.className = "tool-card cat-" + cat.toLowerCase();
        
        var desc = getShortDesc(it.slug);
        
        card.innerHTML = `
          <div class="tool-card-icon">${it.tool.icon || '⚙'}</div>
          <div class="tool-card-header">
            <h3>${it.tool.title}</h3>
            <span class="tool-card-badge">${it.tool.short}</span>
          </div>
          <p class="tool-card-desc">${desc}</p>
          <button class="tool-card-btn">Launch Generator &rarr;</button>
        `;
        
        card.addEventListener("click", (function (s) {
          return function () { selectTool(s); };
        })(it.slug));
        
        cardsGrid.appendChild(card);
      }
      
      catSection.appendChild(cardsGrid);
      container.appendChild(catSection);
    }
  }

  function initDivider() {
    var div = document.getElementById("divider");
    if (!div) return;
    var dividerDragging = false;
    div.addEventListener("mousedown", function (e) {
      e.preventDefault();
      dividerDragging = true;
      div.classList.add("dragging");
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    });
    document.addEventListener("mousemove", function (e) {
      if (!dividerDragging) return;
      var isMobile = window.innerWidth <= 800;
      var main = document.getElementById("main");
      if (!main) return;
      var rect = main.getBoundingClientRect();
      if (isMobile) {
        var pct = ((e.clientY - rect.top) / rect.height) * 100;
        pct = Math.max(20, Math.min(80, pct));
        var editorPane = document.getElementById("editor-pane");
        var outputPane = document.getElementById("output-pane");
        if (editorPane) editorPane.style.flex = "0 0 calc(" + pct + "% - 2px)";
        if (outputPane) outputPane.style.flex = "1 1 auto";
      } else {
        var pct = ((e.clientX - rect.left) / rect.width) * 100;
        pct = Math.max(25, Math.min(75, pct));
        var editorPane = document.getElementById("editor-pane");
        var outputPane = document.getElementById("output-pane");
        if (editorPane) editorPane.style.flex = "0 0 calc(" + pct + "% - 2px)";
        if (outputPane) outputPane.style.flex = "1 1 auto";
      }
    });
    document.addEventListener("mouseup", function () {
      if (dividerDragging) {
        dividerDragging = false;
        var div = document.getElementById("divider");
        if (div) div.classList.remove("dragging");
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      }
    });
  }

  function extractDeviceConfigs(cliConfigText) {
    var configs = {};
    if (!cliConfigText) return configs;
    var currentDevice = null;
    var currentLines = [];
    
    var lines = cliConfigText.split("\n");
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var match = line.match(/^!\s*---\s*([a-zA-Z0-9_\-]+)\s*---/);
      if (match) {
        if (currentDevice && currentLines.length > 0) {
          configs[currentDevice] = currentLines.join("\n").trim();
        }
        currentDevice = match[1];
        currentLines = [];
      } else {
        currentLines.push(line);
      }
    }
    if (currentDevice && currentLines.length > 0) {
      configs[currentDevice] = currentLines.join("\n").trim();
    }
    return configs;
  }

  function generatePTBuilderScript(data, cliConfigText) {
    if (!data) return "";
    
    var lines = [
      "// PTBuilder Script - Generated by Keystone Automation",
      "// Paste this into Packet Tracer: Extensions > Builder Code Editor\n",
      'function configureIosDevice(name, cmds) {',
      "    try {",
      "        var d;",
      "        try { d = ipc.network().getDevice(name); } catch(e) {}",
      "        if (!d) try { d = network.getDevice(name); } catch(e) {}",
      "        if (!d) try { var n = ipc.appWindow().getActiveFile().getMainNetwork(); d = n.getDevice(name); } catch(e) {}",
      '        if (!d) return;',
      "        try { d.setPower(true); } catch(e) {}",
      "        var cl = d.getCommandLine();",
      "        if (!cl) return;",
      "        var fn = null;",
      '        if (typeof cl.enterCommand === "function") fn = function(c){cl.enterCommand(c);};',
      '        else if (typeof cl.sendCommand === "function") fn = function(c){cl.sendCommand(c);};',
      '        else if (typeof cl.execute === "function") fn = function(c){cl.execute(c);};',
      "        if (!fn) return;",
      "        for (var i = 0; i < cmds.length; i++) {",
      "            fn(cmds[i]);",
      "        }",
      "    } catch(e) {}",
      "}\n",
    ];
    
    var devices = [];
    var links = [];
    
    if (data && typeof data === "object" && !Array.isArray(data) && Array.isArray(data.devices)) {
      devices = data.devices;
      if (Array.isArray(data.links)) {
        links = data.links;
      } else if (Array.isArray(data.connections)) {
        links = data.connections;
      }
    } else {
      devices = asList(data);
    }
    
    var step = 0;
    
    step++;
    lines.push("// ===== " + step + ". Spawning Devices =====");
    var x = 100, y = 100;
    var devicePositions = {};
    
    var modelMap = {
      'router': '2911',
      'switch': '2960-24TT',
      'firewall': '5506-X',
      'asa': '5506-X',
      'pc': 'PC-PT',
      'server': 'Server-PT',
      'hub': 'Hub-PT',
      'cloud': 'Cloud-PT'
    };
    
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i];
      if (!d) continue;
      
      var name = d.hostname || d.name || ("Device" + (i + 1));
      var slugHint = (activeSlug === "vlan-weaver" || activeSlug === "dhcp-allocator") ? "switch" : (activeSlug === "asa-shield" || activeSlug === "nat-portal") ? "firewall" : "router";
      var type = (d.type || slugHint).toLowerCase();
      var model = d.model || modelMap[type] || "2911";
      
      var devX = x, devY = y;
      if (d.position && typeof d.position === "object") {
        if (d.position.x != null) devX = Number(d.position.x);
        if (d.position.y != null) devY = Number(d.position.y);
      } else if (d.x != null && d.y != null) {
        devX = Number(d.x);
        devY = Number(d.y);
      } else {
        devX = x;
        devY = y;
        x += 250;
        if (x > 1500) {
          x = 100;
          y += 300;
        }
      }
      
      devicePositions[name] = { x: devX, y: devY, type: type };
      lines.push(`addDevice("${name}", "${model}", ${devX}, ${devY});`);
    }
    
    // Check if modules exist
    var hasModules = false;
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i];
      if (d && Array.isArray(d.modules)) {
        if (!hasModules) {
          step++;
          lines.push("\n// ===== " + step + ". Adding Hardware Modules =====");
          hasModules = true;
        }
        var name = d.hostname || d.name || ("Device" + (i + 1));
        for (var m = 0; m < d.modules.length; m++) {
          var mod = d.modules[m];
          if (mod && mod.slot && mod.model) {
            lines.push(`addModule("${name}", "${mod.slot}", "${mod.model}");`);
          }
        }
      }
    }
    
    // Add links
    if (links.length > 0) {
      step++;
      lines.push("\n// ===== " + step + ". Linking Interfaces =====");
      for (var j = 0; j < links.length; j++) {
        var link = links[j];
        if (!link) continue;
        
        var source = link.source || "";
        var target = link.target || "";
        var linkType = link.link_type || link.type || "straight";
        
        if (source && target && source.includes(":") && target.includes(":")) {
          var srcParts = source.split(":");
          var tgtParts = target.split(":");
          var srcDevice = srcParts[0];
          var srcPort = _normalizePortHelper(srcParts[1]);
          var tgtDevice = tgtParts[0];
          var tgtPort = _normalizePortHelper(tgtParts[1]);
          
          lines.push(`addLink("${srcDevice}", "${srcPort}", "${tgtDevice}", "${tgtPort}", "${linkType}");`);
        }
      }
    }
    
    // Configure IOS devices
    if (cliConfigText) {
      var deviceConfigs = extractDeviceConfigs(cliConfigText);
      var configLines = [];
      for (var name in deviceConfigs) {
        if (deviceConfigs.hasOwnProperty(name)) {
          var commands = deviceConfigs[name];
          var raw = commands
            .replace(/\\/g, '\\\\')
            .replace(/"/g, '\\"');
          var cmdList = raw.split('\n');
          var all = ['no', ' ', 'enable', 'configure terminal'];
          for (var ci = 0; ci < cmdList.length; ci++) {
            var c = cmdList[ci].trim();
            if (c && c.indexOf('!') !== 0) {
              all.push(c);
            }
          }
          all.push('end', 'write memory');
          configLines.push('configureIosDevice("' + name + '", ["' + all.join('", "') + '"]);');
        }
      }
      if (configLines.length > 0) {
        step++;
        lines.push("\n// ===== " + step + ". Configuring Cisco IOS Devices =====");
        lines.push(...configLines);
      }
    }
    
    // Configure PC IP configurations
    var pcConfigLines = [];
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i];
      if (!d) continue;
      var name = d.hostname || d.name || ("Device" + (i + 1));
      var type = (d.type || "").toLowerCase();
      var nameLc = name.toLowerCase();
      if (type === "pc" || type === "server" || nameLc.indexOf("pc") === 0 || nameLc.indexOf("host") === 0 || nameLc.indexOf("srv") === 0) {
        var dhcp = d.dhcp === true;
        var ip = d.ip || d.ip_address || "";
        var mask = d.mask || d.subnet_mask || "";
        var gw = d.gateway || d.default_gateway || "";
        var dns = d.dns || d.dns_server || "";
        
        if (dhcp || ip) {
          pcConfigLines.push(`configurePcIp("${name}", ${dhcp}, "${ip}", "${mask}", "${gw}", "${dns}");`);
        }
      }
    }
    if (pcConfigLines.length > 0) {
      step++;
      lines.push("\n// ===== " + step + ". Configuring PC IP Settings =====");
      lines.push(...pcConfigLines);
    }
    
    return lines.join("\n");
  }
  
  function _normalizePortHelper(port) {
    var p = String(port).trim();
    if (/^(GigabitEthernet|FastEthernet|Serial|Ethernet|Loopback|Vlan|Port-channel|Tunnel|TenGigabit)/i.test(p)) return p;
    var portMap = {
      '0/0': 'GigabitEthernet0/0',
      '0/1': 'GigabitEthernet0/1',
      '0/2': 'GigabitEthernet0/2',
      '0/3': 'GigabitEthernet0/3',
      '1/0': 'GigabitEthernet1/0',
      '1/1': 'GigabitEthernet1/1',
      'g0/0': 'GigabitEthernet0/0',
      'g0/1': 'GigabitEthernet0/1',
      'f0/0': 'FastEthernet0/0',
      'f0/1': 'FastEthernet0/1',
      'inside': 'GigabitEthernet0/0',
      'outside': 'GigabitEthernet0/1',
      'dmz': 'GigabitEthernet0/2'
    };
    var normalized = p.toLowerCase();
    return portMap[normalized] || ("GigabitEthernet" + p);
  }

  function doGenerate() {
    var tool = TOOLS[activeSlug];
    if (!tool) { showToast("No tool selected", "error"); return; }
    var input = document.getElementById("input");
    var output = document.getElementById("output");
    var outputPt = document.getElementById("output-ptbuilder");
    if (!input || !output) return;

    // Special case: Extract from PT reads raw analyzer text, not YAML
    if (activeSlug === "extract-from-pt") {
      genExtractFromPt(input, output, outputPt);
      return;
    }

    try {
      var data = parseInput(input.value);
      var cliOutput = tool.generate(data);
      output.value = cliOutput;
      if (outputPt) {
        outputPt.value = generatePTBuilderScript(data, cliOutput);
      }
      scheduleSave();
    } catch (e) {
      output.value = "! Error: " + e.message;
      if (outputPt) {
        outputPt.value = "// Error: " + e.message;
      }
      showToast(e.message, "error");
    }
  }

  function doReset() {
    var tool = TOOLS[activeSlug];
    if (!tool) return;
    var input = document.getElementById("input");
    var output = document.getElementById("output");
    var outputPt = document.getElementById("output-ptbuilder");
    if (input) input.value = tool.template;
    if (output) output.value = "";
    if (outputPt) outputPt.value = "";
    updateLineCount();
    validateInput();
    scheduleSave();
  }

  async function doCopy() {
    var activeTab = "cli";
    var cliTab = document.querySelector(".pane-tab-btn[data-tab='cli']");
    if (cliTab && !cliTab.classList.contains("active")) {
      activeTab = "ptbuilder";
    }
    
    var outputEl = activeTab === "cli" 
      ? document.getElementById("output") 
      : document.getElementById("output-ptbuilder");
      
    if (!outputEl) return;
    var text = outputEl.value || "";
    if (!text) { showToast("Nothing to copy", "error"); return; }
    try {
      await navigator.clipboard.writeText(text);
      showToast("Copied to clipboard", "success");
      
      var copyBtn = document.getElementById("action-copy") || document.getElementById("copy");
      if (copyBtn) {
        copyBtn.classList.add("copy-flash");
        setTimeout(function() { copyBtn.classList.remove("copy-flash"); }, 1000);
      }
    } catch (e) {
      showToast("Copy failed", "error");
    }
  }

  function validateInput() {
    var input = document.getElementById("input");
    var badge = document.getElementById("input-status-badge");
    var pane = document.getElementById("editor-pane");
    if (!input) return;
    
    var text = input.value.trim();
    if (!text) {
      if (badge) {
        badge.textContent = "Empty";
        badge.className = "pane-badge status-empty";
        badge.title = "No configuration input provided.";
      }
      if (pane) pane.classList.remove("has-error");
      return;
    }

    // Extract from PT uses raw analyzer text, not YAML
    if (activeSlug === "extract-from-pt") {
      if (badge) {
        var hasDevices = text.indexOf("DEVICE:") >= 0;
        badge.textContent = hasDevices ? "Ready" : "Instructions";
        badge.className = hasDevices ? "pane-badge status-valid" : "pane-badge status-empty";
        badge.title = hasDevices ? "Analyzer output detected. Click Generate to parse." : "Paste analyzer output and click Generate.";
      }
      if (pane) pane.classList.remove("has-error");
      return;
    }
    
    try {
      var data = parseInput(text);
      if (badge) {
        var isJson = text.startsWith("{") || text.startsWith("[");
        badge.textContent = isJson ? "✓ Valid JSON" : "✓ Valid YAML";
        badge.className = "pane-badge status-valid";
        badge.title = "Syntax is fully correct and ready to generate.";
      }
      if (pane) pane.classList.remove("has-error");
    } catch (e) {
      if (badge) {
        badge.textContent = "✗ Syntax Error";
        badge.className = "pane-badge status-invalid";
        badge.title = e.message;
      }
      if (pane) pane.classList.add("has-error");
    }
  }

  function initTheme() {
    var toggleBtn = document.getElementById("theme-toggle");
    if (!toggleBtn) return;
    
    var currentTheme = localStorage.getItem("keystone_theme") || "dark";
    document.documentElement.setAttribute("data-theme", currentTheme);
    updateThemeUI(currentTheme);
    
    toggleBtn.addEventListener("click", function () {
      var theme = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", theme);
      localStorage.setItem("keystone_theme", theme);
      updateThemeUI(theme);
      showToast("Switched to " + theme + " theme", "info");
    });
  }
  
  function updateThemeUI(theme) {
    var toggleBtn = document.getElementById("theme-toggle");
    if (!toggleBtn) return;
    var iconSpan = toggleBtn.querySelector(".theme-icon");
    if (iconSpan) {
      iconSpan.textContent = theme === "dark" ? "🌙" : "☀️";
    }
  }

  function initSearch() {
    var searchInput = document.getElementById("search-input");
    var searchClear = document.getElementById("search-clear");
    if (!searchInput) return;
    
    searchInput.addEventListener("input", function () {
      var query = searchInput.value.toLowerCase().trim();
      if (searchClear) searchClear.style.display = query ? "block" : "none";
      
      var groups = document.querySelectorAll(".sidebar-group");
      groups.forEach(function (group) {
        var items = group.querySelectorAll(".sidebar-item");
        var visibleCount = 0;
        
        items.forEach(function (item) {
          var title = item.textContent.toLowerCase();
          var slug = item.getAttribute("data-slug");
          var matches = title.includes(query) || slug.includes(query);
          
          item.style.display = matches ? "flex" : "none";
          if (matches) visibleCount++;
        });
        
        group.style.display = visibleCount > 0 ? "block" : "none";
      });
    });
    
    if (searchClear) {
      searchClear.addEventListener("click", function () {
        searchInput.value = "";
        searchClear.style.display = "none";
        searchInput.dispatchEvent(new Event("input"));
        searchInput.focus();
      });
    }
  }

  function initTabs() {
    var tabs = document.querySelectorAll(".pane-tab-btn");
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        tabs.forEach(function (t) { t.classList.remove("active"); });
        tab.classList.add("active");
        
        var target = tab.getAttribute("data-tab");
        var output = document.getElementById("output");
        var outputPt = document.getElementById("output-ptbuilder");
        
        if (target === "cli") {
          if (output) output.style.display = "block";
          if (outputPt) outputPt.style.display = "none";
        } else {
          if (output) output.style.display = "none";
          if (outputPt) outputPt.style.display = "block";
        }
      });
    });
  }

  /* ─── Embedded pt_analyzer.js (loaded inline so it works on file://) ─── */
  var PT_ANALYZER_JS = [
    "// Keystone PT Topology Analyzer",
    "// Reads all devices and their configs from an open topology",
    '// Output can be copied and used to recreate/modify topologies',
    "//",
    "// How to use:",
    "//   Extensions -> Scripting -> Edit File Script Module",
    "//   Paste this code, click Run",
    "//",
    "// Uses Java reflection to find the PT network when ipc.network()",
    "// is not available (PT 8.2.2 Script Module limitation).",
    "",
    "function getNetwork()",
    "{",
    "    try { if (typeof ipc !== \"undefined\" && typeof ipc.network === \"function\") { return ipc.network(); } } catch(e) {}",
    "    try { if (typeof network !== \"undefined\") { return network; } } catch(e) {}",
    "    try { if (this && typeof this.network !== \"undefined\") { return this.network; } } catch(e) {}",
    "",
    "    var visited = [];",
    "    function isNet(obj) { if (!obj || typeof obj !== \"object\") return false; try { return typeof obj.getDeviceCount === \"function\"; } catch(e) { return false; } }",
    "",
    "    function probe(obj, path)",
    "    {",
    "        if (!obj || typeof obj !== \"object\") return null;",
    "        try { var id = java.lang.System.identityHashCode(obj); if (visited.indexOf(id) >= 0) return null; visited.push(id); } catch(e) { return null; }",
    "        try { if (isNet(obj)) return obj; } catch(e) {}",
    "        var cls = obj.getClass ? obj.getClass() : null;",
    "        if (!cls) return null;",
    "        var cn = cls.getName() || \"\";",
    "        if (cn.indexOf(\"java.\") === 0 && cn.indexOf(\"javax.swing.\") !== 0) return null;",
    "        if (cn.indexOf(\"sun.\") === 0) return null;",
    "",
    "        try {",
    "            var methods = cls.getMethods();",
    "            for (var mi = 0; mi < methods.length && mi < 200; mi++) {",
    "                var m = methods[mi];",
    "                var mn = m.getName();",
    "                if (mn === \"getClass\" || mn === \"toString\" || mn === \"hashCode\" ||",
    "                    mn === \"equals\" || mn === \"notify\" || mn === \"wait\" ||",
    "                    mn === \"notifyAll\" || m.getParameterTypes().length > 0) continue;",
    "                if (mn.indexOf(\"get\") === 0 || mn.indexOf(\"is\") === 0 || mn.indexOf(\"has\") === 0) {",
    "                    try {",
    "                        m.setAccessible(true);",
    "                        var val = m.invoke(obj);",
    "                        if (val != null && val !== obj) { var r = probe(val, path + \".\" + mn + \"()\"); if (r != null) return r; }",
    "                    } catch(e2) {}",
    "                }",
    "            }",
    "        } catch(e) {}",
    "",
    "        try {",
    "            var fields = cls.getDeclaredFields();",
    "            for (var fi = 0; fi < fields.length && fi < 100; fi++) {",
    "                var f = fields[fi];",
    "                var ft = f.getType();",
    "                if (!ft || ft.isPrimitive() || ft === java.lang.String.class ||",
    "                    ft === java.lang.Boolean.class || ft === java.lang.Number.class) continue;",
    "                try {",
    "                    f.setAccessible(true);",
    "                    var val = f.get(obj);",
    "                    if (val != null && val !== obj) { var r = probe(val, path + \".\" + f.getName()); if (r != null) return r; }",
    "                } catch(e2) {}",
    "            }",
    "        } catch(e) {}",
    "",
    "        try {",
    "            if (obj instanceof java.awt.Container) {",
    "                var children = obj.getComponents();",
    "                for (var ci = 0; ci < children.length; ci++) { var r = probe(children[ci], path + \"[\" + ci + \"]\"); if (r != null) return r; }",
    "            }",
    "        } catch(e) {}",
    "        return null;",
    "    }",
    "",
    "    try { var frames = java.awt.Frame.getFrames(); for (var fi = 0; fi < frames.length; fi++) { var r = probe(frames[fi], \"frame[\" + fi + \"]\"); if (r != null) return r; } } catch(e) {}",
    "",
    "    try {",
    "        var probeClasses = [",
    '            "com.cisco.packettracer.PacketTracer",',
    '            "com.cisco.packettracer.network.NetworkManager",',
    '            "com.cisco.packettracer.NetworkManager",',
    '            "com.cisco.packettracer.TopologyManager",',
    '            "com.cisco.packettracer.CPD"',
    "        ];",
    "        for (var ci = 0; ci < probeClasses.length; ci++) {",
    "            try {",
    "                var clazz = java.lang.Class.forName(probeClasses[ci]);",
    "                try { var m = clazz.getMethod(\"getInstance\"); var inst = m.invoke(null); if (inst != null) { var r = probe(inst, probeClasses[ci] + \".getInstance()\"); if (r != null) return r; } } catch(e2) {}",
    "                try {",
    "                    var methods = clazz.getMethods();",
    "                    for (var mi = 0; mi < methods.length && mi < 100; mi++) {",
    "                        var m = methods[mi];",
    "                        if (m.getName() === \"getClass\" || m.getName() === \"toString\") continue;",
    "                        if (m.getParameterTypes() && m.getParameterTypes().length > 0) continue;",
    "                        try { var val = m.invoke(null); if (val != null) { var r = probe(val, probeClasses[ci] + \".\" + m.getName() + \"()\"); if (r != null) return r; } } catch(e3) {}",
    "                    }",
    "                } catch(e2) {}",
    "                try {",
    "                    var fields = clazz.getDeclaredFields();",
    "                    for (var fi = 0; fi < fields.length && fi < 50; fi++) {",
    "                        var f = fields[fi];",
    "                        var ft = f.getType();",
    "                        if (!ft || ft.isPrimitive() || ft === java.lang.String.class) continue;",
    "                        try { f.setAccessible(true); var val = f.get(null); if (val != null) { var r = probe(val, probeClasses[ci] + \".\" + f.getName()); if (r != null) return r; } } catch(e3) {}",
    "                    }",
    "                } catch(e2) {}",
    "            } catch(e2) {}",
    "        }",
    "    } catch(e) {}",
    "",
    "    return null;",
    "}",
    "",
    "function main()",
    "{",
    '    dprint("\\u2554\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2557");',
    '    dprint("\\u2551         KEYSTONE - PT TOPOLOGY ANALYZER v1.0          \\u2551");',
    '    dprint("\\u255a\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u2550\\u255d\\n");',
    "",
    "    try {",
    "        var network = getNetwork();",
    "        if (network == null) {",
        '            dprint("\\n\\u274c Cannot access network object.");',
        '            dprint("");',
        '            dprint("The Java reflection scan did not find the PT network object.");',
        '            dprint("This may be due to PT 8.2.2\'s internal class structure.");',
        '            dprint("");',
        '            dprint("Workaround: Save your topology as a .pkt file, then use");',
        "            dprint(\"the external 'ptexplorer.py' tool to convert it to XML and\");",
        '            dprint("extract the device configs. Or copy each device\'s running-config");',
        '            dprint("manually from PT\'s CLI tab.");',
        '            dprint("");',
    "            return;",
    "        }",
    "        var deviceCount = network.getDeviceCount();",
    "",
    '        dprint("TOPOLOGY SUMMARY");',
    '        dprint("Total devices: " + deviceCount);',
    '        dprint("");',
    "",
    "        if (deviceCount === 0) {",
    '            dprint("No devices found in topology!");',
    "            return;",
    "        }",
    "",
    '        dprint("PHASE 1: DEVICE ENUMERATION\\n");',
    "",
    "        var devices = [];",
    "        for (var i = 0; i < deviceCount; i++) {",
    "            var device = network.getDeviceAt(i);",
    "            var name = device.getName();",
    "            var model = device.getModel();",
    "            var type = \"unknown\";",
    "            try { type = device.getDescriptor().getType(); } catch(e) {}",
    "            var portCount = 0;",
    "            try { portCount = device.getPortCount(); } catch(e) {}",
    "",
    "            devices.push({",
    "                index: i, name: name, model: model, type: type, ports: portCount, device: device",
    "            });",
    "",
    '            dprint("[" + (i + 1) + "] " + name);',
    '            dprint("    Model: " + model);',
    '            dprint("    Type: " + type);',
    '            dprint("    Ports: " + portCount);',
    '            dprint("");',
    "        }",
    "",
    '        dprint("\\nPHASE 2: CONFIGURATION EXTRACTION\\n");',
    "",
    "        var configs = [];",
    "",
    "        for (var i = 0; i < devices.length; i++) {",
    "            var device = devices[i].device;",
    "            var deviceName = devices[i].name;",
    "",
    '            dprint("[Device " + (i + 1) + ": " + deviceName + "]");',
    "",
    "            try {",
    "                var cmdLine = device.getCommandLine();",
    "",
    "                if (cmdLine == null) {",
    '                    dprint("No CLI available");',
    "                    continue;",
    "                }",
    "",
    "                var output = cmdLine.getOutput();",
    '                if (output.indexOf("Would you like to enter the initial configuration dialog") > -1) {',
    '                    dprint("Skipping setup dialog...");',
    '                    cmdLine.enterCommand("no");',
    "                    java.lang.Thread.sleep(300);",
    "                }",
    "",
    '                dprint("Extracting running configuration...");',
    '                cmdLine.enterCommand("enable");',
    "                java.lang.Thread.sleep(100);",
    "",
    '                cmdLine.enterCommand("terminal length 0");',
    "                java.lang.Thread.sleep(100);",
    "",
    '                cmdLine.enterCommand("show running-config");',
    "                java.lang.Thread.sleep(500);",
    "",
    "                var config = cmdLine.getOutput();",
    "",
    '                var configStart = config.indexOf("Building configuration");',
    "                if (configStart === -1) {",
    '                    configStart = config.indexOf("Current configuration");',
    "                }",
    "                if (configStart === -1) {",
    '                    configStart = config.indexOf("!");',
    "                }",
    "",
    "                var cleanConfig = configStart > -1 ? config.substring(configStart) : config;",
    "",
    "                configs.push({",
    "                    device: deviceName, model: devices[i].model, config: cleanConfig, size: cleanConfig.length",
    "                });",
    "",
    '                dprint("Retrieved " + cleanConfig.length + " bytes");',
    "",
    "            } catch(e) {",
    '                dprint("Error: " + e.message);',
    "            }",
    "        }",
    "",
    '        dprint("\\nEXTRACTED CONFIGURATIONS\\n");',
    "",
    "        for (var i = 0; i < configs.length; i++) {",
    "            var cfg = configs[i];",
    '            dprint("DEVICE: " + cfg.device);',
    '            dprint("MODEL: " + cfg.model);',
    '            dprint("SIZE: " + cfg.size + " bytes");',
    '            dprint("");',
    "            dprint(cfg.config);",
    '            dprint("");',
    "        }",
    "",
    '        dprint("\\nSUMMARY");',
    "",
    "        var totalConfigSize = 0;",
    "        for (var i = 0; i < configs.length; i++) {",
    "            totalConfigSize += configs[i].size;",
    "        }",
    "",
    '        dprint("Total devices analyzed: " + configs.length);',
    '        dprint("Total config size: " + totalConfigSize + " bytes");',
    "",
    "    } catch(e) {",
    '        dprint("FATAL ERROR: " + e.message);',
    "    }",
    "}",
    "",
    "function cleanUp()",
    "{",
    '    dprint("Analyzer cleanup complete.");',
    "}"
  ].join("\n");

  /* ─── Extract from PT helper ─── */
  function genExtractFromPt(input, output, outputPt) {
    var text = (input ? input.value : "").trim();

    // First click or empty -> show instructions, copy JS, put JS in PT-Builder tab
    if (!text || text.indexOf("DEVICE:") === -1) {
      output.value = "! ========================================\n"
        + "! EXTRACT FROM PACKET TRACER - INSTRUCTIONS\n"
        + "! ========================================\n!\n"
        + "! 1. The pt_analyzer.js is ready in the PT-Builder tab below\n"
        + "! 2. In Packet Tracer, run the script via:\n"
        + "!    Extensions \u2192 Scripting \u2192 Manage ExApps \u2192 Add \u2192 Paste \u2192 Run\n"
        + "!    OR Extensions \u2192 Scripting \u2192 Edit File Script Module \u2192 Paste \u2192 Run\n"
        + "! 3. Copy ALL output from the PT console (Ctrl+A, Ctrl+C)\n"
        + "! 4. Paste it into the editor (REPLACE this template text)\n"
        + "! 5. Click GENERATE again to parse into YAML\n";

      if (outputPt) {
        outputPt.value = PT_ANALYZER_JS;
        outputPt.style.display = "";
      }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(PT_ANALYZER_JS).catch(function() {});
      }
      var st = document.getElementById("output-status");
      if (st) st.textContent = "JS copied to clipboard";
      updateLineCount();
      return;
    }

    // Second click: text contains DEVICE: -> parse output
    var blocks = [];
    var current = null;
    var configLines = [];
    var inHeader = false;

    var lines = text.split("\n");
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var dm = line.match(/^DEVICE:\s*(.+)/);
      var mm = line.match(/^MODEL:\s*(.+)/);

      if (dm) {
        if (current && configLines.length > 0) {
          current.config = configLines.join("\n");
          blocks.push(current);
        }
        current = { device: dm[1].trim(), model: "", config: "" };
        configLines = [];
        inHeader = true;
        continue;
      }
      if (mm && current) {
        current.model = mm[1].trim();
        inHeader = true;
        continue;
      }

      if (inHeader && current) {
        var st = line.trim();
        if (st.match(/^SIZE:/) || st === "" || st.match(/^[━═]{2,}/)) continue;
        inHeader = false;
      }

      if (current && !inHeader) configLines.push(line);
    }
    if (current && configLines.length > 0) {
      current.config = configLines.join("\n");
      blocks.push(current);
    }

    if (blocks.length === 0) {
      output.value = "# No device configurations found.\n"
        + "# Make sure you pasted the full pt_analyzer.js output\n"
        + "# with DEVICE: names and running configs.";
      return;
    }

    var MODEL_MAP = {
      "2911": "router", "2960": "switch", "5506-X": "firewall",
      "PC-PT": "pc", "Laptop-PT": "laptop", "Server-PT": "server"
    };

    var yamlLines = [
      "# Topology parsed from Packet Tracer analyzer output",
      "# Generated by Keystone",
      "# Devices: " + blocks.length,
      "devices:"
    ];

    for (var bi = 0; bi < blocks.length; bi++) {
      var blk = blocks[bi];
      var dtype = "router";
      for (var mk in MODEL_MAP) {
        if (blk.model.indexOf(mk) >= 0) { dtype = MODEL_MAP[mk]; break; }
      }
      yamlLines.push("  - hostname: " + blk.device);
      yamlLines.push("    type: " + dtype);

      var cfgLines = blk.config.split("\n");
      var interfaces = [];
      var currentIface = null;

      for (var ci = 0; ci < cfgLines.length; ci++) {
        var cl = cfgLines[ci].trim();
        if (!cl || cl.charAt(0) === "!") continue;
        var im = cl.match(/^interface\s+(\S+)/);
        if (im) { currentIface = { name: im[1] }; interfaces.push(currentIface); continue; }
        if (currentIface) {
          var ipm = cl.match(/^ip address\s+(\S+)\s+(\S+)/);
          if (ipm) { currentIface.ip = ipm[1]; currentIface.mask = ipm[2]; continue; }
          var dm2 = cl.match(/^description\s+(.+)/);
          if (dm2) { currentIface.description = dm2[1].replace(/"/g, ""); continue; }
        }
      }

      if (interfaces.length > 0) {
        yamlLines.push("    interfaces:");
        for (var ifi = 0; ifi < interfaces.length; ifi++) {
          var f = interfaces[ifi];
          yamlLines.push("      - name: " + f.name);
          if (f.ip) yamlLines.push("        ip: " + f.ip);
          if (f.mask) yamlLines.push("        mask: " + f.mask);
          if (f.description) yamlLines.push("        description: \"" + f.description + "\"");
        }
      }
    }

    output.value = yamlLines.join("\n");
    if (outputPt) {
      outputPt.value = "// Use the YAML output above with Full Topology generator\n"
        + "// to create a .pkt build script for this extracted topology.";
      outputPt.style.display = "";
    }
    var st = document.getElementById("output-status");
    if (st) st.textContent = blocks.length + " devices parsed";
    updateLineCount();
  }

  function boot() {
    /* ─── Tabs initialization ─── */
    initTabs();
    /* ─── Sidebar toggle ─── */
    var toggleBtn = document.getElementById("sidebar-toggle");
    if (toggleBtn) {
      toggleBtn.addEventListener("click", function () {
        var sb = document.getElementById("sidebar");
        if (sb) sb.classList.toggle("collapsed");
      });
    }

    /* ─── Topbar title click -> Go to Dashboard ─── */
    var titleEl = document.getElementById("topbar-title");
    if (titleEl) {
      titleEl.style.cursor = "pointer";
      titleEl.addEventListener("click", function () {
        showDashboard();
      });
    }

    /* ─── Top bar actions (orchestrator IDs + standalone fallback) ─── */
    var genBtn = document.getElementById("action-generate") || document.getElementById("run");
    var resetBtn = document.getElementById("action-reset") || document.getElementById("reset");
    var copyBtn = document.getElementById("action-copy") || document.getElementById("copy");

    if (genBtn) genBtn.addEventListener("click", doGenerate);
    if (resetBtn) resetBtn.addEventListener("click", doReset);
    if (copyBtn) copyBtn.addEventListener("click", doCopy);

    /* ─── Keyboard shortcut ─── */
    document.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        doGenerate();
      }
    });

    /* ─── Line count & validation tracking ─── */
    var inputEl = document.getElementById("input");
    if (inputEl) {
      inputEl.addEventListener("input", function () {
        scheduleLineCount();
        validateInput();
      });
    }

    /* ─── Init divider ─── */
    initDivider();

    /* ─── Determine active tool ─── */
    var initialSlug = null;

    /* Check hash first */
    if (window.location.hash) {
      initialSlug = window.location.hash.replace("#", "");
    }

    /* Check query param (for backward compat with tool.html?tool=x) */
    if (!initialSlug || !TOOLS[initialSlug]) {
      var params = new URLSearchParams(window.location.search);
      var qs = params.get("tool");
      if (qs) initialSlug = qs;
    }

    /* Check standalone mode */
    var isStandalone = !document.getElementById("tool-list");
    if (isStandalone) {
      if (!initialSlug || !TOOLS[initialSlug]) {
        for (var s in TOOLS) { if (TOOLS.hasOwnProperty(s)) { initialSlug = s; break; } }
      }
      selectTool(initialSlug);
      initTheme();
      return;
    }

    /* If slug is dashboard or empty, show dashboard */
    if (initialSlug === "dashboard" || !initialSlug) {
      renderSidebar("");
      showDashboard();
      initTheme();
      initSearch();
      return;
    }

    /* Fall back to last active from localStorage */
    if (!initialSlug || !TOOLS[initialSlug]) {
      try { var saved = localStorage.getItem("keystone_active_slug"); if (saved) initialSlug = saved; } catch (e) {}
    }

    /* Fall back to dashboard if no valid slug is found */
    if (!initialSlug || !TOOLS[initialSlug]) {
      renderSidebar("");
      showDashboard();
      initTheme();
      initSearch();
      return;
    }

    /* Render sidebar */
    renderSidebar(initialSlug);

    /* Select tool */
    selectTool(initialSlug);

    /* Theme & Search */
    initTheme();
    initSearch();

    /* ─── Listen for hash changes ─── */
    window.addEventListener("hashchange", function () {
      var slug = window.location.hash.replace("#", "");
      if (slug === "dashboard" || !slug) {
        showDashboard();
      } else if (slug && TOOLS[slug] && slug !== activeSlug) {
        selectTool(slug);
      }
    });

    /* ─── Save state on page hide ─── */
    window.addEventListener("beforeunload", function () {
      doSaveState();
    });
  }

  function parseInput(text) {
    if (!text.trim()) throw new Error("Input is empty.");
    try {
      return window.jsyaml.load(text);
    } catch (yamlErr) {
      try {
        return JSON.parse(text);
      } catch {
        throw new Error(`Invalid YAML/JSON: ${yamlErr.message}`);
      }
    }
  }

  function asList(data) {
    if (Array.isArray(data)) return data;
    if (data && typeof data === "object") return [data];
    throw new Error("Input root must be an object or a list.");
  }

  function ipv4ToInt(ip) {
    const p = String(ip).split(".").map(Number);
    if (p.length !== 4 || p.some((n) => Number.isNaN(n) || n < 0 || n > 255)) throw new Error(`Invalid IPv4: ${ip}`);
    return ((p[0] << 24) >>> 0) + ((p[1] << 16) >>> 0) + ((p[2] << 8) >>> 0) + (p[3] >>> 0);
  }

  function intToIPv4(n) {
    return [n >>> 24, (n >>> 16) & 255, (n >>> 8) & 255, n & 255].join(".");
  }

  function wildcardFromMask(mask) {
    return mask.split(".").map((n) => 255 - Number(n)).join(".");
  }

  function ipAndMaskToNetwork(ip, mask) {
    return intToIPv4(ipv4ToInt(ip) & ipv4ToInt(mask));
  }

  function prefixFromMask(mask) {
    const bits = mask.split(".").map((n) => Number(n).toString(2).padStart(8, "0")).join("");
    return bits.indexOf("0") === -1 ? 32 : bits.indexOf("0");
  }

  function isIPv6(s) {
    return String(s).includes(":");
  }

  const MAX128 = (1n << 128n) - 1n;

  function parseIPv6ToBigInt(input) {
    const addr = String(input).split("/")[0];
    const [leftPart, rightPart = ""] = addr.split("::");
    const left = leftPart ? leftPart.split(":").filter(Boolean) : [];
    const right = rightPart ? rightPart.split(":").filter(Boolean) : [];
    if (leftPart.includes("::") || rightPart.includes("::")) throw new Error(`Invalid IPv6: ${input}`);
    const zeroFill = 8 - (left.length + right.length);
    if (zeroFill < 0) throw new Error(`Invalid IPv6: ${input}`);
    const groups = [...left, ...Array(zeroFill).fill("0"), ...right].map((g) => parseInt(g || "0", 16));
    if (groups.length !== 8 || groups.some((n) => Number.isNaN(n) || n < 0 || n > 0xffff)) {
      throw new Error(`Invalid IPv6: ${input}`);
    }
    return groups.reduce((acc, g) => (acc << 16n) + BigInt(g), 0n);
  }

  function bigIntToIPv6(v) {
    const groups = [];
    let n = v & MAX128;
    for (let i = 0; i < 8; i++) {
      groups.unshift(Number(n & 0xffffn).toString(16));
      n >>= 16n;
    }
    let bestStart = -1, bestLen = 0;
    for (let i = 0; i < 8;) {
      if (groups[i] !== "0") { i++; continue; }
      let j = i;
      while (j < 8 && groups[j] === "0") j++;
      const len = j - i;
      if (len > bestLen && len > 1) { bestStart = i; bestLen = len; }
      i = j;
    }
    if (bestStart >= 0) {
      const left = groups.slice(0, bestStart).join(":");
      const right = groups.slice(bestStart + bestLen).join(":");
      if (!left && !right) return "::";
      if (!left) return `::${right}`;
      if (!right) return `${left}::`;
      return `${left}::${right}`;
    }
    return groups.join(":");
  }

  function maskForPrefix6(prefix) {
    if (prefix <= 0) return 0n;
    if (prefix >= 128) return MAX128;
    return (MAX128 << BigInt(128 - prefix)) & MAX128;
  }

  function bitLength(n) {
    let x = n, bits = 0n;
    while (x > 0n) { x >>= 1n; bits++; }
    return bits === 0n ? 1n : bits;
  }

  function randomBigInt(maxExclusive) {
    const bits = Number(bitLength(maxExclusive - 1n));
    while (true) {
      let r = 0n;
      for (let b = 0; b < bits; b += 24) {
        const chunk = Math.floor(Math.random() * (1 << 24));
        r = (r << 24n) + BigInt(chunk);
      }
      const mask = (1n << BigInt(bits)) - 1n;
      r &= mask;
      if (r < maxExclusive) return r;
    }
  }

  function genVlanWeaver(data) {
    return asList(data).map((entry) => {
      const lines = [`! --- ${entry.hostname} ---`, `! VLAN Configuration for ${entry.hostname}`];
      const vlans = entry.vlans || [];
      const used = new Set(vlans.filter((v) => v.id != null).map((v) => Number(v.id)));
      let nextId = 10;
      for (const vlan of vlans) {
        let id = vlan.id != null ? Number(vlan.id) : null;
        if (!id) {
          while (used.has(nextId)) nextId += 1;
          id = nextId;
          used.add(id);
        }
        lines.push(`vlan ${id}`);
        lines.push(` name ${vlan.name}`);
      }
      lines.push("exit");
      for (const vlan of vlans) {
        if (vlan.id && vlan.ipv6) {
          lines.push(`interface vlan ${Number(vlan.id)}`);
          lines.push(` ipv6 address ${vlan.ipv6}`);
          lines.push(" no shutdown");
          lines.push(" exit");
        }
      }
      return lines.join("\n");
    }).join("\n\n");
  }

  function genSshLocksmith(data) {
    return asList(data).map((e) => {
      const lines = [
        `! --- ${e.hostname} ---`,
        `! SSH Security Configuration for ${e.hostname}`,
        `hostname ${e.hostname}`,
        `ip domain-name ${e.domain_name || "soymsa.local"}`,
        `crypto key generate rsa modulus ${e.key_size ?? 1024}`,
        `ip ssh version ${e.version ?? 2}`,
        `ip ssh time-out ${e.timeout ?? 60}`,
        `ip ssh authentication-retries ${e.retries ?? 3}`,
        `username ${e.username || "admin"} secret ${e.password || "Cisco123"}`
      ];
      if (e.enable_secret) lines.push(`enable secret ${e.enable_secret}`);
      if (e.ipv6_vty) {
        lines.push(`ipv6 access-list VTY_ACL`);
        lines.push(` permit tcp ${e.vty_acl_ipv6 || "2001:db8::/32"} any eq 22`);
        lines.push(" exit");
      }
      lines.push("line vty 0 15", " login local", " transport input ssh");
      if (e.ipv6_vty) lines.push(" ipv6 access-class VTY_ACL in");
      lines.push(" exit");
      return lines.join("\n");
    }).join("\n\n");
  }

  function genDhcpAllocator(data) {
    return asList(data).map((e) => {
      const lines = [`! --- ${e.hostname} ---`, `! DHCP Configuration for ${e.hostname}`];
      const excluded = e.excluded || [];
      if (excluded.length) {
        lines.push("! Excluded Addresses");
        for (const ex of excluded) {
          lines.push(ex.end ? `ip dhcp excluded-address ${ex.start} ${ex.end}` : `ip dhcp excluded-address ${ex.start}`);
        }
      }
      for (const p of (e.pools || [])) {
        lines.push(`ip dhcp pool ${p.name}`);
        lines.push(` network ${p.network} ${p.mask}`);
        lines.push(` default-router ${p.gateway}`);
        lines.push(` dns-server ${p.dns || "8.8.8.8"}`);
        lines.push(" exit");
      }
      for (const p of (e.ipv6_pools || [])) {
        lines.push(`ipv6 dhcp pool ${p.name}`);
        lines.push(` prefix-delegation pool ${p.prefix}`);
        if (p.dns) lines.push(` dns-server ${p.dns}`);
        lines.push(" exit");
      }
      return lines.join("\n");
    }).join("\n\n");
  }

  function genHsrpSentinel(data) {
    return asList(data).map((e) => {
      const lines = [`! --- ${e.hostname} ---`, `! HSRP & SVI Configuration for ${e.hostname}`];
      for (const i of (e.interfaces || [])) {
        lines.push(`interface vlan ${i.vlan_id}`);
        if (i.ip && i.hsrp_ip) {
          lines.push(` ip address ${i.ip} ${i.mask}`);
          lines.push(` standby ${i.vlan_id} ip ${i.hsrp_ip}`);
          lines.push(` standby ${i.vlan_id} priority ${i.priority ?? 100}`);
          lines.push(` standby ${i.vlan_id} preempt`);
        }
        if (i.ipv6 && i.hsrp_ipv6) {
          lines.push(` ipv6 address ${i.ipv6}/${i.ipv6_mask ?? 64}`);
          lines.push(` standby ${i.vlan_id} ipv6 ${i.hsrp_ipv6}`);
          lines.push(` standby ${i.vlan_id} priority ${i.priority ?? 100}`);
          lines.push(` standby ${i.vlan_id} preempt`);
        }
        lines.push(" no shutdown");
        lines.push(" exit");
      }
      return lines.join("\n");
    }).join("\n\n");
  }

  function genStaticAnchor(data) {
    return asList(data).map((e) => {
      const lines = [`! --- ${e.hostname} ---`, `! Static Routes for ${e.hostname}`];
      for (const r of (e.routes || [])) {
        const target = r.next_hop && r.exit_interface ? `${r.exit_interface} ${r.next_hop}` : (r.next_hop || r.exit_interface || "");
        const v6 = isIPv6(r.network);
        let cmd = v6
          ? `ipv6 route ${String(r.network).includes("/") ? r.network : `${r.network}/${r.mask}`} ${target}`.trim()
          : `ip route ${r.network} ${r.mask} ${target}`.trim();
        if ((r.distance ?? 1) !== 1) cmd += ` ${r.distance}`;
        if (r.description) lines.push(`! ${r.description}`);
        lines.push(cmd);
      }
      return lines.join("\n");
    }).join("\n\n");
  }

  function genNatPortal(data) {
    return asList(data).map((e) => {
      const lines = [`! --- ${e.hostname} ---`, `! Master NAT/PAT Configuration for ${e.hostname}`, "! Interface NAT Roles"];
      const useNvi = !!e.use_nvi;
      const insideCmd = useNvi ? "ip nat enable" : "ip nat inside";
      const outsideCmd = useNvi ? "ip nat enable" : "ip nat outside";
      for (const i of (e.inside_interfaces || [])) lines.push(`interface ${i}`, ` ${insideCmd}`);
      for (const o of (e.outside_interfaces || [])) lines.push(`interface ${o}`, ` ${outsideCmd}`);
      lines.push("exit");

      if (e.acls && Object.keys(e.acls).length) {
        lines.push("! NAT Access Control Lists");
        for (const [aclId, nets] of Object.entries(e.acls)) {
          for (const n of nets) lines.push(`access-list ${aclId} permit ${n}`);
        }
      }

      if ((e.pools || []).length) {
        lines.push("! NAT Pools");
        for (const p of e.pools) {
          lines.push(`ip nat pool ${p.name} ${p.start} ${p.end} prefix-length ${p.prefix}`);
        }
      }

      let rules = e.rules || [];
      if (!rules.length && Array.isArray(e.static_nats)) {
        rules = e.static_nats.map((n) => ({
          rule_type: "static",
          local_ip: n.inside_ip,
          global_ip: n.outside_ip
        }));
      }

      if (rules.length) {
        lines.push("! NAT Translation Rules");
        for (const r of rules) {
          if (r.description) lines.push(`! ${r.description}`);
          if (r.rule_type === "static") lines.push(`ip nat inside source static ${r.local_ip} ${r.global_ip}`);
          else if (r.rule_type === "port-forward") lines.push(`ip nat inside source static ${r.protocol || "tcp"} ${r.local_ip} ${r.local_port} ${r.global_ip} ${r.global_port} extendable`);
          else if (r.rule_type === "dynamic") lines.push(`ip nat inside source list ${r.acl_id} pool ${r.pool}`);
          else if (r.rule_type === "overload") {
            const target = r.interface ? `interface ${r.interface}` : `pool ${r.pool}`;
            lines.push(`ip nat inside source list ${r.acl_id} ${target} overload`);
          }
        }
      }

      const ipv6Nats = e.ipv6_nats || [];
      if (ipv6Nats.length) {
        lines.push("! IPv6 NAT / NAT64");
        for (const r of ipv6Nats) {
          if (r.description) lines.push(`! ${r.description}`);
          if (r.rule_type === "static") lines.push(`ipv6 nat source static ${r.local_ipv6} ${r.global_ipv6}`);
        }
      }

      return lines.join("\n");
    }).join("\n\n");
  }

  function genAsaShield(data) {
    return asList(data).map((e) => {
      const lines = [`! --- ${e.hostname} ---`, `! ASA_Shield Configuration for ${e.hostname}`, "terminal width 132", "! Interfaces"];
      for (const i of (e.interfaces || [])) {
        lines.push(`interface ${i.name}`, ` nameif ${i.nameif}`, ` security-level ${i.security_level}`);
        if (i.ip && i.mask) lines.push(` ip address ${i.ip} ${i.mask}`);
        if (i.ipv6) lines.push(` ipv6 address ${i.ipv6}/${i.ipv6_mask ?? 64}`);
        lines.push(" no shutdown");
      }
      lines.push("! Network Objects");
      for (const o of (e.objects || [])) {
        lines.push(`object network ${o.name}`);
        if (o.host) lines.push(` host ${o.host}`);
        else if (o.subnet && o.mask) lines.push(` subnet ${o.subnet} ${o.mask}`);
        else if (o.ipv6_host) lines.push(` host ${o.ipv6_host}`);
        else if (o.ipv6_subnet) lines.push(` subnet ${o.ipv6_subnet}`);
      }
      lines.push("! NAT");
      for (const n of (e.nats || [])) {
        if ((n.type || "dynamic") === "dynamic") {
          lines.push(`object network ${n.obj_name}`);
          lines.push(` nat (inside,${n.translated_interface || "outside"}) dynamic interface`);
        } else {
          lines.push(`! Manual NAT config required for ${n.obj_name}`);
        }
      }
      lines.push("! ACLs");
      for (const a of (e.acls || [])) {
        const service = a.service ? ` ${a.service}` : "";
        lines.push(`access-list ${a.access_list} extended ${a.action} ${a.protocol} ${a.source} ${a.destination}${service}`);
      }
      lines.push("! Access Groups");
      for (const [name, iface] of Object.entries(e.access_groups || {})) {
        lines.push(`access-group ${name} in interface ${iface}`);
      }
      return lines.join("\n");
    }).join("\n\n");
  }

  function genBgpConductor(data) {
    return asList(data).map((e) => {
      const lines = [`! --- ${e.hostname} ---`, `! BGP Configuration for ${e.hostname}`, `router bgp ${e.as_number}`];
      if (e.router_id) lines.push(` bgp router-id ${e.router_id}`);
      lines.push(" bgp log-neighbor-changes");
      const neighbors = e.neighbors || [];
      for (const n of neighbors) {
        lines.push(` neighbor ${n.ip} remote-as ${n.remote_as}`);
        if (n.description) lines.push(` neighbor ${n.ip} description ${n.description}`);
        if (n.update_source) lines.push(` neighbor ${n.ip} update-source ${n.update_source}`);
        if (n.next_hop_self) lines.push(` neighbor ${n.ip} next-hop-self`);
        if (n.ebgp_multihop) lines.push(` neighbor ${n.ip} ebgp-multihop ${n.ebgp_multihop}`);
      }
      const networks = e.networks || [];
      const v4N = neighbors.filter((n) => !isIPv6(n.ip));
      const v6N = neighbors.filter((n) => isIPv6(n.ip));
      const v4Net = networks.filter((n) => !isIPv6(n.network));
      const v6Net = networks.filter((n) => isIPv6(n.network));
      if (v4N.length || v4Net.length) {
        lines.push(" address-family ipv4");
        for (const n of v4N) lines.push(`  neighbor ${n.ip} activate`);
        for (const n of v4Net) lines.push(`  network ${n.network} mask ${n.mask}`);
        lines.push(" exit-address-family");
      }
      if (v6N.length || v6Net.length) {
        lines.push(" address-family ipv6");
        for (const n of v6N) lines.push(`  neighbor ${n.ip} activate`);
        for (const n of v6Net) lines.push(`  network ${String(n.network).includes("/") ? n.network : `${n.network}/${n.mask}`}`);
        lines.push(" exit-address-family");
      }
      lines.push(" exit");
      return lines.join("\n");
    }).join("\n\n");
  }

  function genEigrpCatalyst(data) {
    return asList(data).map((e) => {
      const lines = [`! --- ${e.hostname} ---`, `! EIGRP Configuration for ${e.hostname}`];
      const interfaces = e.interfaces || [];
      if (e.ipv6_as_number != null) {
        for (const iface of interfaces) {
          if (iface.ipv6_enabled) {
            lines.push(`interface ${iface.name}`);
            lines.push(` ipv6 eigrp ${e.ipv6_as_number}`);
            lines.push(" exit");
          }
        }
      }
      lines.push(`router eigrp ${e.as_number}`);
      if (e.router_id) lines.push(` eigrp router-id ${e.router_id}`);
      if (e.is_stub) lines.push(" eigrp stub connected summary");
      for (const iface of interfaces) if (iface.is_passive) lines.push(` passive-interface ${iface.name}`);
      const networks = new Set();
      for (const iface of interfaces) {
        if (iface.ip_address && iface.subnet_mask && !isIPv6(iface.ip_address)) {
          networks.add(` network ${ipAndMaskToNetwork(iface.ip_address, iface.subnet_mask)} ${wildcardFromMask(iface.subnet_mask)}`);
        }
      }
      [...networks].sort().forEach((n) => lines.push(n));
      lines.push(" no auto-summary");
      lines.push(" exit");

      if (e.ipv6_as_number != null) {
        lines.push(`ipv6 router eigrp ${e.ipv6_as_number}`);
        if (e.router_id) lines.push(` eigrp router-id ${e.router_id}`);
        if (e.is_stub) lines.push(" eigrp stub connected summary");
        for (const iface of interfaces) if (iface.is_passive && iface.ipv6_enabled) lines.push(` passive-interface ${iface.name}`);
        lines.push(" no shutdown");
        lines.push(" exit");
      }
      return lines.join("\n");
    }).join("\n\n");
  }

  function genOspfPathmaker(data) {
    return asList(data).map((e) => {
      const lines = [`! --- ${e.hostname} ---`, `! OSPF Configuration for ${e.hostname}`];
      const proc = e.process_id ?? 1;
      const v6Proc = e.ipv6_process_id;
      const useIface = !!e.use_interface_config;
      const interfaces = e.interfaces || [];

      if (v6Proc != null) lines.push("ipv6 unicast-routing");

      for (const iface of interfaces) {
        const il = [];
        if (iface.ip_address && iface.subnet_mask) il.push(` ip address ${iface.ip_address} ${iface.subnet_mask}`);
        if (iface.ipv6_address) il.push(` ipv6 address ${iface.ipv6_address}`);
        if (useIface) {
          il.push(` ip ospf ${proc} area ${iface.area ?? 0}`);
          if (iface.auth_type === "message-digest") {
            il.push(" ip ospf authentication message-digest");
            il.push(` ip ospf message-digest-key 1 md5 ${iface.auth_key}`);
          } else if (iface.auth_type === "cleartext") {
            il.push(" ip ospf authentication");
            il.push(` ip ospf authentication-key ${iface.auth_key}`);
          }
        }
        if (v6Proc != null && iface.ipv6_area != null) il.push(` ipv6 ospf ${v6Proc} area ${iface.ipv6_area}`);
        if (il.length) {
          lines.push(`interface ${iface.name}`);
          lines.push(...il);
          lines.push(" no shutdown");
          lines.push(" exit");
        }
      }

      lines.push(`router ospf ${proc}`);
      lines.push(` router-id ${e.router_id}`);
      for (const iface of interfaces) if (iface.is_passive) lines.push(` passive-interface ${iface.name}`);
      if (!useIface) {
        const netLines = new Set();
        for (const iface of interfaces) {
          if (iface.ip_address && iface.subnet_mask && !isIPv6(iface.ip_address)) {
            netLines.add(` network ${ipAndMaskToNetwork(iface.ip_address, iface.subnet_mask)} ${wildcardFromMask(iface.subnet_mask)} area ${iface.area ?? 0}`);
          }
        }
        [...netLines].sort().forEach((n) => lines.push(n));
      }
      lines.push(" exit");

      if (v6Proc != null) {
        lines.push(`ipv6 router ospf ${v6Proc}`);
        lines.push(` router-id ${e.router_id}`);
        for (const iface of interfaces) if (iface.is_passive) lines.push(` passive-interface ${iface.name}`);
        lines.push(" exit");
      }

      return lines.join("\n");
    }).join("\n\n");
  }

  function randomIPv4FromSubnet(ip, mask, count) {
    const prefix = prefixFromMask(mask);
    const net = ipv4ToInt(ipAndMaskToNetwork(ip, mask));
    const total = 2 ** (32 - prefix);
    const first = prefix >= 31 ? net : net + 1;
    const last = prefix >= 31 ? net + total - 1 : net + total - 2;
    const seen = new Set();
    const max = Math.max(0, Math.min(count, last - first + 1));
    while (seen.size < max) seen.add(intToIPv4(first + Math.floor(Math.random() * (last - first + 1))));
    return [...seen];
  }

  function randomIPv6FromSubnet(ip, prefixLen, count) {
    const p = Number(prefixLen);
    const addr = parseIPv6ToBigInt(ip);
    const network = addr & maskForPrefix6(p);
    const hostBits = 128 - p;
    
    // Safety check for tiny subnets /127, /128 loopback / point-to-point links
    // to prevent infinite loops in randomBigInt.
    if (hostBits <= 2) {
      const size = 1n << BigInt(hostBits);
      const result = [];
      const max = Math.min(BigInt(count), size);
      for (let i = 0n; i < max; i++) {
        result.push(bigIntToIPv6(network + i));
      }
      return result;
    }
    
    const size = 1n << BigInt(hostBits);
    const first = network + 1n;
    const last = network + size - 2n;
    const result = new Set();
    const max = Math.min(count, 5);
    while (result.size < max) {
      const r = first + randomBigInt(last - first + 1n);
      result.add(bigIntToIPv6(r));
    }
    return [...result];
  }

  function randomIPsFromRange(classId, ipv6, count) {
    const v4 = { A: "10.0.0.0/8", B: "172.16.0.0/12", C: "192.168.0.0/16" };
    const v6 = { A: "fc00::/32", B: "fc00:0:100::/40", C: "fc00:0:200::/48" };
    const cidr = (ipv6 ? v6 : v4)[classId];
    if (!cidr) return [];
    if (!ipv6) {
      const [base, pref] = cidr.split("/");
      const prefix = Number(pref);
      const net = ipv4ToInt(base);
      const total = 2 ** (32 - prefix);
      const first = net + 1;
      const last = net + total - 2;
      const out = new Set();
      while (out.size < count) out.add(intToIPv4(first + Math.floor(Math.random() * (last - first + 1))));
      return [...out];
    }
    const [base, pref] = cidr.split("/");
    const prefix = Number(pref);
    const net = parseIPv6ToBigInt(base) & maskForPrefix6(prefix);
    const first = net + 1n;
    const last = net + (1n << BigInt(128 - prefix)) - 2n;
    const out = new Set();
    while (out.size < count) out.add(bigIntToIPv6(first + randomBigInt(last - first + 1n)));
    return [...out];
  }

  var IP_CLASS_RANGES_V4 = { A: "10.0.0.0/8", B: "172.16.0.0/12", C: "192.168.0.0/16" };
  var IP_CLASS_RANGES_V6 = { A: "fc00::/32", B: "fc00:0:100::/40", C: "fc00:0:200::/48" };

  function genIpArchitect(data) {
    const entries = asList(data);
    const blocks = [];
    for (const e of entries) {
      if (e.interfaces) {
        const lines = [`--- Generating Random IPs from ${e.hostname || "Unknown"} Interfaces ---`, ""];
        for (const iface of e.interfaces) {
          if (!iface.ip || iface.mask == null) continue;
          const v6 = isIPv6(iface.ip);
          const generated = v6
            ? randomIPv6FromSubnet(iface.ip, iface.mask, 5)
            : randomIPv4FromSubnet(iface.ip, iface.mask, 5);
          lines.push(`Interface: ${iface.name || "Unknown"}`);
          lines.push(`  Network: ${iface.ip}/${iface.mask} (${v6 ? "IPv6" : "IPv4"})`);
          lines.push("  Generated IPs:");
          generated.forEach((ip, i) => lines.push(`    ${i + 1}. ${ip}`));
          lines.push("");
        }
        blocks.push(lines.join("\n").trimEnd());
      } else if (e.random_ips) {
        const cfg = e.random_ips || {};
        const count = Number(cfg.count ?? 5);
        const classes = cfg.classes || ["C"];
        const useV6 = !!cfg.ipv6;
        const lines = [`--- Generating Random ${useV6 ? "IPv6" : "IPv4"} Private IPs ---`, ""];
        for (const cls of classes) {
          const per = classes.length > 1 ? Math.floor(count / classes.length) : count;
          const ips = randomIPsFromRange(cls, useV6, Math.max(1, per));
          const range = useV6
            ? IP_CLASS_RANGES_V6[cls]
            : IP_CLASS_RANGES_V4[cls];
          lines.push(`Class ${cls} (${range}, ${useV6 ? "IPv6" : "IPv4"}):`);
          ips.forEach((ip, i) => lines.push(`  ${i + 1}. ${ip}`));
          lines.push("");
        }
        blocks.push(lines.join("\n").trimEnd());
      }
    }
    return blocks.join("\n\n");
  }

  function findBestPrefixV4(hosts) {
    if (hosts < 0) return null;
    if (hosts === 0) return 32;
    const bits = Math.ceil(Math.log2(hosts + 2));
    const prefix = 32 - bits;
    return prefix < 0 ? null : prefix;
  }

  function cidrBlockDetailsV4(networkInt, prefix) {
    const size = 2 ** (32 - prefix);
    const bcast = networkInt + size - 1;
    const first = prefix < 31 ? networkInt + 1 : null;
    const last = prefix < 31 ? bcast - 1 : null;
    const totalHosts = prefix < 31 ? size - 2 : (prefix === 31 ? 2 : 1);
    const maskInt = prefix === 0 ? 0 : ((0xffffffff << (32 - prefix)) >>> 0);
    return {
      cidr: `${intToIPv4(networkInt)}/${prefix}`,
      prefix,
      netmask: intToIPv4(maskInt),
      wildcard: intToIPv4((~maskInt) >>> 0),
      network: intToIPv4(networkInt),
      broadcast: intToIPv4(bcast),
      first: first == null ? "N/A" : intToIPv4(first),
      last: last == null ? "N/A" : intToIPv4(last),
      totalHosts,
      nextNetwork: bcast + 1
    };
  }

  function parseIPv4Cidr(cidr) {
    const [ip, p] = String(cidr).split("/");
    const prefix = Number(p);
    const ipInt = ipv4ToInt(ip);
    const mask = prefix === 0 ? 0 : ((0xffffffff << (32 - prefix)) >>> 0);
    return { networkInt: (ipInt & mask) >>> 0, prefix };
  }

  function parseIPv6Cidr(cidr) {
    const [ip, p] = String(cidr).split("/");
    const prefix = Number(p);
    const network = parseIPv6ToBigInt(ip) & maskForPrefix6(prefix);
    return { network, prefix };
  }

  function genCidrArchitect(data) {
    const entries = asList(data);
    const out = [];
    for (const cfg of entries) {
      if (cfg.network && Array.isArray(cfg.subnets)) {
        if (isIPv6(cfg.network)) {
          const { network, prefix } = parseIPv6Cidr(cfg.network);
          out.push(`=== CIDR Subnet Allocation Plan (IPv6) ===`, ``, `Base Network: ${cfg.network}`, `Total Capacity: 2^${128 - prefix} addresses (essentially unlimited)`, ``, `${"=".repeat(70)}`, ``);
          cfg.subnets.forEach((s, idx) => {
            const subnet = network + (BigInt(idx) * (1n << 64n));
            const cidr = `${bigIntToIPv6(subnet)}/64`;
            out.push(
              `[${idx + 1}] ${s.name}`,
              `    Requested: ${s.size}`,
              `    CIDR: ${cidr} (/64)`,
              `    Network Address: ${bigIntToIPv6(subnet)}`,
              `    Prefix (IPv6): /64`,
              `    Total Addresses: ${2n ** 64n}`,
              ``
            );
          });
          out.push(`${"=".repeat(70)}`, `Summary: ${cfg.subnets.length} /64 subnets allocated`, ``);
        } else {
          const { networkInt, prefix } = parseIPv4Cidr(cfg.network);
          const totalCapacity = (2 ** (32 - prefix)) - 2;
          out.push(`=== CIDR Subnet Allocation Plan (IPv4) ===`, ``, `Base Network: ${cfg.network}`, `Total Capacity: ${totalCapacity} usable hosts`, `Netmask: ${intToIPv4(prefix === 0 ? 0 : ((0xffffffff << (32 - prefix)) >>> 0))}`, ``, `${"=".repeat(70)}`, ``);
          let current = networkInt;
          let totalPlanned = 0;
          cfg.subnets.forEach((s, idx) => {
            const pfx = findBestPrefixV4(Number(s.size));
            if (pfx == null) return;
            const d = cidrBlockDetailsV4(current, pfx);
            totalPlanned += d.totalHosts;
            out.push(
              `[${idx + 1}] ${s.name}`,
              `    Requested: ${s.size}`,
              `    CIDR: ${d.cidr} (/${d.prefix})`,
              `    Netmask: ${d.netmask}`,
              `    Network Address: ${d.network}`,
              `    Broadcast Address: ${d.broadcast}`,
              `    Usable Range: ${d.first} - ${d.last}`,
              `    Gateway: ${d.first}`,
              `    Total Addresses: ${d.totalHosts}`,
              ``
            );
            current = d.nextNetwork;
          });
          const util = totalCapacity > 0 ? ((totalPlanned / totalCapacity) * 100).toFixed(1) : "0.0";
          out.push(`${"=".repeat(70)}`, `Summary: ${cfg.subnets.length} subnets | ${totalPlanned} total hosts`, `Utilization: ${util}%`, ``);
        }
      } else if (cfg.hosts != null) {
        const hosts = Number(cfg.hosts);
        const base = cfg.base || "192.168.1.0";
        const pfx = findBestPrefixV4(hosts);
        if (pfx == null) {
          out.push(`Error: Could not find a valid subnet for ${hosts} hosts.`);
          continue;
        }
        const baseInt = ipv4ToInt(base);
        const maskInt = pfx === 0 ? 0 : ((0xffffffff << (32 - pfx)) >>> 0);
        const d = cidrBlockDetailsV4(baseInt & maskInt, pfx);
        out.push(
          `=== Subnet Plan for ${hosts} Hosts ===`,
          `Recommended Prefix: /${d.prefix}`,
          `Network Address:    ${d.network}`,
          `Subnet Mask:        ${d.netmask}`,
          `Wildcard Mask:      ${d.wildcard}`,
          `Broadcast Address:  ${d.broadcast}`,
          `Usable Range:       ${d.first} - ${d.last}`,
          `Total Usable Hosts: ${d.totalHosts}`,
          ``
        );
      }
    }
    return out.join("\n");
  }

  function genFullTopology(data) {
    var name = data.name || "Full Topology";
    var devices = data.devices || asList(data);
    var output = [];
    output.push("! ========================================");
    output.push("! Full Topology: " + name);
    output.push("! Generated by Keystone Automation");
    output.push("! ========================================");
    output.push("");
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i];
      if (!d || !d.hostname) continue;
      var lines = [];
      lines.push("! --- " + d.hostname + " ---");
      lines.push("hostname " + d.hostname);
      if (d.domain_name) lines.push("ip domain-name " + d.domain_name);
      if (d.vlans && d.vlans.length) {
        lines.push("! VLANs");
        for (var v = 0; v < d.vlans.length; v++) {
          var vl = d.vlans[v];
          if (vl.id) { lines.push("vlan " + vl.id); if (vl.name) lines.push(" name " + vl.name); }
        }
        lines.push("exit");
        for (var v = 0; v < d.vlans.length; v++) {
          var vl = d.vlans[v];
          if (vl.id && (vl.ip || vl.ipv6)) {
            lines.push("interface vlan " + vl.id);
            if (vl.ip) lines.push(" ip address " + vl.ip + " " + vl.mask);
            if (vl.ipv6) lines.push(" ipv6 address " + vl.ipv6);
            lines.push(" no shutdown");
            lines.push(" exit");
          }
        }
      }
      if (d.interfaces) {
        for (var j = 0; j < d.interfaces.length; j++) {
          var f = d.interfaces[j];
          lines.push("interface " + f.name);
          if (f.description) lines.push(" description " + f.description);
          if (f.mode) { lines.push(" switchport mode " + f.mode); if (f.access_vlan) lines.push(" switchport access vlan " + f.access_vlan); if (f.trunk_allowed) lines.push(" switchport trunk allowed vlan " + f.trunk_allowed); }
          if (f.ip && f.mask) lines.push(" ip address " + f.ip + " " + f.mask);
          if (f.ipv6) lines.push(" ipv6 address " + f.ipv6);
          if (f.nameif) lines.push(" nameif " + f.nameif);
          if (f.security_level != null) lines.push(" security-level " + f.security_level);
          if (f.hsrp) {
            var hg = f.hsrp.group || 1;
            if (f.hsrp.ip) lines.push(" standby " + hg + " ip " + f.hsrp.ip);
            if (f.hsrp.priority) lines.push(" standby " + hg + " priority " + f.hsrp.priority);
            if (f.hsrp.preempt) lines.push(" standby " + hg + " preempt");
          }
          if (f.dhcp) { lines.push(" ip address dhcp"); }
          lines.push(" no shutdown"); lines.push(" exit");
        }
      }
      if (d.ospf) {
        var pid = d.ospf.process_id || 1;
        lines.push("router ospf " + pid);
        if (d.ospf.router_id) lines.push(" router-id " + d.ospf.router_id);
        if (d.interfaces) {
          for (var j = 0; j < d.interfaces.length; j++) {
            var f = d.interfaces[j];
            if (f.ip && f.mask) lines.push(" network " + ipAndMaskToNetwork(f.ip, f.mask) + " " + wildcardFromMask(f.mask) + " area " + (d.ospf.area || 0));
          }
        }
        lines.push(" exit");
      }
      if (d.eigrp) {
        var asNum = d.eigrp.as || 100;
        lines.push("router eigrp " + asNum);
        if (d.interfaces) {
          for (var j = 0; j < d.interfaces.length; j++) {
            var f = d.interfaces[j];
            if (f.ip && f.mask) lines.push(" network " + ipAndMaskToNetwork(f.ip, f.mask) + " " + wildcardFromMask(f.mask));
          }
        }
        lines.push(" no auto-summary"); lines.push(" exit");
      }
      if (d.bgp) {
        var bgpAs = d.bgp.as || 65000;
        lines.push("router bgp " + bgpAs);
        if (d.bgp.router_id) lines.push(" bgp router-id " + d.bgp.router_id);
        if (d.bgp.networks) {
          for (var j = 0; j < d.bgp.networks.length; j++) {
            var bn = d.bgp.networks[j];
            lines.push(" network " + bn.network + (bn.mask ? " mask " + bn.mask : ""));
          }
        }
        if (d.bgp.neighbors) {
          for (var j = 0; j < d.bgp.neighbors.length; j++) {
            var nbr = d.bgp.neighbors[j];
            var ras = nbr.remote_as || bgpAs;
            lines.push(" neighbor " + nbr.ip + " remote-as " + ras);
            if (nbr.update_source) lines.push(" neighbor " + nbr.ip + " update-source " + nbr.update_source);
            if (nbr.next_hop_self) lines.push(" neighbor " + nbr.ip + " next-hop-self");
            if (nbr.ebgp_multihop) lines.push(" neighbor " + nbr.ip + " ebgp-multihop " + nbr.ebgp_multihop);
          }
        }
        lines.push(" exit");
      }
      if (d.routes) {
        for (var j = 0; j < d.routes.length; j++) {
          var r = d.routes[j];
          var tgt = r.next_hop || "";
          if (isIPv6(r.network)) lines.push("ipv6 route " + r.network + "/" + r.mask + " " + tgt);
          else lines.push("ip route " + r.network + " " + r.mask + " " + tgt);
        }
      }
      if (d.dhcp && d.dhcp.pools) {
        for (var j = 0; j < d.dhcp.pools.length; j++) {
          var p = d.dhcp.pools[j];
          lines.push("ip dhcp pool " + p.name);
          lines.push(" network " + p.network + " " + p.mask);
          lines.push(" default-router " + p.gateway);
          if (p.dns) lines.push(" dns-server " + p.dns);
          lines.push(" exit");
        }
      }
      if (d.dhcp && d.dhcp.ipv6_pools) {
        for (var j = 0; j < d.dhcp.ipv6_pools.length; j++) {
          var p = d.dhcp.ipv6_pools[j];
          lines.push("ipv6 dhcp pool " + p.name);
          lines.push(" prefix-delegation pool " + p.prefix);
          if (p.dns) lines.push(" dns-server " + p.dns);
          lines.push(" exit");
        }
      }
      if (d.nat) {
        for (var j = 0; j < d.nat.length; j++) {
          var n = d.nat[j];
          if (n.type === "dynamic") lines.push("ip nat inside source list " + (n.acl_id || "1") + " interface " + n.outside_interface + " overload");
        }
      }
      if (d.ssh) {
        lines.push("crypto key generate rsa modulus " + (d.ssh.key_size || 2048));
        lines.push("ip ssh version 2");
        lines.push("username " + (d.ssh.username || "admin") + " secret " + (d.ssh.password || "cisco"));
        if (d.ssh.ipv6_vty) {
          lines.push("ipv6 access-list VTY_ACL");
          lines.push(" permit tcp " + (d.ssh.vty_acl_ipv6 || "2001:db8::/32") + " any eq 22");
          lines.push(" exit");
        }
        lines.push("line vty 0 15"); lines.push(" login local"); lines.push(" transport input ssh");
        if (d.ssh.ipv6_vty) lines.push(" ipv6 access-class VTY_ACL in");
        lines.push(" exit");
      }
      output.push(lines.join("\n"));
    }
    output.push("");
    output.push("! ========================================");
    output.push("! Topology Summary");
    output.push("! Devices: " + devices.filter(function(d) { return d && d.hostname; }).length);
    output.push("! ========================================");
    return output.join("\n\n");
  }

  window.addEventListener("DOMContentLoaded", boot);
})();
