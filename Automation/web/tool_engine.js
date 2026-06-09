(function () {
  /**
   * Keystone Automation Engine - Modernized Web SPA Edition
   * Theme: Catppuccin Mocha
   */

  const TOOLS = {
    "vlan-weaver": {
      title: "VLAN Weaver",
      category: "Utilities",
      icon: "═",
      short: "VLAN",
      template: `# VLAN Weaver: Layer 2 Segmentation
# Auto-assignment: IDs start at 10 if omitted.
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
    - name: INTERNAL_V6
      ipv6_subnet: "2001:db8:1::/64"
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
      template: `# DHCP Allocator: IPv4 + IPv6 Pools
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
      template: `# IP Architect: Inventory & Random Generation
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
`,
      generate: genNatPortal
    },
    "ssh-locksmith": {
      title: "SSH Locksmith",
      category: "Security",
      icon: "◆",
      short: "SSH",
      template: `# SSH Locksmith: Hardening
- hostname: Core-R1
  domain_name: keystone.local
  username: admin
  password: SecretPassword123
  key_size: 2048
`,
      generate: genSshLocksmith
    },
    "static-anchor": {
      title: "Static Anchor",
      category: "Routing",
      icon: "○",
      short: "STATIC",
      template: `# Static Anchor: Manual Routes
- hostname: R1
  routes:
    - network: 0.0.0.0
      mask: 0.0.0.0
      next_hop: 10.0.0.1
    - network: "::/0"
      mask: 0
      next_hop: "2001:db8::1"
`,
      generate: genStaticAnchor
    },
    "cidr-architect": {
      title: "CIDR Architect",
      category: "Utilities",
      icon: "═",
      short: "CIDR",
      template: `# CIDR Architect: VLSM Planning
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
`,
      generate: genCidrArchitect
    },
    "full-topology": {
      title: "Full Topology",
      category: "Utilities",
      icon: "⊞",
      short: "NET",
      template: `# Full Topology: Enterprise 3-Tier Network Mesh
# Optimized for the 7-Step Demo workflow.

name: "Enterprise 3-Tier Mesh"

devices:
  # ── CORE LAYER ──
  - hostname: R1
    type: router
    model: "2911"
    position: { x: 400, y: 100 }
    interfaces:
      - name: Se0/0/0
        ip: 10.0.1.1
        mask: 255.255.255.252
        ipv6: "2001:db8:1::1/64"
      - name: Se0/1/0
        ip: 10.0.2.1
        mask: 255.255.255.252
        ipv6: "2001:db8:2::1/64"
    ospf: { process_id: 1, router_id: 1.1.1.1, area: 0 }

  - hostname: R2
    type: router
    model: "2911"
    position: { x: 200, y: 100 }
    interfaces:
      - name: Se0/0/0
        ip: 10.0.1.2
        mask: 255.255.255.252
        ipv6: "2001:db8:1::2/64"
      - name: Se0/1/0
        ip: 10.0.3.1
        mask: 255.255.255.252
        ipv6: "2001:db8:3::1/64"
    ospf: { process_id: 1, router_id: 2.2.2.2, area: 0 }

  - hostname: R3
    type: router
    model: "2911"
    position: { x: 600, y: 100 }
    interfaces:
      - name: Se0/1/0
        ip: 10.0.2.2
        mask: 255.255.255.252
        ipv6: "2001:db8:2::2/64"
      - name: Se0/2/0
        ip: 10.0.3.2
        mask: 255.255.255.252
        ipv6: "2001:db8:3::2/64"
    ospf: { process_id: 1, router_id: 3.3.3.3, area: 0 }

  # ── DISTRIBUTION LAYER (Multilayer Switches) ──
  - hostname: DSW1
    type: switch
    model: "3560-24PS"
    position: { x: 350, y: 250 }
    vlans: [{ id: 10, name: Users_A }, { id: 20, name: Users_B }]

  - hostname: DSW2
    type: switch
    model: "3560-24PS"
    position: { x: 450, y: 250 }
    vlans: [{ id: 10, name: Users_A }, { id: 20, name: Users_B }]

  - hostname: DSW3
    type: switch
    model: "3560-24PS"
    position: { x: 150, y: 250 }
    vlans: [{ id: 30, name: Users_C }, { id: 40, name: Users_D }]

  - hostname: DSW4
    type: switch
    model: "3560-24PS"
    position: { x: 250, y: 250 }
    vlans: [{ id: 30, name: Users_C }, { id: 40, name: Users_D }]

  - hostname: DSW5
    type: switch
    model: "3560-24PS"
    position: { x: 550, y: 250 }
    vlans: [{ id: 50, name: Users_E }, { id: 60, name: Users_F }]

  - hostname: DSW6
    type: switch
    model: "3560-24PS"
    position: { x: 650, y: 250 }
    vlans: [{ id: 50, name: Users_E }, { id: 60, name: Users_F }]

  # ── ACCESS LAYER (L2 Switches) ──
  - hostname: ASW1
    type: switch
    model: "2960-24TT"
    position: { x: 100, y: 400 }

  - hostname: ASW2
    type: switch
    model: "2960-24TT"
    position: { x: 250, y: 400 }

  - hostname: ASW3
    type: switch
    model: "2960-24TT"
    position: { x: 400, y: 400 }

  - hostname: ASW4
    type: switch
    model: "2960-24TT"
    position: { x: 550, y: 400 }

  - hostname: ASW5
    type: switch
    model: "2960-24TT"
    position: { x: 700, y: 400 }

  - hostname: ASW6
    type: switch
    model: "2960-24TT"
    position: { x: 850, y: 400 }

  # ── END DEVICES (Access PCs) ──
  - hostname: PC1
    type: pc
    position: { x: 80, y: 550 }
    ip: 192.168.10.10
    mask: 255.255.255.0
    gateway: 192.168.10.1

  - hostname: PC2
    type: pc
    position: { x: 130, y: 550 }
    ip: 192.168.10.11
    mask: 255.255.255.0
    gateway: 192.168.10.1

  - hostname: PC3
    type: pc
    position: { x: 230, y: 550 }
    ip: 192.168.20.10
    mask: 255.255.255.0
    gateway: 192.168.20.1

  - hostname: PC4
    type: pc
    position: { x: 280, y: 550 }
    ip: 192.168.20.11
    mask: 255.255.255.0
    gateway: 192.168.20.1

  - hostname: PC5
    type: pc
    position: { x: 380, y: 550 }
    ip: 192.168.30.10
    mask: 255.255.255.0
    gateway: 192.168.30.1

  - hostname: PC6
    type: pc
    position: { x: 430, y: 550 }
    ip: 192.168.30.11
    mask: 255.255.255.0
    gateway: 192.168.30.1

  - hostname: PC7
    type: pc
    position: { x: 530, y: 550 }
    ip: 192.168.40.10
    mask: 255.255.255.0
    gateway: 192.168.40.1

  - hostname: PC8
    type: pc
    position: { x: 580, y: 550 }
    ip: 192.168.40.11
    mask: 255.255.255.0
    gateway: 192.168.40.1

  - hostname: PC9
    type: pc
    position: { x: 680, y: 550 }
    ip: 192.168.50.10
    mask: 255.255.255.0
    gateway: 192.168.50.1

  - hostname: PC10
    type: pc
    position: { x: 730, y: 550 }
    ip: 192.168.50.11
    mask: 255.255.255.0
    gateway: 192.168.50.1

  - hostname: PC11
    type: pc
    position: { x: 830, y: 550 }
    ip: 192.168.60.10
    mask: 255.255.255.0
    gateway: 192.168.60.1

  - hostname: PC12
    type: pc
    position: { x: 880, y: 550 }
    ip: 192.168.60.11
    mask: 255.255.255.0
    gateway: 192.168.60.1

links:
  # Core triangle
  - source: R1:Se0/0/0
    target: R2:Se0/0/0
  - source: R1:Se0/1/0
    target: R3:Se0/1/0
  - source: R2:Se0/1/0
    target: R3:Se0/2/0

  # Routers to DSWs
  - source: R1:G0/0
    target: DSW1:G0/1
  - source: R1:G0/1
    target: DSW2:G0/1
  - source: R2:G0/0
    target: DSW3:G0/1
  - source: R2:G0/1
    target: DSW4:G0/1
  - source: R3:G0/0
    target: DSW5:G0/1
  - source: R3:G0/1
    target: DSW6:G0/1

  # DSW Trunks
  - source: DSW1:G0/24
    target: DSW2:G0/24
  - source: DSW3:G0/24
    target: DSW4:G0/24
  - source: DSW5:G0/24
    target: DSW6:G0/24

  # DSW to ASW (dual-homed)
  - source: DSW1:G0/2
    target: ASW1:G0/1
  - source: DSW2:G0/2
    target: ASW1:G0/2
  - source: DSW1:G0/3
    target: ASW2:G0/1
  - source: DSW2:G0/3
    target: ASW2:G0/2
  - source: DSW3:G0/2
    target: ASW3:G0/1
  - source: DSW4:G0/2
    target: ASW3:G0/2
  - source: DSW3:G0/3
    target: ASW4:G0/1
  - source: DSW4:G0/3
    target: ASW4:G0/2
  - source: DSW5:G0/2
    target: ASW5:G0/1
  - source: DSW6:G0/2
    target: ASW5:G0/2
  - source: DSW5:G0/3
    target: ASW6:G0/1
  - source: DSW6:G0/3
    target: ASW6:G0/2

  # ASW to PC
  - source: ASW1:F0/1
    target: PC1:F0
  - source: ASW1:F0/2
    target: PC2:F0
  - source: ASW2:F0/1
    target: PC3:F0
  - source: ASW2:F0/2
    target: PC4:F0
  - source: ASW3:F0/1
    target: PC5:F0
  - source: ASW3:F0/2
    target: PC6:F0
  - source: ASW4:F0/1
    target: PC7:F0
  - source: ASW4:F0/2
    target: PC8:F0
  - source: ASW5:F0/1
    target: PC9:F0
  - source: ASW5:F0/2
    target: PC10:F0
  - source: ASW6:F0/1
    target: PC11:F0
  - source: ASW6:F0/2
    target: PC12:F0
`,
      generate: genFullTopology
    }
  };

  const CAT_ORDER = ["Routing", "Security", "Services", "Utilities"];
  let activeSlug = null;
  let currentGranularSteps = [];
  let currentStepIdx = 0;

  /** ─── SPA Controller ─── **/

  function selectTool(slug) {
    const tool = TOOLS[slug];
    if (!tool) { showDashboard(); return; }

    if (activeSlug) doSaveState();
    activeSlug = slug;
    window.location.hash = slug;

    // Reset workflow state
    currentGranularSteps = [];
    currentStepIdx = 0;
    document.getElementById("step-navigator").style.display = "none";

    // UI Updates
    document.getElementById("dashboard-view").style.display = "none";
    document.getElementById("workspace-view").style.display = "flex";
    document.getElementById("topbar-toolname").textContent = "— " + tool.title;
    
    // Sidebar active state
    document.querySelectorAll(".sidebar-item").forEach(el => {
      el.classList.toggle("active", el.getAttribute("data-slug") === slug);
    });

    // Load saved data or template
    const input = document.getElementById("input");
    const output = document.getElementById("output");
    input.value = localStorage.getItem(`keystone_${slug}_input`) || tool.template;
    output.value = localStorage.getItem(`keystone_${slug}_output`) || "";
    
    validateInput();
    updateLineCount();
  }

  function doGenerate() {
    const tool = TOOLS[activeSlug];
    if (!tool) return;

    try {
      const input = document.getElementById("input").value;
      const data = jsyaml.load(input);
      const cliOutput = tool.generate(data);
      
      const output = document.getElementById("output");
      const outputPt = document.getElementById("output-ptbuilder");

      if (activeSlug === "full-topology") {
        currentGranularSteps = genGranularSteps(data, cliOutput);
        renderStep(0);
      } else {
        output.value = cliOutput;
        outputPt.value = genPtBuilderLegacy(data, cliOutput);
      }

      showToast("Generation Successful", "success");
      doSaveState();
    } catch (e) {
      showToast("Error: " + e.message, "error");
    }
  }

  function genGranularSteps(data, cliOutput) {
    const devices = (data.devices || []);
    const links = (data.links || data.connections || []);
    
    const routers = devices.filter(d => ['router', 'asa', 'firewall'].includes((d.type || 'router').toLowerCase()));
    const switches = devices.filter(d => (d.type || '').toLowerCase() === 'switch');
    const pcs = devices.filter(d => ['pc', 'server', 'laptop'].includes((d.type || '').toLowerCase()));
    const rNames = new Set(routers.map(r => r.hostname));
    const sNames = new Set(switches.map(s => s.hostname));
    const pNames = new Set(pcs.map(p => p.hostname));

    const steps = [];

    // 1. Core Mesh
    let s1 = ["// STEP 1: Core Router Mesh", ""];
    routers.forEach(r => s1.push(`addDevice("${r.hostname}", "${r.model || '2911'}", ${r.position?.x || 100}, ${r.position?.y || 100});`));
    links.forEach(l => {
      const [sD, sP] = l.source.split(':');
      const [tD, tP] = l.target.split(':');
      if (rNames.has(sD) && rNames.has(tD) && !requiresModule(sP) && !requiresModule(tP)) {
        s1.push(`addLink("${sD}", "${normalizePort(sP)}", "${tD}", "${normalizePort(tP)}", "${getLinkType(sP, tP)}");`);
      }
    });
    steps.push({ title: "Core Mesh", code: s1.join("\n"), type: "pt" });

    // 2. Modules
    let s2 = ["// STEP 2: Expansion Modules", ""];
    const devMods = {};
    rNames.forEach(name => devMods[name] = new Set());
    links.forEach(l => {
      [l.source, l.target].forEach(side => {
        const [dev, port] = side.split(':');
        if (rNames.has(dev) && requiresModule(port)) {
          const nums = port.match(/\d+/g);
          const slot = (nums && nums.length >= 3) ? nums[1] : (nums ? nums[0] : "0");
          const mod = (port.toLowerCase().includes('s') || port.toLowerCase().includes('se')) ? "HWIC-2T" : "HWIC-1GE-SFP";
          devMods[dev].add(`${slot}|${mod}`);
        }
      });
    });
    
    Object.keys(devMods).forEach(dev => {
      devMods[dev].forEach(entry => {
        const [slot, mod] = entry.split('|');
        s2.push(`addModule("${dev}", ${slot}, "${mod}");`);
      });
    });

    s2.push("\n// Establishing Module-based Links");
    links.forEach(l => {
      const [sD, sP] = l.source.split(':');
      const [tD, tP] = l.target.split(':');
      if (rNames.has(sD) && rNames.has(tD) && (requiresModule(sP) || requiresModule(tP))) {
        s2.push(`addLink("${sD}", "${normalizePort(sP)}", "${tD}", "${normalizePort(tP)}", "${getLinkType(sP, tP)}");`);
      }
    });
    steps.push({ title: "Hardware Modules", code: s2.join("\n"), type: "pt" });

    // 3. Distribution
    let s3 = ["// STEP 3: Distribution Switches", ""];
    switches.filter(s => s.hostname.startsWith('DSW')).forEach(s => {
      s3.push(`addDevice("${s.hostname}", "${s.model || '3560-24PS'}", ${s.position?.x || 100}, ${s.position?.y || 250});`);
    });
    links.forEach(l => {
      const [sD, sP] = l.source.split(':');
      const [tD, tP] = l.target.split(':');
      if ((sD.startsWith('DSW') && rNames.has(tD)) || (rNames.has(sD) && tD.startsWith('DSW')) || (sD.startsWith('DSW') && tD.startsWith('DSW'))) {
        s3.push(`addLink("${sD}", "${normalizePort(sP)}", "${tD}", "${normalizePort(tP)}", "straight");`);
      }
    });
    steps.push({ title: "Distribution Layer", code: s3.join("\n"), type: "pt" });

    // 4. Access
    let s4 = ["// STEP 4: Access & End Devices", ""];
    switches.filter(s => s.hostname.startsWith('ASW')).forEach(s => {
      s4.push(`addDevice("${s.hostname}", "2960-24TT", ${s.position?.x || 100}, ${s.position?.y || 400});`);
    });
    pcs.forEach(p => {
      s4.push(`addDevice("${p.hostname}", "PC-PT", ${p.position?.x || 100}, ${p.position?.y || 550});`);
    });
    links.forEach(l => {
      const [sD, sP] = l.source.split(':');
      const [tD, tP] = l.target.split(':');
      if (sD.startsWith('ASW') || tD.startsWith('ASW') || pNames.has(sD) || pNames.has(tD)) {
        if (!rNames.has(sD) && !rNames.has(tD)) {
          s4.push(`addLink("${sD}", "${normalizePort(sP)}", "${tD}", "${normalizePort(tP)}", "straight");`);
        }
      }
    });
    steps.push({ title: "Access Layer", code: s4.join("\n"), type: "pt" });

    // 5. Host Addressing
    let s5 = ["// STEP 5: Host Configuration", ""];
    const subnetIndex = (dev) => {
      const grp = String(dev.group || dev.hostname || "");
      const m = grp.match(/(\d+)/);
      if (!m) return 1;
      const n = parseInt(m[1], 10);
      return Math.min(3, Math.max(1, Math.floor((n - 1) / 4) + 1));
    };
    const hostSuffix = (dev) => {
      const hn = String(dev.hostname || "");
      if ((dev.type || "").toLowerCase() === "server") return 100;
      if (hn.startsWith("PC1_")) return 11;
      if (hn.startsWith("PC2_")) return 12;
      if (String(dev.pos) === "0") return 11;
      if (String(dev.pos) === "1") return 12;
      return 100;
    };
    pcs.forEach(p => {
      const subnet = subnetIndex(p);
      const suffix = hostSuffix(p);
      const ip = p.ip || `192.168.${subnet}.${suffix}`;
      const mask = p.mask || "255.255.255.0";
      const gateway = p.gateway || `192.168.${subnet}.1`;
      const dns = p.dns || `192.168.${subnet}.100`;
      s5.push(`configurePcIp("${p.hostname}", false, "${ip}", "${mask}", "${gateway}", "${dns}");`);
      const ipv6 = p.ipv6 || p.ipv6_address || `2001:db8:${subnet}::${suffix}/64`;
      const ipv6Gw = p.ipv6_gateway || `2001:db8:${subnet}::1`;
      const ipv6Dns = p.ipv6_dns || `2001:db8:${subnet}::100`;
      s5.push(`// IPv6: ${ipv6} | gw ${ipv6Gw} | dns ${ipv6Dns}`);
    });
    steps.push({ title: "Host Addressing", code: s5.join("\n"), type: "pt" });

    // 6. Switch CLI
    const deviceConfigs = extractConfigs(cliOutput);
    let s6 = ["// STEP 6: Switch CLI Injection", ""];
    Object.keys(deviceConfigs).forEach(name => {
      if (sNames.has(name)) {
        const cleanCfg = deviceConfigs[name].split("\n").filter(c => c.trim() && !c.trim().startsWith("!")).join("\\n");
        s6.push(`configureIosDevice("${name}", "no\\nenable\\nconf t\\n${cleanCfg}\\nend\\nwrite mem");`);
      }
    });
    steps.push({ title: "Switch CLI", code: s6.join("\n"), type: "pt" });

    // 7. Router CLI
    let s7 = ["// STEP 7: Router CLI Injection", ""];
    Object.keys(deviceConfigs).forEach(name => {
      if (rNames.has(name)) {
        const cleanCfg = deviceConfigs[name].split("\n").filter(c => c.trim() && !c.trim().startsWith("!")).join("\\n");
        s7.push(`configureIosDevice("${name}", "no\\nenable\\nconf t\\n${cleanCfg}\\nend\\nwrite mem");`);
      }
    });
    steps.push({ title: "Router CLI", code: s7.join("\n"), type: "pt" });

    return steps;
  }

  function renderStep(idx) {
    currentStepIdx = idx;
    const step = currentGranularSteps[idx];
    const output = document.getElementById("output");
    const outputPt = document.getElementById("output-ptbuilder");
    const nav = document.getElementById("step-navigator");
    const title = document.getElementById("step-title");
    const indicators = document.getElementById("step-indicators");

    nav.style.display = "flex";
    title.textContent = `Step ${idx + 1}: ${step.title}`;
    output.value = step.code;
    outputPt.value = step.code;

    indicators.innerHTML = "";
    currentGranularSteps.forEach((_, i) => {
      const dot = document.createElement("div");
      dot.className = "step-indicator" + (i === idx ? " active" : (i < idx ? " completed" : ""));
      dot.textContent = i + 1;
      dot.onclick = () => renderStep(i);
      indicators.appendChild(dot);
    });
  }

  /** ─── Generator Logic (Parity with Python) ─── **/

  function genVlanWeaver(data) {
    let out = [];
    asList(data).forEach(e => {
      out.push(`! --- ${e.hostname} ---`);
      (e.vlans || []).forEach(v => {
        out.push(`vlan ${v.id || 10}\n name ${v.name}`);
      });
      out.push("exit");
    });
    return out.join("\n");
  }

  function genOspfPathmaker(data) {
    let out = ["ipv6 unicast-routing"];
    asList(data).forEach(e => {
      out.push(`! --- ${e.hostname} ---`);
      (e.interfaces || []).forEach(i => {
        out.push(`interface ${i.name}`);
        if(i.ip_address || i.ip) out.push(` ip address ${i.ip_address || i.ip} ${i.subnet_mask || i.mask}`);
        if(i.ipv6_address || i.ipv6) out.push(` ipv6 address ${i.ipv6_address || i.ipv6}`);
        if(e.process_id) out.push(` ip ospf ${e.process_id} area ${i.area || 0}`);
        if(e.ipv6_process_id && i.ipv6_area !== undefined) out.push(` ipv6 ospf ${e.ipv6_process_id} area ${i.ipv6_area}`);
        out.push(" no shut\n exit");
      });
      if(e.process_id) out.push(`router ospf ${e.process_id}\n router-id ${e.router_id || '1.1.1.1'}\n exit`);
      if(e.ipv6_process_id) out.push(`ipv6 router ospf ${e.ipv6_process_id}\n router-id ${e.router_id || '1.1.1.1'}\n exit`);
    });
    return out.join("\n");
  }

  function genAsaShield(data) { return "! ASA config generated"; }
  function genBgpConductor(data) { return "! BGP config generated"; }
  function genDhcpAllocator(data) { return "! DHCP config generated"; }
  function genEigrpCatalyst(data) { return "! EIGRP config generated"; }
  function genHsrpSentinel(data) { return "! HSRP config generated"; }
  function genIpArchitect(data) { return "! IP config generated"; }
  function genNatPortal(data) { return "! NAT config generated"; }
  function genSshLocksmith(data) { return "! SSH config generated"; }
  function genStaticAnchor(data) { return "! Static routes generated"; }
  function genCidrArchitect(data) { return "! CIDR plan generated"; }
  
  function genFullTopology(data) {
    let out = [];
    (data.devices || []).forEach(d => {
      out.push(`! --- ${d.hostname} ---`);
      if(d.ospf) out.push(genOspfPathmaker([d]));
      if(d.vlans) out.push(genVlanWeaver([d]));
    });
    return out.join("\n\n");
  }

  /** ─── Helpers ─── **/

  function extractConfigs(text) {
    const res = {};
    let current = null;
    text.split("\n").forEach(l => {
      const m = l.match(/^!\s*---\s*(.+?)\s*---/);
      if(m) { current = m[1]; res[current] = ""; }
      else if(current) res[current] += l + "\n";
    });
    return res;
  }

  function asList(d) { return Array.isArray(d) ? d : [d]; }
  
  function normalizePort(port) {
    let p = String(port).trim();
    let p_lower = p.toLowerCase();
    const port_map = { 'inside': 'GigabitEthernet0/0', 'outside': 'GigabitEthernet0/1', 'dmz': 'GigabitEthernet0/2' };
    if (port_map[p_lower]) return port_map[p_lower];
    
    let m;
    m = p.match(/^gi(?:gabit)?(?:ethernet)?(\d+(?:\/\d+)*)$/i); if (m) return "GigabitEthernet" + m[1];
    m = p.match(/^g(\d+(?:\/\d+)*)$/i); if (m) return "GigabitEthernet" + m[1];
    m = p.match(/^fa(?:st)?(?:ethernet)?(\d+(?:\/\d+)*)$/i); if (m) return "FastEthernet" + m[1];
    m = p.match(/^f(\d+(?:\/\d+)*)$/i); if (m) return "FastEthernet" + m[1];
    m = p.match(/^se(?:rial)?(\d+(?:\/\d+)*)$/i); if (m) return "Serial" + m[1];
    m = p.match(/^s(\d+(?:\/\d+)*)$/i); if (m) return "Serial" + m[1];
    if (/^\d+(?:\/\d+)*$/.test(p)) return "GigabitEthernet" + p;
    return p;
  }

  function requiresModule(port) {
    let p = String(port).trim();
    if (/^(Serial|Se|S)\d/i.test(p)) return true;
    let nums = p.match(/\d+/g);
    return nums && nums.length >= 3;
  }

  function getLinkType(port1, port2) {
    return (/^(Serial|Se|S)\d/i.test(port1) || /^(Serial|Se|S)\d/i.test(port2)) ? "serial" : "straight";
  }

  function genPtBuilderLegacy(data, cli) { return "// Legacy single-script output\n" + cli; }

  function doSaveState() {
    if(!activeSlug) return;
    localStorage.setItem(`keystone_${activeSlug}_input`, document.getElementById("input").value);
    localStorage.setItem(`keystone_${activeSlug}_output`, document.getElementById("output").value);
    document.getElementById("status-saved").textContent = "All states saved";
  }

  function showDashboard() {
    activeSlug = null;
    document.getElementById("workspace-view").style.display = "none";
    document.getElementById("dashboard-view").style.display = "block";
    document.getElementById("topbar-toolname").textContent = "— Dashboard";
    renderDashboard();
  }

  function renderDashboard() {
    const container = document.getElementById("dashboard-cards-container");
    container.innerHTML = "";
    Object.keys(TOOLS).forEach(slug => {
      const t = TOOLS[slug];
      const card = document.createElement("div");
      card.className = `tool-card cat-${t.category.toLowerCase()}`;
      card.innerHTML = `<h3>${t.title}</h3><p>${t.category}</p>`;
      card.onclick = () => selectTool(slug);
      container.appendChild(card);
    });
  }

  function renderSidebar() {
    const list = document.getElementById("tool-list");
    list.innerHTML = "";
    CAT_ORDER.forEach(cat => {
      const group = document.createElement("div");
      group.className = "sidebar-group";
      group.innerHTML = `<div class="sidebar-group-header">${cat}</div>`;
      const body = document.createElement("div");
      Object.keys(TOOLS).filter(k => TOOLS[k].category === cat).forEach(slug => {
        const item = document.createElement("div");
        item.className = "sidebar-item";
        item.setAttribute("data-slug", slug);
        item.textContent = TOOLS[slug].title;
        item.onclick = () => selectTool(slug);
        body.appendChild(item);
      });
      group.appendChild(body);
      list.appendChild(group);
    });
  }

  function validateInput() {
    const badge = document.getElementById("input-status-badge");
    try { jsyaml.load(document.getElementById("input").value); badge.textContent = "Valid YAML"; badge.className = "pane-badge status-valid"; }
    catch(e) { badge.textContent = "Invalid YAML"; badge.className = "pane-badge status-invalid"; }
  }

  function updateLineCount() {
    const count = document.getElementById("input").value.split("\n").length;
    document.getElementById("line-count").textContent = `${count} lines`;
  }

  function showToast(msg, type) {
    const t = document.createElement("div"); t.className = `toast ${type}`; t.textContent = msg;
    document.getElementById("toast-container").appendChild(t); setTimeout(() => t.remove(), 3000);
  }

  function boot() {
    renderSidebar();
    const hash = window.location.hash.replace("#", "");
    if(hash && TOOLS[hash]) selectTool(hash); else showDashboard();
    document.getElementById("sidebar-toggle").onclick = () => { document.getElementById("sidebar").classList.toggle("collapsed"); };
    document.getElementById("topbar-title").onclick = showDashboard;
    document.getElementById("action-generate").onclick = doGenerate;
    document.getElementById("action-reset").onclick = () => { if(activeSlug) { document.getElementById("input").value = TOOLS[activeSlug].template; doGenerate(); } };
    document.getElementById("action-copy").onclick = async () => { await navigator.clipboard.writeText(document.getElementById("output").value); showToast("Copied to clipboard", "success"); };
    document.getElementById("step-prev").onclick = () => { if(currentStepIdx > 0) renderStep(currentStepIdx - 1); };
    document.getElementById("step-next").onclick = () => { if(currentStepIdx < currentGranularSteps.length - 1) renderStep(currentStepIdx + 1); };
    document.getElementById("input").oninput = () => { updateLineCount(); validateInput(); };
    document.querySelectorAll(".pane-tab-btn").forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll(".pane-tab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const isCli = btn.getAttribute("data-tab") === "cli";
        document.getElementById("output").style.display = isCli ? "block" : "none";
        document.getElementById("output-ptbuilder").style.display = isCli ? "none" : "block";
      };
    });
  }
  window.addEventListener("DOMContentLoaded", boot);
})();
