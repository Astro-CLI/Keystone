# ⚡ PT Analyzer - Quick Start (5 Minutes)

## The Problem You're Solving

> **"I have this awesome topology in Packet Tracer. How do I extract it, modify it, and rebuild it?"**

## The Solution (3 Steps)

### Step 1️⃣: Run Analyzer in Packet Tracer (2 min)

```
1. Extensions → Scripting → Edit File Script Module
2. Delete everything
3. Paste the contents of: pt_analyzer.js
4. Click Run
5. Wait for output (should show all devices + configs)
```

**You'll see:**
```
╔════════════════════════════════════════════════════════╗
║         KEYSTONE - PT TOPOLOGY ANALYZER v1.0          ║
╚════════════════════════════════════════════════════════╝

═══ TOPOLOGY SUMMARY ═══
Total devices: 5
...
[Device names, models, ports]
...
━━━ EXTRACTED CONFIGURATIONS ━━━
[All running configs displayed here]
```

### Step 2️⃣: Parse to YAML (1 min)

```bash
# 1. Copy the entire output from Step 1
# 2. Create a file: configs.txt
# 3. Paste the output
# 4. Run:

python3 pt_config_parser.py configs.txt --yaml

# Output: configs_topology.yaml
```

**Result:**
```yaml
devices:
  - hostname: Router1
    type: router
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.1.1
        mask: 255.255.255.0
```

### Step 3️⃣: Modify & Rebuild (2 min)

**Edit the YAML** (change whatever you want):

```yaml
devices:
  - hostname: Router1                    # ← Change name
    type: router
    interfaces:
      - name: GigabitEthernet0/0
        ip: 10.0.2.1                     # ← Change IP
        mask: 255.255.255.0
```

**Then rebuild** with topology_composer:

```bash
python3 topology_composer.py \
  --file configs_topology.yaml \
  --output new_commands.txt
```

**Now use main.js** to deploy the new topology to Packet Tracer.

---

## Real Example

### Original PT Topology
```
Device: ISP-Router
IP: 203.0.113.1
OSPF: Network 203.0.113.0/24
```

### Extract with Analyzer
```
$ python3 pt_config_parser.py extracted.txt --yaml

Parsed: ISP-Router
Generated: extracted_topology.yaml
```

### Modify the YAML
```yaml
hostname: BRANCH-Router      # ← Changed from ISP-Router
interfaces:
  - name: GigabitEthernet0/0
    ip: 192.168.1.1          # ← Changed from 203.0.113.1
```

### Deploy New Topology
```bash
python3 topology_composer.py --file extracted_topology.yaml
# Generates CLI commands for new IP range
```

---

## What You Get

✅ Extract device counts
✅ Extract all running configs
✅ Parse to human-editable YAML
✅ Modify IPs, hostnames, VLANs
✅ Auto-generate new CLI commands
✅ Deploy to PT via scripting

---

## One More Thing...

The real magic is that **all 3 steps are reversible**:

```
Real PT Topology
    ↓ (Analyzer extracts)
Raw Cisco Configs
    ↓ (Parser converts)
YAML Definition
    ↓ (Modify anything)
Modified YAML
    ↓ (topology_composer generates)
CLI Commands
    ↓ (Main.js injects)
New PT Topology ✨
```

You can run this cycle infinitely—extract, modify, rebuild, repeat.

---

## File Reference

| File | What It Does |
|------|-------------|
| `pt_analyzer.js` | Run in PT to extract configs |
| `pt_config_parser.py` | Convert raw configs to YAML |
| `topology_composer.py` | Generate CLI from YAML |
| `main.js` | Inject CLI into PT devices |

---

## Troubleshooting

**Q: Analyzer shows no devices?**
- Make sure at least one device is in the topology
- Verify Extensions > Scripting is enabled

**Q: Parser throws errors?**
- Make sure the config output is complete (has `end` at bottom)
- Check file encoding is UTF-8

**Q: CLI injection fails?**
- Device might be waiting for setup dialog (add `no` first)
- Try increasing sleep times

---

**Ready?** Start with Step 1️⃣ right now!

