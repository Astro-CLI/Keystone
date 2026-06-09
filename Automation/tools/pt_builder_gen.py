import re

def normalize_port(port):
    p = str(port).strip()
    p_lower = p.lower()
    
    port_map = {
        'inside': 'GigabitEthernet0/0',
        'outside': 'GigabitEthernet0/1',
        'dmz': 'GigabitEthernet0/2',
    }
    if p_lower in port_map:
        return port_map[p_lower]
        
    m = re.match(r'^gi(?:gabit)?(?:ethernet)?(\d+(?:/\d+)*)$', p, re.IGNORECASE)
    if m: return f"GigabitEthernet{m.group(1)}"
    m = re.match(r'^g(\d+(?:/\d+)*)$', p, re.IGNORECASE)
    if m: return f"GigabitEthernet{m.group(1)}"
        
    m = re.match(r'^fa(?:st)?(?:ethernet)?(\d+(?:/\d+)*)$', p, re.IGNORECASE)
    if m: return f"FastEthernet{m.group(1)}"
    m = re.match(r'^f(\d+(?:/\d+)*)$', p, re.IGNORECASE)
    if m: return f"FastEthernet{m.group(1)}"
        
    m = re.match(r'^se(?:rial)?(\d+(?:/\d+)*)$', p, re.IGNORECASE)
    if m: return f"Serial{m.group(1)}"
    m = re.match(r'^s(\d+(?:/\d+)*)$', p, re.IGNORECASE)
    if m: return f"Serial{m.group(1)}"
        
    if re.match(r'^\d+(?:/\d+)*$', p):
        return f"GigabitEthernet{p}"
    return p


def requires_module(port):
    p = str(port).strip()
    if re.match(r'^(?:Serial|Se|S)\d', p, re.IGNORECASE):
        return True
    nums = re.findall(r'\d+', p)
    if len(nums) >= 3: # e.g. 0/0/0
        return True
    return False


def get_link_type(port1, port2):
    if re.match(r'^(?:Serial|Se|S)\d', port1, re.IGNORECASE) or re.match(r'^(?:Serial|Se|S)\d', port2, re.IGNORECASE):
        return "serial"
    return "straight"


def extract_device_configs(cli_text):
    configs = {}
    current_hostname = None
    current_lines = []
    marker_pattern = re.compile(r'^!\s+---\s+(.+?)\s+---')
    for line in cli_text.split('\n'):
        m = marker_pattern.match(line)
        if m:
            if current_hostname and current_lines:
                configs[current_hostname] = '\n'.join(current_lines).strip()
            current_hostname = m.group(1).strip()
            current_lines = []
        elif current_hostname:
            current_lines.append(line)
    if current_hostname and current_lines:
        configs[current_hostname] = '\n'.join(current_lines).strip()
    return configs


def generate_pt_workflow(data, cli_text):
    """
    7-Step Demo Workflow Generator.
    Calculates positions for a clean 3-tier visual.
    """
    if not data: return []

    devices = data.get('devices', []) if isinstance(data, dict) else data
    links = data.get('links', data.get('connections', [])) if isinstance(data, dict) else []

    routers = [d for d in devices if (d.get('type') or 'router').lower() in ['router', 'firewall', 'asa']]
    switches = [d for d in devices if (d.get('type') or '').lower() == 'switch']
    pcs = [d for d in devices if (d.get('type') or '').lower() in ['pc', 'server', 'laptop']]
    
    rNames = {d.get('hostname') for d in routers}
    sNames = {d.get('hostname') for d in switches}
    pNames = {d.get('hostname') for d in pcs}
    
    steps = []

    # 1. Core Mesh
    s1 = ["// STEP 1: Core Router Mesh", ""]
    # Triangle positions
    tri = [{'x': 400, 'y': 50}, {'x': 200, 'y': 250}, {'x': 600, 'y': 250}]
    for i, d in enumerate(routers):
        pos = d.get('position') or tri[i % 3]
        s1.append(f'addDevice("{d["hostname"]}", "{d.get("model", "2911")}", {pos["x"]}, {pos["y"]});')
    
    for l in links:
        s_dev, s_p = l['source'].split(':')
        t_dev, t_p = l['target'].split(':')
        if s_dev in rNames and t_dev in rNames and not (requires_module(s_p) or requires_module(t_p)):
            s1.append(f'addLink("{s_dev}", "{normalize_port(s_p)}", "{t_dev}", "{normalize_port(t_p)}", "{get_link_type(s_p, t_p)}");')
    steps.append({"title": "Core Mesh", "code": "\n".join(s1)})

    # 2. Hardware Modules
    s2 = ["// STEP 2: Expansion Modules", ""]
    dev_mods = {name: set() for name in rNames}
    for l in links:
        for side in ['source', 'target']:
            dev, port = l[side].split(':')
            if dev in rNames and requires_module(port):
                nums = re.findall(r'\d+', port)
                slot = int(nums[1]) if len(nums) >= 3 else int(nums[0])
                mod = "HWIC-2T" if 's' in port.lower() or 'se' in port.lower() else "HWIC-1GE-SFP"
                dev_mods[dev].add((slot, mod))
    
    for dev, mods in dev_mods.items():
        for slot, mod in mods:
            s2.append(f'addModule("{dev}", {slot}, "{mod}");')
    
    s2.append("\n// Establishing Module-based Links")
    for l in links:
        s_dev, s_p = l['source'].split(':')
        t_dev, t_p = l['target'].split(':')
        if s_dev in rNames and t_dev in rNames and (requires_module(s_p) or requires_module(t_p)):
            s2.append(f'addLink("{s_dev}", "{normalize_port(s_p)}", "{t_dev}", "{normalize_port(t_p)}", "{get_link_type(s_p, t_p)}");')
    steps.append({"title": "Hardware Modules", "code": "\n".join(s2)})

    # 3. Distribution Layer
    s3 = ["// STEP 3: Distribution Switches", ""]
    dsw_list = [s for s in switches if s['hostname'].startswith('DSW')]
    for i, d in enumerate(dsw_list):
        pos = d.get('position') or {'x': 100 + (i * 150), 'y': 400}
        s3.append(f'addDevice("{d["hostname"]}", "{d.get("model", "3560-24PS")}", {pos["x"]}, {pos["y"]});')
    
    for l in links:
        s_dev, s_p = l['source'].split(':')
        t_dev, t_p = l['target'].split(':')
        if (s_dev.startswith('DSW') and t_dev in rNames) or (s_dev in rNames and t_dev.startswith('DSW')) or (s_dev.startswith('DSW') and t_dev.startswith('DSW')):
            s3.append(f'addLink("{s_dev}", "{normalize_port(s_p)}", "{t_dev}", "{normalize_port(t_p)}", "straight");')
    steps.append({"title": "Distribution Layer", "code": "\n".join(s3)})

    # 4. Access Layer
    s4 = ["// STEP 4: Access & End Devices", ""]
    asw_list = [s for s in switches if s['hostname'].startswith('ASW')]
    for i, d in enumerate(asw_list):
        pos = d.get('position') or {'x': 50 + (i * 100), 'y': 550}
        s4.append(f'addDevice("{d["hostname"]}", "2960-24TT", {pos["x"]}, {pos["y"]});')
    for i, d in enumerate(pcs):
        pos = d.get('position') or {'x': 30 + (i * 60), 'y': 700}
        s4.append(f'addDevice("{d["hostname"]}", "PC-PT", {pos["x"]}, {pos["y"]});')
    
    for l in links:
        s_dev, s_p = l['source'].split(':')
        t_dev, t_p = l['target'].split(':')
        if s_dev.startswith('ASW') or t_dev.startswith('ASW') or s_dev in pNames or t_dev in pNames:
            if not (s_dev in rNames or t_dev in rNames) and not (s_dev.startswith('DSW') and t_dev.startswith('DSW')):
                s4.append(f'addLink("{s_dev}", "{normalize_port(s_p)}", "{t_dev}", "{normalize_port(t_p)}", "straight");')
    steps.append({"title": "Access Layer", "code": "\n".join(s4)})

    # 5. PC Addressing
    s5 = ["// STEP 5: Host Configuration", ""]
    def subnet_index(dev):
        grp = str(dev.get('group') or dev.get('hostname') or '')
        m = re.search(r'(\d+)', grp)
        if not m:
            return 1
        n = int(m.group(1))
        return min(3, max(1, ((n - 1) // 4) + 1))

    def host_suffix(dev):
        hn = str(dev.get('hostname') or '')
        if dev.get('type') == 'server':
            return 100
        if hn.startswith('PC1_'):
            return 11
        if hn.startswith('PC2_'):
            return 12
        pos = dev.get('pos')
        if str(pos) == '0':
            return 11
        if str(pos) == '1':
            return 12
        return 100

    for d in pcs:
        subnet = subnet_index(d)
        suffix = host_suffix(d)
        ip = d.get("ip") or f"192.168.{subnet}.{suffix}"
        mask = d.get("mask") or "255.255.255.0"
        gateway = d.get("gateway") or f"192.168.{subnet}.1"
        dns = d.get("dns") or f"192.168.{subnet}.100"
        s5.append(f'configurePcIp("{d["hostname"]}", false, "{ip}", "{mask}", "{gateway}", "{dns}");')
        ipv6 = d.get("ipv6") or d.get("ipv6_address") or f"2001:db8:{subnet}::{suffix}/64"
        ipv6_gw = d.get("ipv6_gateway") or f"2001:db8:{subnet}::1"
        ipv6_dns = d.get("ipv6_dns") or f"2001:db8:{subnet}::100"
        s5.append(f'// IPv6: {ipv6} | gw {ipv6_gw} | dns {ipv6_dns}')
    steps.append({"title": "Host Addressing", "code": "\n".join(s5)})

    # 6. Switch CLI
    s6 = ["// STEP 6: Switch CLI Injection", ""]
    configs = extract_device_configs(cli_text)
    for name, cfg in configs.items():
        if name in sNames:
            clean_cfg = "\\n".join([c.strip() for c in cfg.split('\n') if c.strip() and not c.strip().startswith('!')])
            s6.append(f'configureIosDevice("{name}", "no\\nenable\\nconf t\\n{clean_cfg}\\nend\\nwrite mem");')
    steps.append({"title": "Switch CLI", "code": "\n".join(s6)})

    # 7. Router CLI
    s7 = ["// STEP 7: Router CLI Injection", ""]
    for name, cfg in configs.items():
        if name in rNames:
            clean_cfg = "\\n".join([c.strip() for c in cfg.split('\n') if c.strip() and not c.strip().startswith('!')])
            s7.append(f'configureIosDevice("{name}", "no\\nenable\\nconf t\\n{clean_cfg}\\nend\\nwrite mem");')
    steps.append({"title": "Router CLI", "code": "\n".join(s7)})

    return steps

def generate_pt_builder_script(data, cli_text):
    return "\n\n".join([s['code'] for s in generate_pt_workflow(data, cli_text)])
