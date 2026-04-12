# SOYMSA Network Topology Files

This directory contains Cisco Packet Tracer (.pkt) files representing the various network segments and topologies for the SOYMSA enterprise infrastructure.

## Files Overview

### Core.pkt
The core backbone network segment. Size: 47 KB

### DMZ.pkt  
The original DMZ (Demilitarized Zone) topology connecting internal servers to the firewall. Size: 5.1 MB

### ReDMZ.pkt ⭐
**The revised DMZ topology** — basically the "v2" after we discovered some serious design issues with the original approach. Think of it like how Revanced came back after Vanced got nuked. 

We had to pretty much rebuild the entire DMZ configuration, routing, and NAT setup from the ground up. Packet Tracer was not happy with us for a solid afternoon, but we got there eventually. This version incorporates all the lessons learned and fixes from the first attempt.

**Size**: 98 KB  
**Status**: Production-ready (we hope 😅)  
**Last Updated**: Apr 12, 2026

## Recommended Usage

- **For simulations**: Use `ReDMZ.pkt` for the latest, debugged DMZ topology
- **For learning**: Compare `DMZ.pkt` and `ReDMZ.pkt` to see what changed
- **For the core network**: Reference `Core.pkt` for backbone configurations

## File Format

All files are Cisco Packet Tracer 9.0+ compatible topology files. Open with:
```bash
packettracer [filename].pkt
```

---

*See [GIT_GUIDE.md](./GIT_GUIDE.md) for version control practices specific to this directory.*
