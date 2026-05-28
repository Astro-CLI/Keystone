# All Workflows & Use Patterns

This document covers every workflow in Keystone. Pick the one that matches your goal.

---

## Workflow 0: GUI-Based Generation (Python Desktop)

**Goal:** Generate CLI and PT-Builder output using the point-and-click desktop GUI.

**Time:** 2 minutes

**Steps:**

```bash
# 1. Launch the GUI
python3 KeystoneGUI.py
```

2. Select a generator from the sidebar (collapsible categories: Routing, Services, Network Design, Address Planning)
3. Use the search bar to filter generators
4. Edit the YAML template in the editor pane
5. Click **Generate** (or press Ctrl+Enter)
6. Switch between **CLI** and **PT-Builder** output tabs
7. Copy output to clipboard or **Export** as `.yaml`/`.txt` file

**GUI Layout:**
- **Top bar**: Generate, Reset, Import/Export buttons
- **Sidebar**: Search + collapsible categories with 13 generator tools
- **Editor**: YAML template for the selected tool
- **Output**: Dual-tabbed (CLI commands + PT-Builder script)
- **Status bar**: Ready / Generated / Error feedback

**What you can do:**
- Generate CLI commands for any of the 13 protocol generators
- Generate PT-Builder Python scripts for `.pkt` creation
- Import existing YAML topologies for modification
- Export generated CLI or PT-Builder output
- Full Topology tool: 12 devices, 12 links, multi-protocol in one click

---

## Workflow 0b: Browser SPA Generation

**Goal:** Same as Workflow 0 but in a browser.

**Time:** 2 minutes

**Steps:**

```bash
# Open orchestrator.html in any browser
open orchestrator.html
```

Same 13 tools, same CLI/PT-Builder dual output, cyber-obsidian design.

---

## Workflow 1: Extract -> Modify -> Rebuild

**Goal:** Extract an existing topology, modify it, and rebuild it.

**Time:** 15 minutes

**Steps:**

```bash
# 1. Extract from Packet Tracer
#    (Run scripts/pt_analyzer.js in PT via Extensions → Scripting)
#    Copy output to configs.txt

# 2. Parse to YAML
python3 scripts/pt_config_parser.py configs.txt --yaml

# 3. Edit the YAML (change IPs, hostnames, etc.)
nano configs_topology.yaml

# 4. Generate new CLI commands
python3 tools/topology_composer.py --file configs_topology.yaml

# 5. Deploy back to PT
#    (Run main.js via Extensions → Scripting)
```

**Output:** Newly rebuilt topology with your changes applied.

**See also:** [docs/GETTING_STARTED.md](GETTING_STARTED.md) — Step-by-step guide

---

## 🎬 Workflow 2: YAML → Runnable main.js

**Goal:** Convert a YAML topology definition into a self-contained Packet Tracer script.

**Time:** 5 minutes

**Steps:**

```bash
# 1. Have a topology in YAML
#    (Use examples/simple_topology.yaml as template)

# 2. Generate main.js
python3 tools/yaml_to_mainjs.py \
  examples/simple_topology.yaml \
  --output generated_main.js

# 3. In Packet Tracer:
#    - Make sure you have seed devices (one router, one switch, etc.)
#    - Extensions → Scripting → Edit File Script Module
#    - Paste generated_main.js
#    - Click Run

# 4. The script will:
#    - Spawn devices
#    - Inject CLI configs
#    - Print manual link plan
```

**Output:** Fully configured topology with all devices and configs applied.

**Options:**

```bash
# Spawn devices only (no config injection)
python3 tools/yaml_to_mainjs.py file.yaml --no-config

# Skip the manual link plan
python3 tools/yaml_to_mainjs.py file.yaml --no-link-plan

# Custom layout
python3 tools/yaml_to_mainjs.py file.yaml \
  --start-x 100 \
  --start-y 100 \
  --spacing-x 150 \
  --spacing-y 150 \
  --columns 3
```

**Key Limitation:** You must have seed devices already on the canvas. The script duplicates from templates, not creates from scratch.

**See also:** [docs/GENERATORS_GUIDE.md](GENERATORS_GUIDE.md) — Advanced generator options

---

## 🔍 Workflow 3: Export Live Topology as YAML

**Goal:** Copy a live Packet Tracer topology as YAML directly from the debug console.

**Time:** 3 minutes

**Steps:**

```bash
# 1. Open your .pkt file in Packet Tracer

# 2. Extensions → Scripting → Edit File Script Module

# 3. Paste: scripts/pt_yaml_exporter.js

# 4. Click Run

# 5. Copy the YAML from the debug console output

# 6. Save as topology.yaml

# 7. You can now:
#    - Edit the YAML
#    - Share it with teammates
#    - Use it to rebuild elsewhere
```

**Output:** Copyable YAML block from debug console.

**Captures:**
- Device names and models
- Device types and positions
- Port information
- Running config blocks (when available)
- Connection hints

**Why use this?**
- Fastest way to export a live topology
- No intermediate files needed
- Output goes directly to clipboard
- Useful for collaboration

---

## 🏗️ Workflow 4: Create .pkt Files Programmatically

**Goal:** Generate binary `.pkt` files from YAML/JSON/XML definitions.

**Time:** 5 minutes

**Steps:**

**Option A: Command Line**

```bash
python3 tools/pt_file_builder.py \
  --topology examples/simple_topology.yaml \
  --output my_lab.pkt
```

**Option B: Python Script**

```python
from tools.pt_file_builder import PktFileBuilder

builder = PktFileBuilder('my_topology.yaml')
builder.build('output/my_lab.pkt')
```

**Option C: JSON or XML**

```bash
python3 tools/pt_file_builder.py \
  --topology examples/simple_topology.json \
  --output my_lab.pkt

# Or XML
python3 tools/pt_file_builder.py \
  --topology examples/simple_topology.xml \
  --output my_lab.pkt
```

**Output:** A binary `.pkt` file ready to open in Packet Tracer.

**Why use this?**
- Programmatic lab creation
- Batch lab generation
- CI/CD integration
- Avoid manual PT canvas work

---

## 🧪 Workflow 5: Discover Packet Tracer Runtime Capabilities

**Goal:** Probe the PT runtime to find all available functions, objects, and methods.

**Time:** 10 minutes

**Steps:**

```bash
# 1. Extensions → Scripting → Edit File Script Module

# 2. Paste: scripts/pt_api_explorer.js

# 3. Click Run

# 4. Review the output:
#    - Syntax probes (functions, objects, JSON support)
#    - Global symbols (what's available)
#    - Network object methods
#    - Device/Port/Process object methods
```

**Outputs:**

```
═══ RUNTIME / SYNTAX PROBES ═══
  ✓ function call
  ✓ object literal
  ✓ array push
  ✓ for..in
  ✗ Java interop (not available)
  ✗ Packages (not available)

═══ GLOBAL SYMBOLS ═══
  ipc: present
  JSON: present
  Object: present
  [... and 70+ more ...]

═══ NETWORK OBJECT ═══
  network methods (14):
    getClassName()
    getDevice()
    getDeviceCount()
    [... and more ...]
```

**Why use this?**
- Understand what APIs your PT version supports
- Debug scripting issues
- Discover hidden functions
- Verify runtime capabilities

**See also:** [docs/PT_SCRIPTING_API.md](PT_SCRIPTING_API.md) — Detailed API reference

---

## 🔬 Workflow 6: Deep API Probe for Hidden Methods

**Goal:** Recursively walk the PT runtime to find every available method and property.

**Time:** 15 minutes

**Steps:**

```bash
# 1. Extensions → Scripting → Edit File Script Module

# 2. Paste: scripts/pt_hidden_api_probe.js

# 3. Click Run

# 4. Review the extensive output showing:
#    - All globals and prototypes
#    - Safe getter methods (zero-arg, non-mutating)
#    - Object chains and hierarchies
#    - Potential undiscovered APIs
```

**Output:** Comprehensive inventory of PT runtime surface.

**Why use this?**
- Find APIs not documented elsewhere
- Understand object relationships
- Debug unusual errors
- Discover experimental/hidden methods

---

## 🔄 Workflow 7: Multi-Protocol Lab Generation

**Goal:** Generate complete multi-protocol topologies (OSPF + BGP + NAT + DHCP).

**Time:** 20 minutes

**Steps:**

```bash
# 1. Start with a base topology
cp examples/simple_topology.yaml my_lab.yaml

# 2. Generate OSPF config
python3 generators/ospf_pathmaker.py \
  --topology my_lab.yaml \
  --output ospf_config.yaml

# 3. Merge OSPF results back into your topology
# (Edit my_lab.yaml and add OSPF section)

# 4. Generate BGP config (for other devices)
python3 generators/bgp_conductor.py \
  --topology my_lab.yaml \
  --output bgp_config.yaml

# 5. Continue with other protocols as needed
#    NAT, DHCP, HSRP, SSH, VLAN, etc.

# 6. Merge all into final topology

# 7. Generate main.js
python3 tools/yaml_to_mainjs.py my_lab.yaml --output main.js

# 8. Run in Packet Tracer
```

**Available Generators:**
- `ospf_pathmaker.py` — OSPF routing
- `bgp_conductor.py` — BGP routing
- `eigrp_catalyst.py` — EIGRP routing
- `static_anchor.py` — Static routes
- `nat_portal.py` — NAT translations
- `dhcp_allocator.py` — DHCP pools
- `hsrp_sentinel.py` — HSRP failover
- `vlan_weaver.py` — VLAN configuration
- `ssh_locksmith.py` — SSH security
- `asa_shield.py` — ASA firewall
- `ip_architect.py` — IP addressing
- `cidr_architect.py` — CIDR calculations

**See also:** [docs/GENERATORS_GUIDE.md](GENERATORS_GUIDE.md) — All generator reference

---

## 🛠️ Workflow 8: Custom CI/CD Integration

**Goal:** Integrate Keystone into your CI/CD pipeline.

**Time:** 30 minutes setup

**Steps:**

```bash
# 1. Store topology YAML in version control
git add topologies/
git commit -m "Add lab templates"

# 2. In CI/CD script (e.g., .github/workflows/):
python3 tools/topology_composer.py \
  --file topologies/lab1.yaml \
  --output generated/lab1_commands.txt

# 3. Generate .pkt files
python3 tools/pt_file_builder.py \
  --topology topologies/lab1.yaml \
  --output generated/lab1.pkt

# 4. Artifact upload
git add generated/lab1.pkt
git add generated/lab1_commands.txt

# 5. Students/colleagues can download the pre-built labs
```

**Benefits:**
- Automate lab distribution
- Version control topologies
- Generate labs on every commit
- Track changes in YAML (diff-able)
- Easy rollback to previous versions

---

## 🚀 Workflow 9: Batch Lab Creation

**Goal:** Create 50 variations of a topology for different students.

**Time:** 5 minutes (automated)

**Steps:**

```bash
# 1. Create a template
cp examples/simple_topology.yaml template.yaml

# 2. Create a Python script to batch-generate variations
cat > batch_labs.py << 'EOF'
import yaml
import subprocess
import os

# Load template
with open('template.yaml') as f:
    template = yaml.safe_load(f)

# Generate 50 labs with different IP subnets
for i in range(1, 51):
    lab = template.copy()
    
    # Modify IPs for each lab
    for device in lab['devices']:
        for interface in device.get('interfaces', []):
            # Change subnet to 10.i.0.0/24
            interface['ip'] = f"10.{i}.0.1"
    
    # Save
    output_file = f"output/lab_{i:02d}.yaml"
    with open(output_file, 'w') as f:
        yaml.dump(lab, f)
    
    # Generate .pkt
    subprocess.run([
        'python3', 'tools/pt_file_builder.py',
        '--topology', output_file,
        '--output', f'output/lab_{i:02d}.pkt'
    ])

print("✓ Generated 50 labs")
EOF

python3 batch_labs.py
```

**Output:** 50 customized `.pkt` files, ready to distribute.

**Why use this?**
- Save hours of manual work
- Ensure consistency across labs
- Easily create student variations
- Reduce human error

---

## 📊 Workflow 10: Format Conversion

**Goal:** Convert between YAML, JSON, and XML formats.

**Time:** 2 minutes

**Steps:**

```bash
# Extract to YAML
python3 scripts/pt_config_parser.py configs.txt --yaml
# → configs_topology.yaml

# Convert YAML to JSON
python3 -c "
import yaml, json
with open('configs_topology.yaml') as f:
    data = yaml.safe_load(f)
print(json.dumps(data, indent=2))
" > configs_topology.json

# Convert to XML (if needed)
# Use format_parser.py for multi-format support
python3 tools/format_parser.py configs_topology.yaml --output xml
# → configs_topology.xml
```

**Which format to use?**
- **YAML:** Recommended for humans (40% smaller, more readable)
- **JSON:** For APIs and programmatic access
- **XML:** For legacy systems or special integrations

---

## Workflow Comparison

| Workflow | Extract | Modify | Generate | Deploy | Time | Use Case |
|----------|---------|--------|----------|--------|------|----------|
| 0. GUI Generation | — | ✅ GUI | CLI+PT | Copy | 2 min | Quick generation |
| 0b. Browser SPA | — | ✅ Web | CLI+PT | Copy | 2 min | Web-based gen |
| 1. Extract/Modify/Rebuild | ✅ PT | ✅ YAML | CLI | PT | 15 min | Existing labs |
| 2. YAML -> main.js | — | ✅ YAML | main.js | PT | 5 min | Template-based |
| 3. Export Topology | ✅ Live | — | YAML | Copy | 3 min | Quick export |
| 4. Create .pkt | — | ✅ File | .pkt file | Standalone | 5 min | Batch creation |
| 5. Discover APIs | — | — | Report | Console | 10 min | Debugging |
| 6. Deep Probe | — | — | Report | Console | 15 min | API research |
| 7. Multi-Protocol | — | ✅ YAML | Multi-gen | PT | 20 min | Complex labs |
| 8. CI/CD | ✅ Git | ✅ Git | Artifact | Download | Setup | Distribution |
| 9. Batch Create | — | Script | 50x .pkt | Download | 5 min | 100s of labs |
| 10. Format Conv. | — | ✅ Format | Multi-format | File | 2 min | Interop |

---

## Pick Your Workflow

**I want to generate configs quickly:**
- Click a button -> Use **Workflow 0** (GUI) or **Workflow 0b** (Browser SPA)

**I have a live topology in PT and want to:**
- Export it -> Use **Workflow 3** (Live Export)
- Modify it -> Use **Workflow 1** (Extract/Modify/Rebuild)

**I have a YAML topology definition and want to:**
- Deploy it to PT -> Use **Workflow 2** (YAML -> main.js)
- Create a .pkt file -> Use **Workflow 4** (Create .pkt)
- Generate protocols -> Use **Workflow 7** (Multi-Protocol)

**I want to:**
- Distribute labs to 100 students -> Use **Workflow 9** (Batch Create)
- Integrate with CI/CD -> Use **Workflow 8** (CI/CD)
- Convert formats -> Use **Workflow 10** (Format Conv.)

**I need to:**
- Debug API issues -> Use **Workflow 5** (API Probe)
- Find hidden functions -> Use **Workflow 6** (Deep Probe)

---

## For More Information

- **Getting Started:** `docs/GETTING_STARTED.md`
- **All Generators:** `docs/GENERATORS_GUIDE.md`
- **API Reference:** `docs/PT_API_DEEP_REFERENCE.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING_GUIDE.md`

---

**Ready to pick a workflow? Start with `python3 KeystoneGUI.py` or `docs/GETTING_STARTED.md`!**
