(function () {
  const TOOLS = {
    "vlan-weaver": {
      title: "VLAN Weaver",
      template: `# VLAN Weaver: Layer 2 Segmentation
- hostname: DSW-1
  vlans:
    - name: Management
      id: 10
    - name: Sales
    - name: Guest
`,
      generate: genVlanWeaver
    },
    "ospf-pathmaker": {
      title: "OSPF Pathmaker",
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
      template: `# DHCP Allocator: IPv4 Pools
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
      template: `# IP Architect: Interfaces + Random
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
      template: `# NAT Portal: Mapping
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
    }
  };

  function boot() {
    const params = new URLSearchParams(window.location.search);
    const slug = params.get("tool");
    const tool = TOOLS[slug];
    if (!tool) {
      document.getElementById("tool-title").textContent = "Unknown tool";
      return;
    }
    document.title = `${tool.title} - Keystone`;
    document.getElementById("tool-title").textContent = tool.title;
    const input = document.getElementById("input");
    const output = document.getElementById("output");
    input.value = tool.template;

    document.getElementById("run").addEventListener("click", () => {
      try {
        const data = parseInput(input.value);
        output.value = tool.generate(data);
      } catch (e) {
        output.value = `Error: ${e.message}`;
      }
    });
    document.getElementById("reset").addEventListener("click", () => {
      input.value = tool.template;
      output.value = "";
    });
    document.getElementById("copy").addEventListener("click", async () => {
      await navigator.clipboard.writeText(output.value || "");
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
      lines.push("line vty 0 15", " login local", " transport input ssh", " exit");
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
            ? ({ A: "fc00::/32", B: "fc00:0:100::/40", C: "fc00:0:200::/48" }[cls])
            : ({ A: "10.0.0.0/8", B: "172.16.0.0/12", C: "192.168.0.0/16" }[cls]);
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

  window.addEventListener("DOMContentLoaded", boot);
})();
