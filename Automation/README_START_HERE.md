# 🎯 Keystone Automation - START HERE

## Welcome! 👋

This is the **Keystone Network Automation Suite** for Packet Tracer. It's now organized and ready to use.

---

## ⚡ 5-Second Overview

You can now:
1. **Extract** running configs from any Packet Tracer topology
2. **Parse** those configs to human-readable YAML
3. **Modify** them (change IPs, hostnames, VLANs, etc.)
4. **Rebuild** the topology automatically with new settings
5. **Deploy** everything back to Packet Tracer

---

## 📂 Directory Structure

```
Automation/
├── scripts/        ← Quick analysis tools
├── docs/           ← Documentation (START HERE!)
├── tools/          ← Core utilities
├── generators/     ← 12 protocol generators
├── examples/       ← Sample topologies
├── output/         ← Generated files
├── templates/      ← (reserved)
├── reference/      ← Research & debug files
├── main.js         ← PT entry point
└── DIRECTORY_STRUCTURE.md ← Full guide
```

**For detailed explanation:** See `DIRECTORY_STRUCTURE.md`

---

## 🚀 Quick Start (Choose One)

### Option A: New User? (5 minutes)
1. Read: `docs/PT_ANALYZER_INDEX.md`
2. Then: `docs/PT_ANALYZER_QUICKSTART.md`
3. Done! You'll understand the whole system

### Option B: Impatient? (2 minutes)
1. Open any Packet Tracer topology
2. Extensions → Scripting → Edit File Script Module
3. Paste: `scripts/pt_analyzer.js`
4. Click Run
5. Copy output to `configs.txt`
6. Run: `python3 scripts/pt_config_parser.py configs.txt --yaml`
7. Edit the generated YAML
8. Run: `python3 tools/topology_composer.py --file my_topology.yaml`
9. Deploy with `main.js`

### Option C: Visual Learner? (10 minutes)
1. View: `STRUCTURE_VISUAL.txt`
2. View: `docs/ANALYZER_ARCHITECTURE.txt`
3. Read: `docs/PT_ANALYZER_README.md`

---

## 📚 Documentation Map

| I want to... | Read this |
|--------------|-----------|
| **Get started** | `docs/PT_ANALYZER_INDEX.md` |
| **5-minute quickstart** | `docs/PT_ANALYZER_QUICKSTART.md` |
| **Complete reference** | `docs/PT_ANALYZER_README.md` |
| **PT API reference** | `docs/PT_API_DEEP_REFERENCE.md` |
| **Understand architecture** | `docs/ANALYZER_ARCHITECTURE.txt` |
| **See visuals** | `STRUCTURE_VISUAL.txt` |
| **Troubleshoot** | `docs/TROUBLESHOOTING_GUIDE.md` |
| **Compare formats** | `docs/FORMAT_COMPARISON.md` |
| **API reference** | `docs/API_QUICK_REFERENCE.md` |
| **Directory guide** | `DIRECTORY_STRUCTURE.md` |

---

## 🎯 Common Tasks

### Extract a Topology
```bash
# 1. In Packet Tracer:
Extensions > Scripting > Edit File Script Module
→ Paste scripts/pt_analyzer.js
→ Click Run
→ Copy output to configs.txt

# 2. On computer:
python3 scripts/pt_config_parser.py configs.txt --yaml
```

### Modify a Topology
```bash
# Edit the generated YAML file
# Change hostnames, IPs, OSPF IDs, VLANs, etc.
nano my_topology.yaml
```

### Rebuild & Deploy
```bash
# Generate CLI commands
python3 tools/topology_composer.py --file my_topology.yaml

# Deploy to PT via main.js
Extensions > Scripting > Edit File Script Module
→ Paste main.js (with new commands embedded)
→ Click Run
```

### Generate OSPF Configs
```bash
python3 generators/ospf_pathmaker.py --topology examples/simple_topology.yaml
```

---

## 🎓 Learning Path

### Beginner (30 minutes)
1. `docs/PT_ANALYZER_INDEX.md` — Navigation
2. `docs/PT_ANALYZER_QUICKSTART.md` — Quick start
3. Try extracting your first topology
4. Look at `examples/` to see sample format

### Intermediate (1-2 hours)
1. `docs/PT_ANALYZER_README.md` — Complete guide
2. `docs/ANALYZER_ARCHITECTURE.txt` — Architecture
3. Experiment with modifying example topologies
4. Try different generators in `generators/`

### Advanced (2-3 hours)
1. `docs/OPTION_C_COMPLETE_DOCUMENTATION.md` — Full API
2. `docs/API_QUICK_REFERENCE.md` — Quick reference
3. `docs/PT_API_DEEP_REFERENCE.md` — Detailed object/function catalog
4. Explore tools and modify scripts
5. Build custom workflows

---

## 📦 What's Included

### Scripts (in `scripts/`)
- `pt_analyzer.js` — Extract configs from PT
- `pt_config_parser.py` — Parse to YAML/JSON

### Tools (in `tools/`)
- `topology_composer.py` — Generate CLI from YAML
- `format_parser.py` — Multi-format support
- `pt_file_builder.py` — .pkt file generation

### Generators (in `generators/`)
12 protocol-specific generators:
- OSPF, BGP, EIGRP, Static routing
- NAT, DHCP, HSRP, VLAN, SSH
- ASA firewall, IP addressing, CIDR

### Examples (in `examples/`)
Sample topologies in 3 formats each:
- YAML (recommended)
- JSON
- XML

---

## ✨ Key Features

✅ **Extract** — Read running configs from PT via scripting API
✅ **Parse** — Convert Cisco configs to editable YAML
✅ **Modify** — Change anything: hostnames, IPs, protocols, VLANs
✅ **Generate** — Create CLI commands automatically
✅ **Deploy** — Inject configs back into PT instantly
✅ **Repeat** — Cycle infinitely: extract → modify → rebuild

---

## 🔗 File Quick Reference

| I need... | Location |
|-----------|----------|
| Entry point for PT | `main.js` |
| Extract configs | `scripts/pt_analyzer.js` |
| Parse configs | `scripts/pt_config_parser.py` |
| Generate commands | `tools/topology_composer.py` |
| OSPF generator | `generators/ospf_pathmaker.py` |
| BGP generator | `generators/bgp_conductor.py` |
| Sample topology | `examples/simple_topology.yaml` |
| Complete docs | `docs/PT_ANALYZER_README.md` |
| Quick start | `docs/PT_ANALYZER_QUICKSTART.md` |
| Troubleshooting | `docs/TROUBLESHOOTING_GUIDE.md` |

---

## 🆘 Having Issues?

1. **First check:** `docs/TROUBLESHOOTING_GUIDE.md`
2. **Need architecture help:** `docs/ANALYZER_ARCHITECTURE.txt`
3. **API questions:** `docs/API_QUICK_REFERENCE.md`
4. **Format issues:** `docs/FORMAT_COMPARISON.md`

---

## 💡 Pro Tips

- Start with `examples/simple_topology.yaml` — it's the easiest
- Keep generated `.pkt` files in `output/` — easy to clean up
- Use YAML format — it's 40% smaller than JSON/XML
- Check generator docs in `generators/*.md` for details
- All tools support multi-format (YAML/JSON/XML automatically)

---

## 🎉 Ready?

**Pick your starting point:**

- 👶 **Beginner** → `docs/PT_ANALYZER_QUICKSTART.md` (5 min)
- 🤔 **Visual** → `STRUCTURE_VISUAL.txt` (10 min)
- 📖 **Reference** → `docs/PT_ANALYZER_README.md` (30 min)
- 🏗️ **Architecture** → `docs/ANALYZER_ARCHITECTURE.txt` (20 min)

---

**Welcome to Keystone! Let's automate some networks.** 🚀
