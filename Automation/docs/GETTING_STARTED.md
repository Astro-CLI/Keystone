# 🚀 Getting Started with Keystone

**Extract. Parse. Modify. Rebuild.** Learn the complete workflow in 15 minutes.

---

## 🎯 What You're Solving

> "I have a complex topology in Packet Tracer with OSPF, DHCP, NAT, etc. I want to extract it, modify the IPs and hostnames, then rebuild it programmatically."

**Keystone makes this possible in 5 steps.**

---

## ⚡ The 5-Minute Quick Start

If you want to jump right in:

```bash
# 1. In Packet Tracer: Extensions → Scripting → Edit File Script Module
#    Paste: scripts/pt_analyzer.js
#    Click Run → Copy output to configs.txt

# 2. Parse to YAML
python3 scripts/pt_config_parser.py configs.txt --yaml

# 3. Edit the generated YAML
nano configs_topology.yaml

# 4. Generate new configs
python3 tools/topology_composer.py --file configs_topology.yaml

# 5. Deploy to PT
#    (Run main.js via Extensions → Scripting)
```

**That's it!** Your topology is recreated with new settings.

---

## 📖 The Complete Workflow (15 Minutes)

### Step 1️⃣: Extract Your Topology (3 minutes)

**In Packet Tracer:**

1. Open any `.pkt` topology
2. Go to **Extensions → Scripting → Edit File Script Module**
3. Clear everything and paste `scripts/pt_analyzer.js`
4. Click **Run**
5. Wait for the output (shows all devices + configs)

**You'll see:**
```
╔════════════════════════════════════════════════════════╗
║         KEYSTONE - PT TOPOLOGY ANALYZER v1.0          ║
╚════════════════════════════════════════════════════════╝

═══ TOPOLOGY SUMMARY ═══
Total devices: 3

[1] Router1 (Model: 2911)
[2] Router2 (Model: 2911)
[3] Switch1 (Model: 2960)

═══ EXTRACTED CONFIGURATIONS ═══
[All running configs displayed]
```

### Step 2️⃣: Copy Output (1 minute)

1. **Select all** (Ctrl+A)
2. **Copy** (Ctrl+C)
3. Create file: `configs.txt`
4. **Paste** everything
5. Save

### Step 3️⃣: Parse to YAML (2 minutes)

```bash
cd Automation

# Parse extracted configs to YAML
python3 scripts/pt_config_parser.py configs.txt --yaml

# Output: configs_topology.yaml
```

**Result:** A structured, human-editable YAML file with all your devices, interfaces, IPs, and configs.

### Step 4️⃣: Edit the YAML (5 minutes)

```yaml
# configs_topology.yaml
devices:
  - hostname: Router1           # ← Edit this
    type: router
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.1.1            # ← Edit this
        mask: 255.255.255.0
        description: "Link to Router2"
    
  - hostname: Router2           # ← Or edit this
    type: router
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.1.2            # ← Change any IP
        mask: 255.255.255.0
```

**Common edits:**
- Change hostnames: `hostname: NewName`
- Change IPs: `ip: 10.0.2.1`
- Change subnets: `mask: 255.255.255.0`
- Change OSPF router IDs, BGP ASNs, DHCP pools, etc.

### Step 5️⃣: Rebuild Topology (4 minutes)

Generate CLI commands from your modified YAML:

```bash
python3 tools/topology_composer.py \
  --file configs_topology.yaml \
  --output commands.txt
```

**Output:** A file with all CLI commands ready to inject.

Then deploy with `main.js` in Packet Tracer or use programmatically with the PT APIs.

---

## 📂 Key Files & When to Use Them

| File | Purpose | When to Use |
|------|---------|-----------|
| `scripts/pt_analyzer.js` | Extract configs from PT | Start here (Step 1) |
| `scripts/pt_config_parser.py` | Parse to YAML/JSON/XML | Parse extracted output (Step 3) |
| `tools/topology_composer.py` | Generate CLI from YAML | Rebuild topology (Step 5) |
| `tools/yaml_to_mainjs.py` | YAML → runnable main.js | Advanced deployment |
| `generators/ospf_pathmaker.py` | Generate OSPF configs | When building complex OSPF topologies |
| `generators/bgp_conductor.py` | Generate BGP configs | When building complex BGP topologies |
| `main.js` | Deploy to PT | Inject configs into live topology |

---

## 🎯 Common Use Cases

### Use Case 1: Extract & Modify a Topology
```bash
# Step 1: Extract from PT (use pt_analyzer.js)
# Step 2: Parse to YAML (use pt_config_parser.py)
# Step 3: Edit YAML (change IPs, hostnames, etc.)
# Step 4: Rebuild with topology_composer.py
```

### Use Case 2: Share a Topology Design
```bash
# You:  Extract → YAML → Send YAML file
# They: Modify YAML → Rebuild → Deploy
```

### Use Case 3: Create Multiple Labs from One Template
```bash
# Template: examples/simple_topology.yaml
# Edit → Save as lab1.yaml
# Edit → Save as lab2.yaml
# Edit → Save as lab3.yaml
# Rebuild each one
```

### Use Case 4: Export a Live Topology as Copyable YAML
```bash
# Use pt_yaml_exporter.js (runs in PT)
# Outputs YAML syntax directly in debug console
# Copy and save
```

---

## 🔧 What You Can Extract & Modify

### ✅ Fully Supported (Extract & Modify)
- **Hostnames** — Device names
- **Interface configs** — IP addresses, subnet masks, descriptions, shutdown state
- **OSPF** — Process ID, router ID, networks, areas, authentication
- **BGP** — ASN, router ID, neighbors, networks
- **EIGRP** — Process ID, networks, AS number
- **DHCP** — Pools, excluded addresses, default gateway, DNS
- **NAT** — Inside/outside interfaces, translations, ACLs
- **HSRP** — Virtual IP, priority, group
- **SSH** — Version, key exchange, ciphers
- **VLAN** — VLAN IDs, descriptions, IP addresses

### 🔶 Partially Supported
- **Static routes** — Destinations, masks, next hops
- **ACLs** — Standard and extended ACLs

### ❌ Not Yet Supported
- QoS policies (advanced)
- BGP policy routes (complex)
- MPLS (not tested)

See **[docs/PT_SCRIPTING_API.md](../docs/PT_SCRIPTING_API.md)** for detailed API capabilities.

---

## 📁 Directory Layout

```
Automation/
├── README.md                      ← Main overview
├── docs/
│   ├── GETTING_STARTED.md         ← You are here
│   ├── ARCHITECTURE.md            ← How it works
│   ├── PT_SCRIPTING_API.md        ← API deep reference
│   ├── WORKFLOWS.md               ← Advanced patterns
│   ├── GENERATORS_GUIDE.md        ← All 12 generators
│   ├── INTEGRATION.md             ← Integration options
│   ├── TROUBLESHOOTING.md         ← Common issues
│   └── FORMAT_SUPPORT.md          ← Format comparisons
├── scripts/                       ← Analysis scripts
│   ├── pt_analyzer.js             ← Extract topology
│   ├── pt_yaml_exporter.js        ← Export as YAML
│   ├── pt_api_explorer.js         ← Discover APIs
│   ├── pt_config_parser.py        ← Parse configs
│   └── README.md                  ← Scripts overview
├── tools/                         ← Core tools
│   ├── topology_composer.py       ← YAML → commands
│   ├── yaml_to_mainjs.py          ← YAML → main.js
│   ├── pt_file_builder.py         ← Create .pkt files
│   ├── format_parser.py           ← Multi-format support
│   └── README.md                  ← Tools overview
├── generators/                    ← 12 protocol generators
│   ├── ospf_pathmaker.py
│   ├── bgp_conductor.py
│   ├── [10 more...]
│   └── README.md
├── examples/                      ← Sample topologies
├── output/                        ← Generated files
└── main.js                        ← PT deployment script
```

---

## 🚨 Troubleshooting

### Problem: "pt_analyzer.js won't run"
**Solution:** Check that Extensions → Scripting is available in your PT version (6.2+)

### Problem: "pt_config_parser.py gives errors"
**Solution:** Ensure Python 3.7+, and run from the `Automation/` directory

### Problem: "topology_composer.py says 'Invalid YAML'"
**Solution:** Check YAML formatting (indentation, colons, quotes). See `examples/`

See **[docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)** for more issues.

---

## 🎓 Next Steps

### To Learn More
- **Architecture:** [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) — Understand the data flow
- **All Workflows:** [docs/WORKFLOWS.md](../docs/WORKFLOWS.md) — Advanced use patterns
- **Generators:** [docs/GENERATORS_GUIDE.md](../docs/GENERATORS_GUIDE.md) — Protocol-specific guides
- **API Reference:** [docs/PT_SCRIPTING_API.md](../docs/PT_SCRIPTING_API.md) — Deep dive into PT APIs

### To Get Hands-On
1. Try `examples/simple_topology.yaml` — the easiest template
2. Run `python3 tools/pt_file_builder_tests.py` — verify your setup
3. Extract your first real topology and modify it

### To Integrate Into Your Project
- See **[docs/INTEGRATION.md](../docs/INTEGRATION.md)** for integration patterns
- Embed tools into CI/CD pipelines
- Programmatically generate topologies

---

## 💡 Pro Tips

- **YAML is smaller:** Use YAML format (40% smaller than JSON)
- **Auto-detection:** All tools automatically detect YAML/JSON/XML
- **Keep it organized:** Use `output/` folder for generated files
- **Test first:** Run tests with `python3 tools/pt_file_builder_tests.py`
- **Start simple:** Use `examples/simple_topology.yaml` as a template
- **Version control:** Track YAML files in git, not generated CLI

---

## 🆘 Need Help?

- **Stuck?** → [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
- **Want more details?** → [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
- **Advanced usage?** → [docs/WORKFLOWS.md](../docs/WORKFLOWS.md)
- **API details?** → [docs/PT_SCRIPTING_API.md](../docs/PT_SCRIPTING_API.md)

---

**Ready? Extract your first topology:** Run `pt_analyzer.js` in Packet Tracer now! 🚀
