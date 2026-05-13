# Packet Tracer YAML Exporter

This is the live Packet Tracer-side exporter.

Paste the script into Packet Tracer as `main.js`, run it against an open `.pkt`,
and copy the YAML from the debug console into a `.yaml` file.

## What it captures

- device names
- device types and models
- positions
- ports
- running config blocks where available
- best-effort connection hints

## Why this is the right workflow

For raw Packet Tracer files, the topology already exists in PT.
You do not need a separate Python translator if the script itself prints YAML.

## Usage

1. Open the desired `.pkt`
2. Paste `scripts/pt_yaml_exporter.js` into the Packet Tracer script editor
3. Run it
4. Copy the YAML output from the debug console
5. Save it as `topology.yaml`

## Notes

- This exporter is read-only.
- It does not change the topology.
- If a device has CLI access, its running config is included as a YAML block.
- If the link API is partially exposed, the exporter prints connection hints rather than guessing.

