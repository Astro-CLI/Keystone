#!/usr/bin/env python3
"""
PT Script Generator - Option C
Generates Packet Tracer JavaScript scripts from topology definitions.

Uses Packet Tracer's official IPC scripting API (NOT the broken PTBuilder API).
Run the generated .js file via: Extensions > Scripting > Edit File Script Module

Workflow:
  1. python3 tools/pt_script_gen.py --file examples/my_topology.yaml --output my_lab.js
  2. Open Packet Tracer
  3. Manually place ONE of each required device type on the canvas (seed devices)
  4. Extensions -> Scripting -> Edit File Script Module
  5. Load my_lab.js and click Run
  6. Manually cable the connections listed in the script output
  7. File -> Save As -> my_lab.pkt

Why this works (and Option B doesn't):
  Option B tries to write .pkt binary files externally - PT rejects them.
  Option C uses PT's own IPC API from inside PT - PT accepts it natively.

Supported topology keys:
  devices[].hostname        - Device hostname (set via IOS CLI)
  devices[].type            - router | switch | pc | server | firewall | hub | cloud
  devices[].interfaces[]    - Interface configs (name, ip, mask, description, vlan)
  devices[].ospf            - OSPF routing (process_id, router_id, networks)
  devices[].bgp             - BGP routing (asn, router_id, neighbors, networks)
  devices[].eigrp           - EIGRP routing (asn, router_id, networks)
  devices[].dhcp            - DHCP server (pools, excluded)
  devices[].hsrp            - HSRP redundancy (groups)
  devices[].nat             - NAT config (inside_interfaces, outside_interfaces, static, dynamic)
  devices[].static_routes   - Static routes (destination, mask, next_hop)
  devices[].ssh             - SSH config (enabled: true)
  devices[].acls            - Access lists (number, rules)
  connections[]             - Links between devices (logged for manual cabling)
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from format_parser import parse_file


# Device type -> Packet Tracer model name mapping (used to find seed devices on canvas)
DEVICE_MODEL_MAP = {
    'router':       '2911',
    'switch':       '2960',
    'switch-3750':  '3750',
    'switch-2960':  '2960',
    'pc':           'PC-PT',
    'server':       'Server-PT',
    'firewall':     'ASAv',
    'asa':          'ASAv',
    'hub':          'Hub-PT',
    'cloud':        'Cloud-PT',
}

# Canvas layout constants
LAYOUT_COLS      = 5    # max devices per row
LAYOUT_SPACING_X = 220  # horizontal spacing in PT canvas units
LAYOUT_SPACING_Y = 220  # vertical spacing in PT canvas units
LAYOUT_START_X   = 120  # first device x position
LAYOUT_START_Y   = 120  # first device y position


class PTScriptGen:
    """Generates Packet Tracer IPC JavaScript scripts from topology definitions."""

    def __init__(self, topology_data):
        # format_parser returns a list for XML files (each element is a device dict);
        # YAML/JSON files return {'devices': [...], 'connections': [...]}.
        if isinstance(topology_data, list):
            self.topology = {'devices': topology_data}
        else:
            self.topology = topology_data
        self.devices = self.topology.get('devices', [])
        self.conns   = self.topology.get('connections', self.topology.get('links', []))

    # -------------------------------------------------------------------------
    # Public entry point
    # -------------------------------------------------------------------------

    def generate(self):
        """Return the complete JavaScript script as a string."""
        lines = []
        self._emit_header(lines)
        self._emit_main_open(lines)
        self._emit_phase1_find_seeds(lines)
        self._emit_phase2_create_devices(lines)
        self._emit_phase3_connections(lines)
        self._emit_phase4_configure(lines)
        self._emit_main_close(lines)
        self._emit_configure_device_fn(lines)
        self._emit_cleanup(lines)
        return '\n'.join(lines)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _device_model(self, device):
        dtype = device.get('type', 'router').lower()
        return DEVICE_MODEL_MAP.get(dtype, '2911')

    def _required_models(self):
        """Return {model: device_type_label} for each unique model needed."""
        seen = {}
        for d in self.devices:
            m = self._device_model(d)
            if m not in seen:
                seen[m] = d.get('type', 'router').lower()
        return seen

    def _device_positions(self):
        """Return {hostname: (x, y)} for canvas layout."""
        positions = {}
        for i, d in enumerate(self.devices):
            col = i % LAYOUT_COLS
            row = i // LAYOUT_COLS
            x = LAYOUT_START_X + col * LAYOUT_SPACING_X
            y = LAYOUT_START_Y + row * LAYOUT_SPACING_Y
            positions[d.get('hostname', f'Device{i}')] = (x, y)
        return positions

    @staticmethod
    def _js_str(s):
        """Escape a Python string for embedding as a JS double-quoted string."""
        return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')

    @staticmethod
    def _safe_var(name):
        """Turn a hostname into a safe JS variable name."""
        return 'dev_' + ''.join(c if c.isalnum() else '_' for c in name)

    @staticmethod
    def _as_list(value):
        """Ensure a value is always a list (handles single dict from XML parsing)."""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    def _cli_commands(self, device):
        """Return the list of IOS CLI commands to fully configure a device."""
        hostname = device.get('hostname', 'Router')
        cmds = []

        cmds += ['enable', 'configure terminal', f'hostname {hostname}']

        # Interfaces
        for iface in self._as_list(device.get('interfaces', [])):
            iface_name  = iface.get('name', '')
            ip          = iface.get('ip')
            mask        = iface.get('mask')
            description = iface.get('description', '')
            vlan        = iface.get('vlan')

            if vlan:
                cmds.append(f'interface vlan {vlan}')
            else:
                cmds.append(f'interface {iface_name}')

            if description:
                cmds.append(f' description {description}')
            if ip and mask:
                cmds.append(f' ip address {ip} {mask}')
            cmds += [' no shutdown', ' exit']

        # OSPF
        if 'ospf' in device:
            ospf = device['ospf']
            pid  = ospf.get('process_id', 1)
            rid  = ospf.get('router_id', '')
            cmds.append(f'router ospf {pid}')
            if rid:
                cmds.append(f' router-id {rid}')
            for net in self._as_list(ospf.get('networks', [])):
                network  = net.get('network')
                wildcard = net.get('wildcard')
                area     = net.get('area', 0)
                if network and wildcard:
                    cmds.append(f' network {network} {wildcard} area {area}')
            cmds.append(' exit')

        # BGP
        if 'bgp' in device:
            bgp = device['bgp']
            asn = bgp.get('asn')
            rid = bgp.get('router_id', '')
            if asn:
                cmds.append(f'router bgp {asn}')
                if rid:
                    cmds.append(f' bgp router-id {rid}')
                for neighbor in self._as_list(bgp.get('neighbors', [])):
                    nip   = neighbor.get('ip')
                    nasn  = neighbor.get('asn')
                    ndesc = neighbor.get('description', '')
                    if nip and nasn:
                        cmds.append(f' neighbor {nip} remote-as {nasn}')
                        if ndesc:
                            cmds.append(f' neighbor {nip} description {ndesc}')
                for net in self._as_list(bgp.get('networks', [])):
                    network = net.get('network')
                    mask    = net.get('mask')
                    if network and mask:
                        cmds.append(f' network {network} mask {mask}')
                cmds.append(' exit')

        # EIGRP
        if 'eigrp' in device:
            eigrp = device['eigrp']
            asn   = eigrp.get('asn')
            rid   = eigrp.get('router_id', '')
            if asn:
                cmds.append(f'router eigrp {asn}')
                if rid:
                    cmds.append(f' eigrp router-id {rid}')
                for net in self._as_list(eigrp.get('networks', [])):
                    network  = net.get('network')
                    wildcard = net.get('wildcard')
                    if network and wildcard:
                        cmds.append(f' network {network} {wildcard}')
                cmds.append(' exit')

        # DHCP
        if 'dhcp' in device:
            dhcp = device['dhcp']
            for pool in self._as_list(dhcp.get('pools', [])):
                pool_name = pool.get('name')
                network   = pool.get('network')
                mask      = pool.get('mask')
                gateway   = pool.get('gateway')
                dns       = pool.get('dns', '8.8.8.8')
                if pool_name and network and mask:
                    cmds.append(f'ip dhcp pool {pool_name}')
                    cmds.append(f' network {network} {mask}')
                    if gateway:
                        cmds.append(f' default-router {gateway}')
                    cmds.append(f' dns-server {dns}')
                    cmds.append(' exit')
            for excl in self._as_list(dhcp.get('excluded', [])):
                start = excl.get('start')
                end   = excl.get('end')
                if start:
                    if end:
                        cmds.append(f'ip dhcp excluded-address {start} {end}')
                    else:
                        cmds.append(f'ip dhcp excluded-address {start}')

        # HSRP
        if 'hsrp' in device:
            for grp in self._as_list(device['hsrp'].get('groups', [])):
                vlan       = grp.get('vlan')
                gid        = grp.get('group_id')
                priority   = grp.get('priority', 100)
                virtual_ip = grp.get('virtual_ip')
                if vlan and gid and virtual_ip:
                    cmds += [
                        f'interface vlan {vlan}',
                        f' standby {gid} ip {virtual_ip}',
                        f' standby {gid} priority {priority}',
                        f' standby {gid} preempt',
                        ' no shutdown',
                        ' exit',
                    ]

        # NAT
        if 'nat' in device:
            nat = device['nat']
            for iface in self._as_list(nat.get('inside_interfaces', [])):
                cmds += [f'interface {iface}', ' ip nat inside', ' exit']
            for iface in self._as_list(nat.get('outside_interfaces', [])):
                cmds += [f'interface {iface}', ' ip nat outside', ' exit']
            for mapping in self._as_list(nat.get('static', [])):
                inside  = mapping.get('inside_ip')
                outside = mapping.get('outside_ip')
                if inside and outside:
                    cmds.append(f'ip nat inside source static {inside} {outside}')
            for pool in self._as_list(nat.get('dynamic', [])):
                pool_name = pool.get('name')
                start_ip  = pool.get('start_ip')
                end_ip    = pool.get('end_ip')
                if pool_name and start_ip and end_ip:
                    cmds.append(f'ip nat pool {pool_name} {start_ip} {end_ip} netmask 255.255.255.0')

        # Static routes
        for route in self._as_list(device.get('static_routes', [])):
            dest     = route.get('destination')
            mask     = route.get('mask')
            next_hop = route.get('next_hop')
            if dest and mask and next_hop:
                cmds.append(f'ip route {dest} {mask} {next_hop}')

        # SSH
        if device.get('ssh', {}).get('enabled'):
            cmds += [
                'ip domain-name lab.local',
                'crypto key generate rsa modulus 1024',
                'line vty 0 4',
                ' transport input ssh',
                ' exit',
            ]

        # ACLs
        for acl in self._as_list(device.get('acls', [])):
            acl_num = acl.get('number')
            for rule in self._as_list(acl.get('rules', [])):
                action      = rule.get('action', 'permit')
                protocol    = rule.get('protocol', 'ip')
                source      = rule.get('source')
                destination = rule.get('destination', 'any')
                if source:
                    cmds.append(f'access-list {acl_num} {action} {protocol} {source} {destination}')

        cmds += ['end', 'write memory']
        return cmds

    # -------------------------------------------------------------------------
    # Script emission helpers
    # -------------------------------------------------------------------------

    def _L(self, lines, text=''):
        lines.append(text)

    def _emit_header(self, lines):
        models   = self._required_models()
        n_devs   = len(self.devices)
        n_conns  = len(self.conns)

        self._L(lines, '// ============================================================')
        self._L(lines, '// Keystone PT Script  -  Generated by Keystone Automation')
        self._L(lines, '//')
        self._L(lines, '// HOW TO USE')
        self._L(lines, '//   1. Open Packet Tracer')
        self._L(lines, '//   2. Place ONE seed device on the canvas for each type below:')
        for model, dtype in models.items():
            self._L(lines, f'//        - One {model}  ({dtype})')
        self._L(lines, '//   3. Extensions  ->  Scripting  ->  Edit File Script Module')
        self._L(lines, '//   4. Load this file and click  Run')
        self._L(lines, '//   5. Manually cable the connections shown in the console output')
        self._L(lines, '//   6. Delete the original seed device(s) from the canvas')
        self._L(lines, '//   7. File  ->  Save As  ->  your_lab.pkt')
        self._L(lines, '//')
        self._L(lines, f'// Topology: {n_devs} device(s), {n_conns} connection(s)')
        self._L(lines, '// ============================================================')
        self._L(lines)

    def _emit_main_open(self, lines):
        self._L(lines, 'function main()')
        self._L(lines, '{')
        self._L(lines, '    dprint("=== KEYSTONE TOPOLOGY BUILDER ===");')
        self._L(lines, '    dprint("");')
        self._L(lines)
        self._L(lines, '    try {')
        self._L(lines)
        self._L(lines, '        var network    = ipc.network();')
        self._L(lines, '        var activeFile = ipc.appWindow().getActiveFile();')
        self._L(lines)
        self._L(lines, '        dprint("Seed devices on canvas: " + network.getDeviceCount());')
        self._L(lines)

    def _emit_phase1_find_seeds(self, lines):
        models = self._required_models()

        self._L(lines, '        // ===== PHASE 1: LOCATE SEED DEVICES =====')
        self._L(lines, '        dprint("[1/4] Locating seed devices...");')
        self._L(lines, '        var seeds = {};')
        self._L(lines, '        for (var i = 0; i < network.getDeviceCount(); i++) {')
        self._L(lines, '            var d     = network.getDeviceAt(i);')
        self._L(lines, '            var model = d.getModel();')
        self._L(lines, '            if (!seeds[model]) {')
        self._L(lines, '                seeds[model] = d;')
        self._L(lines, '                dprint("  OK  Found seed: " + model + " (" + d.getName() + ")");')
        self._L(lines, '            }')
        self._L(lines, '        }')
        self._L(lines)

        for model, dtype in models.items():
            escaped_model = self._js_str(model)
            self._L(lines, f'        if (!seeds["{escaped_model}"]) {{')
            self._L(lines, f'            dprint("  ERR  Missing seed: {escaped_model}");')
            self._L(lines, f'            dprint("       Add one {dtype} ({escaped_model}) to the canvas and re-run.");')
            self._L(lines,  '            return;')
            self._L(lines,  '        }')

        self._L(lines)

    def _emit_phase2_create_devices(self, lines):
        positions = self._device_positions()

        self._L(lines, '        // ===== PHASE 2: CREATE DEVICES =====')
        self._L(lines, '        dprint("[2/4] Creating devices...");')
        self._L(lines, '        var devs = {};')
        self._L(lines)

        for device in self.devices:
            hostname  = device.get('hostname', 'Device')
            model     = self._device_model(device)
            x, y      = positions[hostname]
            var_name  = self._safe_var(hostname)
            esc_host  = self._js_str(hostname)
            esc_model = self._js_str(model)

            self._L(lines, f'        // --- {hostname} ---')
            self._L(lines, f'        activeFile.duplicateDevice(seeds["{esc_model}"]);')
            self._L(lines, f'        var {var_name} = network.getDeviceAt(network.getDeviceCount() - 1);')
            self._L(lines, f'        {var_name}.moveToLocationCentered({x}, {y});')
            self._L(lines, f'        devs["{esc_host}"] = {var_name};')
            self._L(lines, f'        dprint("  +  {esc_host} at ({x}, {y})");')
            self._L(lines,  '        java.lang.Thread.sleep(300);')
            self._L(lines)

    def _emit_phase3_connections(self, lines):
        self._L(lines, '        // ===== PHASE 3: CONNECTIONS (manual cabling required) =====')
        self._L(lines, '        dprint("[3/4] Connections to cable manually:");')

        if self.conns:
            for conn in self.conns:
                # Support both topology_composer.py format and pt_scriptable_builder.py format
                from_dev   = conn.get('from_device',  conn.get('source', '').split(':')[0])
                from_iface = conn.get('from_interface', conn.get('source', '').split(':')[1] if ':' in conn.get('source', '') else '')
                to_dev     = conn.get('to_device',    conn.get('target', '').split(':')[0])
                to_iface   = conn.get('to_interface', conn.get('target', '').split(':')[1] if ':' in conn.get('target', '') else '')

                cable_str = f'{from_dev}:{from_iface}  <-->  {to_dev}:{to_iface}'
                self._L(lines, f'        dprint("  {self._js_str(cable_str)}");')
        else:
            self._L(lines, '        dprint("  (no connections defined in topology)");')

        self._L(lines)

    def _emit_phase4_configure(self, lines):
        self._L(lines, '        // ===== PHASE 4: CONFIGURE DEVICES =====')
        self._L(lines, '        dprint("[4/4] Configuring devices (this may take a moment)...");')
        self._L(lines)

        for device in self.devices:
            hostname  = device.get('hostname', 'Device')
            esc_host  = self._js_str(hostname)
            cmds      = self._cli_commands(device)

            # Format commands as a JS array literal
            cmd_items = ', '.join(f'"{self._js_str(c)}"' for c in cmds)
            self._L(lines, f'        dprint("  >> {esc_host}");')
            self._L(lines, f'        configureDevice(devs["{esc_host}"], [{cmd_items}]);')
            self._L(lines,  '        java.lang.Thread.sleep(500);')
            self._L(lines)

    def _emit_main_close(self, lines):
        self._L(lines, '        dprint("");')
        self._L(lines, '        dprint("=== TOPOLOGY COMPLETE ===");')
        self._L(lines, f'        dprint("  Devices created : {len(self.devices)}");')
        self._L(lines, f'        dprint("  Connections     : {len(self.conns)} (see above for cabling)");')
        self._L(lines, '        dprint("");')
        self._L(lines, '        dprint("Next steps:");')
        self._L(lines, '        dprint("  1. Cable the connections listed above");')
        self._L(lines, '        dprint("  2. Delete the original seed device(s)");')
        self._L(lines, '        dprint("  3. File -> Save As -> your_lab.pkt");')
        self._L(lines)
        self._L(lines, '    } catch(e) {')
        self._L(lines, '        dprint("FATAL ERROR: " + e.message);')
        self._L(lines, '        dprint(e.stack);')
        self._L(lines, '    }')
        self._L(lines, '}')
        self._L(lines)
        self._L(lines)

    def _emit_configure_device_fn(self, lines):
        """Emit the reusable configureDevice() helper function."""
        self._L(lines, '// ============================================================')
        self._L(lines, '// Helper: send a list of IOS CLI commands to a device')
        self._L(lines, '// ============================================================')
        self._L(lines, 'function configureDevice(device, commands)')
        self._L(lines, '{')
        self._L(lines, '    try {')
        self._L(lines, '        var cli = device.getCommandLine();')
        self._L(lines, '        if (cli == null) {')
        self._L(lines, '            dprint("  WARN  No CLI available for " + device.getName());')
        self._L(lines, '            return;')
        self._L(lines, '        }')
        self._L(lines)
        self._L(lines, '        // Dismiss the initial configuration dialog if it appears')
        self._L(lines, '        var initialOut = cli.getOutput();')
        self._L(lines, '        if (initialOut.indexOf("initial configuration dialog") > -1) {')
        self._L(lines, '            cli.enterCommand("no");')
        self._L(lines, '            java.lang.Thread.sleep(500);')
        self._L(lines, '        }')
        self._L(lines)
        self._L(lines, '        // Send each command with a short delay')
        self._L(lines, '        for (var i = 0; i < commands.length; i++) {')
        self._L(lines, '            cli.enterCommand(commands[i]);')
        self._L(lines, '            java.lang.Thread.sleep(100);')
        self._L(lines, '        }')
        self._L(lines)
        self._L(lines, '        dprint("  OK  " + device.getName());')
        self._L(lines)
        self._L(lines, '    } catch(e) {')
        self._L(lines, '        dprint("  ERR  " + device.getName() + ": " + e.message);')
        self._L(lines, '    }')
        self._L(lines, '}')
        self._L(lines)
        self._L(lines)

    def _emit_cleanup(self, lines):
        self._L(lines, 'function cleanUp()')
        self._L(lines, '{')
        self._L(lines, '    dprint("Script cleanup complete.");')
        self._L(lines, '}')
        self._L(lines)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='PT Script Generator - create Packet Tracer IPC scripts from topology files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/pt_script_gen.py --file examples/simple_topology.yaml --output output/simple_lab.js
  python3 tools/pt_script_gen.py --file examples/complex_topology.json --output output/complex_lab.js
  python3 tools/pt_script_gen.py --file examples/example_topology.yaml

In Packet Tracer:
  Extensions -> Scripting -> Edit File Script Module -> Load -> Run
        """
    )
    parser.add_argument(
        '--file', '-f',
        required=True,
        help='Path to topology definition file (YAML, JSON, or XML)'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output .js file path (default: print to stdout)'
    )

    args = parser.parse_args()

    try:
        topology = parse_file(args.file)
    except Exception as e:
        print(f'ERROR: Could not load topology file: {e}', file=sys.stderr)
        sys.exit(1)

    gen    = PTScriptGen(topology)
    script = gen.generate()

    if args.output:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, 'w') as fh:
                fh.write(script)

            n_devs  = len(gen.devices)
            n_conns = len(gen.conns)
            models  = gen._required_models()

            print(f'OK  Script written to: {args.output}')
            print(f'    Devices   : {n_devs}')
            print(f'    Connections: {n_conns}')
            print()
            print('Before running in PT, place these seed devices on the canvas:')
            for model, dtype in models.items():
                print(f'   - One {model}  ({dtype})')
            print()
            print('Then in Packet Tracer:')
            print('   Extensions -> Scripting -> Edit File Script Module')
            print(f'   Load: {args.output}  ->  Click Run')
        except Exception as e:
            print(f'ERROR: Could not write output file: {e}', file=sys.stderr)
            sys.exit(1)
    else:
        print(script)


if __name__ == '__main__':
    main()
