# 🎛️ Generators Directory

This folder contains 12 protocol-specific generators for network automation.

---

## 📋 Quick Reference

| Generator | Purpose | Use Case |
|-----------|---------|----------|
| `ospf_pathmaker.py` | OSPF routing | Dynamic routing protocols |
| `bgp_conductor.py` | BGP routing | External routing / Multi-AS |
| `eigrp_catalyst.py` | EIGRP routing | Enhanced interior routing |
| `static_anchor.py` | Static routes | Simple route topologies |
| `dhcp_allocator.py` | DHCP pools | Address allocation services |
| `nat_portal.py` | NAT translations | Network address translation |
| `hsrp_sentinel.py` | HSRP failover | Redundant gateways |
| `ssh_locksmith.py` | SSH security | Secure device access |
| `vlan_weaver.py` | VLAN configuration | Virtual LAN networks |
| `asa_shield.py` | ASA firewall | Firewall rules & policies |
| `ip_architect.py` | IP addressing | Address scheme planning |
| `cidr_architect.py` | CIDR subnetting | Subnet calculations |

---

## 🚀 Usage Pattern

All generators follow the same pattern:

```bash
python3 generators/[generator_name].py \
  --topology path/to/topology.yaml \
  --output output_file.yaml \
  [additional options]
```

---

## 📚 Full Documentation

**See:** [../docs/GENERATORS_GUIDE.md](../docs/GENERATORS_GUIDE.md) for complete reference covering:
- All 12 generators in detail
- Input/output formats
- Usage examples
- Multi-generator workflows
- Integration patterns

---

## 🔄 Generator Workflow

1. Start with a base topology (YAML)
2. Run one or more generators
3. Merge outputs into final topology
4. Use tools to deploy

Example:

```bash
# Extract existing topology
python3 scripts/pt_analyzer.js > configs.txt
python3 scripts/pt_config_parser.py configs.txt --yaml

# Enhance with OSPF
python3 generators/ospf_pathmaker.py --topology configs_topology.yaml

# Enhance with DHCP
python3 generators/dhcp_allocator.py --topology configs_topology.yaml

# Deploy
python3 tools/yaml_to_mainjs.py configs_topology.yaml --output main.js
```

---

## 🔗 Related Documentation

- **All Generator Reference:** [../docs/GENERATORS_GUIDE.md](../docs/GENERATORS_GUIDE.md)
- **All Workflows:** [../docs/WORKFLOWS.md](../docs/WORKFLOWS.md)
- **Tools:** [../tools/README.md](../tools/README.md)
- **Scripts:** [../scripts/README.md](../scripts/README.md)
- **Getting Started:** [../docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md)

---

**For detailed generator documentation, see:** [../docs/GENERATORS_GUIDE.md](../docs/GENERATORS_GUIDE.md)
