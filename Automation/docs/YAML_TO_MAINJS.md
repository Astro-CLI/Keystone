# YAML to `main.js` Translator

This workflow turns a topology definition into a Packet Tracer script you can paste directly into **Extensions → Scripting → Edit File Script Module**.

## What it does

The translator generates a self-contained `main.js` that:

1. reads the topology definition at generation time
2. embeds that data into JavaScript
3. duplicates seed devices already present on the Packet Tracer canvas
4. positions the new devices
5. injects CLI configuration commands when enabled
6. prints a manual link plan for any links in the topology

It is the bridge between:

- **Option C**: spawning devices inside Packet Tracer
- **Option A**: applying CLI configuration automatically

## What it does not do

- It does **not** create links automatically.
- It does **not** invent device templates that do not exist on the canvas.
- It does **not** rename devices reliably, because `setName()` is still broken in tested PT builds.

## Generator

Use:

```bash
python3 tools/yaml_to_mainjs.py examples/simple_topology.yaml --output generated_main.js
```

Default behavior:

- spawns devices
- injects CLI configs
- prints a link plan

Optional flags:

| Flag | Meaning |
|---|---|
| `--no-config` | Spawn devices only |
| `--no-link-plan` | Omit manual link instructions |
| `--start-x` | Starting X position |
| `--start-y` | Starting Y position |
| `--spacing-x` | Horizontal spacing |
| `--spacing-y` | Vertical spacing |
| `--columns` | Grid width for auto-layout |

## Required Packet Tracer setup

Before running the generated `main.js`, place at least one seed device for each device family you want to create.

Examples:

- one router seed for routers
- one switch seed for switches
- one server seed for servers
- one PC seed for PCs

The script searches the initial canvas for a matching template by model/name hints and duplicates that device.

## How device creation works

The generated script uses the proven runtime flow:

```javascript
var appWindow = ipc.appWindow();
var activeFile = appWindow.getActiveFile();
var network = ipc.network();
var template = network.getDeviceAt(0);

activeFile.duplicateDevice(template);
var device = network.getDeviceAt(network.getDeviceCount() - 1);
device.moveToLocationCentered(100, 100);
```

That is the only confirmed spawn path in current testing.

## How configuration works

For each device, the translator embeds the CLI commands produced by `TopologyComposer`.

The generated `main.js`:

1. finds the device’s CLI
2. detects the initial setup dialog if it appears
3. sends the commands one by one
4. waits briefly between commands

## Example workflow

1. Write your topology in YAML.
2. Run `yaml_to_mainjs.py`.
3. Open Packet Tracer with a blank canvas that already contains the seed devices.
4. Paste the generated JS into the script editor.
5. Run it.
6. Manually wire links if your topology includes them.

## Relation to the other tools

- `pt_config_parser.py` extracts configs into YAML/JSON/XML.
- `topology_composer.py` converts topology data into CLI commands.
- `yaml_to_mainjs.py` converts topology data into runnable Packet Tracer JavaScript.
- `pt_yaml_exporter.js` prints live Packet Tracer topology as YAML in the debug console.

That gives you a full loop:

`extract -> edit -> generate CLI -> generate main.js -> run in Packet Tracer`
