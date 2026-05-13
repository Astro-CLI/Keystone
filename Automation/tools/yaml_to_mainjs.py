#!/usr/bin/env python3
"""
YAML/JSON/XML to Packet Tracer main.js translator.

This tool takes a topology definition and generates a self-contained Packet Tracer
JavaScript file that:
  - spawns devices by duplicating existing seed devices on the canvas
  - positions the new devices
  - injects CLI configuration commands when requested
  - prints a manual link plan for topologies that define links

It is the "Option C + Option A" bridge:
  - Option C: spawn devices inside Packet Tracer
  - Option A: inject CLI configuration into those devices
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from format_parser import parse_file  # noqa: E402
from topology_composer import TopologyComposer  # noqa: E402


DEFAULT_LAYOUT = {
    "start_x": 80,
    "start_y": 80,
    "spacing_x": 220,
    "spacing_y": 180,
    "columns": 4,
}

DEVICE_HINTS = {
    "router": ["2911", "1941", "Router"],
    "switch": ["2960", "3750", "2950", "Switch"],
    "server": ["Server-PT", "Server"],
    "pc": ["PC-PT", "PC"],
    "asa": ["ASAv", "ASA"],
    "firewall": ["ASAv", "ASA"],
    "cloud": ["Cloud-PT", "Cloud"],
    "hub": ["Hub-PT", "Hub"],
    "printer": ["Printer-PT", "Printer"],
    "phone": ["IP Phone-PT", "Phone"],
    "wireless": ["Access Point-PT", "Wireless"],
}


class YAMLToMainJsTranslator:
    def __init__(self, topology, include_config=True, include_link_plan=True, layout=None):
        self.topology = self._normalize_topology(topology)
        self.include_config = include_config
        self.include_link_plan = include_link_plan
        self.layout = dict(DEFAULT_LAYOUT)
        if layout:
            self.layout.update(layout)

        self.composer = TopologyComposer(self.topology)
        self.command_map = {}
        self.devices = self._normalize_devices()
        self.links = self._normalize_links()

        if self.include_config:
            self.command_map = self._build_command_map()

    def _normalize_topology(self, topology):
        if isinstance(topology, list):
            if len(topology) == 1 and isinstance(topology[0], dict):
                topology = topology[0]
            else:
                topology = {"devices": topology}

        if not isinstance(topology, dict):
            raise ValueError("Topology must be a mapping with a devices list")

        return topology

    def _normalize_devices(self):
        items = self.topology.get("devices", []) or []
        normalized = []

        for index, device in enumerate(items):
            if not isinstance(device, dict):
                continue

            hostname = device.get("hostname") or device.get("name") or f"Device{index + 1}"
            device_type = str(device.get("type", "router")).lower()
            model = device.get("model") or self._default_model_for_type(device_type)
            position = self._extract_position(device, index)

            normalized.append(
                {
                    "index": index,
                    "hostname": hostname,
                    "type": device_type,
                    "model": model,
                    "position": position,
                    "commands": [],
                    "raw": device,
                }
            )

        return normalized

    def _normalize_links(self):
        links = self.topology.get("links")
        if not links:
            links = self.topology.get("connections", [])
        if not links:
            return []
        if isinstance(links, dict):
            links = [links]
        return [link for link in links if isinstance(link, dict)]

    def _build_command_map(self):
        self.composer.compose()
        return dict(self.composer.commands)

    def _default_model_for_type(self, device_type):
        mapping = {
            "router": "2911",
            "switch": "2960-24TT",
            "server": "Server-PT",
            "pc": "PC-PT",
            "asa": "ASAv",
            "firewall": "ASAv",
            "cloud": "Cloud-PT",
            "hub": "Hub-PT",
            "printer": "Printer-PT",
            "phone": "IP Phone-PT",
            "wireless": "Access Point-PT",
        }
        return mapping.get(device_type, "2911")

    def _extract_position(self, device, index):
        pos = device.get("position")
        if isinstance(pos, dict) and "x" in pos and "y" in pos:
            return {"x": pos["x"], "y": pos["y"]}

        if "x" in device and "y" in device:
            return {"x": device.get("x"), "y": device.get("y")}

        columns = max(1, int(self.layout.get("columns", DEFAULT_LAYOUT["columns"])))
        start_x = int(self.layout.get("start_x", DEFAULT_LAYOUT["start_x"]))
        start_y = int(self.layout.get("start_y", DEFAULT_LAYOUT["start_y"]))
        spacing_x = int(self.layout.get("spacing_x", DEFAULT_LAYOUT["spacing_x"]))
        spacing_y = int(self.layout.get("spacing_y", DEFAULT_LAYOUT["spacing_y"]))

        row = index // columns
        col = index % columns
        return {
            "x": start_x + (col * spacing_x),
            "y": start_y + (row * spacing_y),
        }

    def _js(self, value):
        return json.dumps(value, indent=2, sort_keys=True)

    def _seed_summary(self):
        kinds = []
        for device in self.devices:
            kind = device["type"]
            if kind not in kinds:
                kinds.append(kind)
        return kinds

    def generate(self):
        js = []
        js.append("// Keystone YAML -> Packet Tracer main.js")
        js.append("// Generated automatically from a topology definition")
        js.append("// Workflow: seed devices -> duplicate -> position -> configure")
        js.append("")
        js.append("var TOPOLOGY = " + self._js({"devices": self.devices, "links": self.links}) + ";")
        js.append("var COMMANDS = " + self._js(self.command_map) + ";")
        js.append("var DEVICE_HINTS = " + self._js(DEVICE_HINTS) + ";")
        js.append("var LAYOUT = " + self._js(self.layout) + ";")
        js.append("var LINK_PLAN_ENABLED = " + ("true" if self.include_link_plan else "false") + ";")
        js.append("")
        js.append("function main() {")
        js.append("    dprint('=== KEYSTONE YAML -> main.js TRANSLATOR ===');")
        js.append("    try {")
        js.append("        var appWindow = ipc.appWindow();")
        js.append("        var activeFile = appWindow.getActiveFile();")
        js.append("        var network = ipc.network();")
        js.append("        var seeds = snapshotSeeds(network);")
        js.append("        dprint('Seed devices on canvas: ' + seeds.length);")
        js.append("        dprint('Devices requested: ' + TOPOLOGY.devices.length);")
        js.append("")
        js.append("        for (var i = 0; i < TOPOLOGY.devices.length; i++) {")
        js.append("            var spec = TOPOLOGY.devices[i];")
        js.append("            var template = findTemplate(seeds, spec);")
        js.append("            if (template == null) {")
        js.append("                dprint('ERROR: No seed template found for ' + spec.hostname + ' (' + spec.type + ')');")
        js.append("                continue;")
        js.append("            }")
        js.append("")
        js.append("            activeFile.duplicateDevice(template);")
        js.append("            var device = network.getDeviceAt(network.getDeviceCount() - 1);")
        js.append("            if (device == null) {")
        js.append("                dprint('ERROR: duplicateDevice() did not return a reachable device for ' + spec.hostname);")
        js.append("                continue;")
        js.append("            }")
        js.append("")
        js.append("            positionDevice(device, spec, i);")
        js.append("            dprint('✓ Spawned ' + spec.hostname + ' at (' + spec.position.x + ', ' + spec.position.y + ')');")
        js.append("")
        js.append("            if (COMMANDS[spec.hostname] && COMMANDS[spec.hostname].length) {")
        js.append("                applyCommands(device, COMMANDS[spec.hostname]);")
        js.append("            }")
        js.append("        }")
        js.append("")
        js.append("        printManualLinkPlan();")
        js.append("        dprint('=== DONE ===');")
        js.append("    } catch (e) {")
        js.append("        dprint('ERROR: ' + e.message);")
        js.append("        if (e && e.stack) { dprint(e.stack); }")
        js.append("    }")
        js.append("}")
        js.append("")
        js.append("function cleanUp() {")
        js.append("    dprint('Script cleanup complete');")
        js.append("}")
        js.append("")
        js.append("function snapshotSeeds(network) {")
        js.append("    var out = [];")
        js.append("    var count = network.getDeviceCount();")
        js.append("    for (var i = 0; i < count; i++) {")
        js.append("        var device = network.getDeviceAt(i);")
        js.append("        if (device != null) { out.push(device); }")
        js.append("    }")
        js.append("    return out;")
        js.append("}")
        js.append("")
        js.append("function findTemplate(seeds, spec) {")
        js.append("    var candidates = buildCandidates(spec);")
        js.append("    for (var i = 0; i < seeds.length; i++) {")
        js.append("        var seed = seeds[i];")
        js.append("        var seedName = safeLower(getSafeString(seed, 'getName'));")
        js.append("        var seedModel = safeLower(getSafeString(seed, 'getModel'));")
        js.append("        for (var j = 0; j < candidates.length; j++) {")
        js.append("            var candidate = safeLower(candidates[j]);")
        js.append("            if (!candidate) { continue; }")
        js.append("            if (seedName.indexOf(candidate) !== -1 || seedModel.indexOf(candidate) !== -1) {")
        js.append("                return seed;")
        js.append("            }")
        js.append("        }")
        js.append("    }")
        js.append("    return seeds.length > 0 ? seeds[0] : null;")
        js.append("}")
        js.append("")
        js.append("function buildCandidates(spec) {")
        js.append("    var out = [];")
        js.append("    if (spec.model) { out.push(spec.model); }")
        js.append("    if (spec.type && DEVICE_HINTS[spec.type]) {")
        js.append("        for (var i = 0; i < DEVICE_HINTS[spec.type].length; i++) {")
        js.append("            out.push(DEVICE_HINTS[spec.type][i]);")
        js.append("        }")
        js.append("    }")
        js.append("    out.push(spec.hostname);")
        js.append("    return out;")
        js.append("}")
        js.append("")
        js.append("function positionDevice(device, spec, index) {")
        js.append("    var x = spec.position && spec.position.x != null ? spec.position.x : layoutX(index);")
        js.append("    var y = spec.position && spec.position.y != null ? spec.position.y : layoutY(index);")
        js.append("    device.moveToLocationCentered(x, y);")
        js.append("}")
        js.append("")
        js.append("function layoutX(index) {")
        js.append("    var columns = LAYOUT.columns || 4;")
        js.append("    var startX = LAYOUT.start_x || 80;")
        js.append("    var spacingX = LAYOUT.spacing_x || 220;")
        js.append("    return startX + ((index % columns) * spacingX);")
        js.append("}")
        js.append("")
        js.append("function layoutY(index) {")
        js.append("    var columns = LAYOUT.columns || 4;")
        js.append("    var startY = LAYOUT.start_y || 80;")
        js.append("    var spacingY = LAYOUT.spacing_y || 180;")
        js.append("    return startY + (Math.floor(index / columns) * spacingY);")
        js.append("}")
        js.append("")
        js.append("function applyCommands(device, commands) {")
        js.append("    var cmdLine = device.getCommandLine();")
        js.append("    if (cmdLine == null) {")
        js.append("        dprint('WARN: No CLI available for ' + getSafeString(device, 'getName'));")
        js.append("        return;")
        js.append("    }")
        js.append("")
        js.append("    var output = '';")
        js.append("    try { output = String(cmdLine.getOutput()); } catch (e) { output = ''; }")
        js.append("    if (output.indexOf('Would you like to enter the initial configuration dialog') !== -1) {")
        js.append("        cmdLine.enterCommand('no');")
        js.append("        waitMs(300);")
        js.append("    }")
        js.append("")
        js.append("    for (var i = 0; i < commands.length; i++) {")
        js.append("        cmdLine.enterCommand(commands[i]);")
        js.append("        waitMs(120);")
        js.append("    }")
        js.append("}")
        js.append("")
        js.append("function printManualLinkPlan() {")
        js.append("    if (!LINK_PLAN_ENABLED) {")
        js.append("        return;")
        js.append("    }")
        js.append("    if (!TOPOLOGY.links || !TOPOLOGY.links.length) {")
        js.append("        dprint('No link plan defined.');")
        js.append("        return;")
        js.append("    }")
        js.append("")
        js.append("    dprint('=== MANUAL LINK PLAN ===');")
        js.append("    for (var i = 0; i < TOPOLOGY.links.length; i++) {")
        js.append("        var link = TOPOLOGY.links[i];")
        js.append("        var src = link.source || link.from || 'unknown';")
        js.append("        var dst = link.target || link.to || 'unknown';")
        js.append("        dprint('• ' + src + ' -> ' + dst);")
        js.append("    }")
        js.append("    dprint('Packet Tracer has no proven addLink() API yet, so these remain manual.');")
        js.append("}")
        js.append("")
        js.append("function waitMs(ms) {")
        js.append("    var start = new Date().getTime();")
        js.append("    while ((new Date().getTime() - start) < ms) { }")
        js.append("}")
        js.append("")
        js.append("function getSafeString(obj, methodName) {")
        js.append("    try {")
        js.append("        if (obj != null && typeof obj[methodName] === 'function') {")
        js.append("            return String(obj[methodName]());")
        js.append("        }")
        js.append("    } catch (e) { }")
        js.append("    return '';")
        js.append("}")
        js.append("")
        js.append("function safeLower(value) {")
        js.append("    return String(value || '').toLowerCase();")
        js.append("}")

        return "\n".join(js)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Packet Tracer main.js from YAML/JSON/XML topology definitions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 yaml_to_mainjs.py examples/simple_topology.yaml --output main.js
  python3 yaml_to_mainjs.py examples/complex_topology.yaml --output generated_main.js --no-config
        """,
    )
    parser.add_argument("topology_file", help="Topology definition file (YAML/JSON/XML)")
    parser.add_argument(
        "--output",
        "-o",
        default="generated_main.js",
        help="Output JS file (default: generated_main.js)",
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="Only generate device spawning code; skip CLI injection",
    )
    parser.add_argument(
        "--no-link-plan",
        action="store_true",
        help="Do not print a manual link plan in the generated JS",
    )
    parser.add_argument("--start-x", type=int, default=DEFAULT_LAYOUT["start_x"])
    parser.add_argument("--start-y", type=int, default=DEFAULT_LAYOUT["start_y"])
    parser.add_argument("--spacing-x", type=int, default=DEFAULT_LAYOUT["spacing_x"])
    parser.add_argument("--spacing-y", type=int, default=DEFAULT_LAYOUT["spacing_y"])
    parser.add_argument("--columns", type=int, default=DEFAULT_LAYOUT["columns"])

    args = parser.parse_args()

    try:
        topology = parse_file(args.topology_file)
    except Exception as e:
        print(f"❌ Error loading topology file: {e}", file=sys.stderr)
        sys.exit(1)

    translator = YAMLToMainJsTranslator(
        topology,
        include_config=not args.no_config,
        include_link_plan=not args.no_link_plan,
        layout={
            "start_x": args.start_x,
            "start_y": args.start_y,
            "spacing_x": args.spacing_x,
            "spacing_y": args.spacing_y,
            "columns": args.columns,
        },
    )

    output = translator.generate()

    try:
        Path(args.output).write_text(output)
        print(f"✅ Generated Packet Tracer main.js: {args.output}")
        print(f"   Devices: {len(translator.devices)}")
        print(f"   Links: {len(translator.links)}")
        print(f"   CLI config: {'yes' if not args.no_config else 'no'}")
        print(f"   Link plan: {'yes' if not args.no_link_plan else 'no'}")
    except Exception as e:
        print(f"❌ Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
