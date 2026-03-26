# SOYMSA: A Networking Journey 🚀

[![Status](https://img.shields.io/badge/status-in_progress-brightgreen.svg)](https://github.com/Astro-CLI/Keystone)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Packet Tracer](https://img.shields.io/badge/Packet_Tracer-9.0.0-orange.svg)](#)

> Building a global Cloud Services infrastructure and advanced cybersecurity for **SOYMSA** — reviving a family legacy in the digital age.

---

## 📖 Table of Contents

- [The Mission](#-the-mission)
- [The Backstory](#-the-backstory)
- [Project Overview](#-project-overview)
- [About SOYMSA](#-about-soymsa)
- [What We Do](#-what-we-do)
- [Why Choose Us?](#-why-choose-us)
- [Branch Deployment & Network Architecture](#-branch-deployment--network-architecture)
- [The Global Internet Backbone (WAN Core)](#-the-global-internet-backbone-wan-core)
- [Network Automation](#-network-automation)
- [The Goal: A Living Network Log](#-the-goal-a-living-network-log)
- [The Game Plan](#-the-game-plan)
- [Repository Structure](#-repository-structure)
- [My Rules of Engagement](#-my-rules-of-engagement)
- [How to Follow Along](#-how-to-follow-along)
- [License & Attribution](#-license--attribution)
- [Shoutouts](#-shoutouts)

---

## 🔮 The Mission

Welcome to the reboot of **SOYMSA** (*Sistemas, Organización y Métodos, Sociedad Anónima*).

This repo is where I'm building a full-scale enterprise network from the ground up — simulating a real global Cloud Services provider. It's for a college course, but it's also a personal challenge. This isn't a finished product; it's the live log of a network's birth and evolution. Every commit is a step forward, a lesson learned, or a problem solved.

The end goal? To have a killer project for my portfolio, and maybe create a resource that other students can actually use.

---

## 📜 The Backstory

This isn't just a random project. SOYMSA was a real company started by my grandfather back in the day — before the Windows era. He was building custom organizational and management systems for businesses before the big names took over. When the tech world changed, SOYMSA faded out.

This project is my way of paying tribute to that legacy. I'm bringing the name back for a new, fictionalized SOYMSA, transformed from a traditional consulting firm into a cutting-edge cloud technology company. I'm applying his principles of order and organization inside the routing tables and code of modern internet networks. It's about connecting the past with the future.

---

## 📋 Project Overview

This project presents a comprehensive simulation of the SOYMSA corporate network using **Cisco Packet Tracer**. The network design is built on a resilient architecture spanning three geographically separate branches, connected to the global internet backbone (WAN Core) through three authentic ISPs:

- **Movistar** (AS10834)
- **Cellcom** (AS1680)
- **AT&T** (AS7018)

Inter-branch connectivity is based on the **eBGP** routing protocol, ensuring optimal routing and full redundancy in the event of an ISP failure. Within each branch, Cisco's **three-layer hierarchical model** (Access, Distribution, Core) is implemented for efficient traffic management and scalability.

Security is a top priority. At the organization's perimeter sits a **Cisco ASA 5506-X** firewall, acting as the critical buffer between:
- The secure internal network (Inside)
- The cloud services zone (DMZ)
- The public internet (Outside)

The ASA handles advanced NAT — **Static NAT** for servers and **PAT (NAT Overload)** for end users — and enforces strict Object Group-based **ACL** policies. Core services including **DNS, Web, FTP, and VPN** servers are carefully managed to deliver a stable, fast, and protected communication experience for all end users and clients.

---

## 🏢 About SOYMSA

### Who We Are

**SOYMSA** (*Sistemas, Organización y Métodos, Sociedad Anónima*) is a global Cloud Services and cybersecurity provider that builds and manages critical communication infrastructures for international organizations. The company blends deep organizational experience with next-generation Networking and Cyber technologies.

### A Brief History

The company was originally founded by my grandfather before the Windows era, specializing in organizational systems, order, and management methodologies (hence the name: "Systems, Organization and Methods"). In 2025, as part of my final project, I decided to revive the family brand and perform a **full digital transformation** — turning SOYMSA from a traditional consulting firm into an advanced cloud technology company that embeds his principles of order and structure into the routing and code of modern internet networks.

### Vision & Values

SOYMSA's vision is to serve as the technological backbone for its clients, ensuring **Business Continuity** and maximum availability of **99.99% uptime**.

**Our core values:**
- **Legacy of Excellence** — building on proven organizational foundations
- **Technological Innovation** — embracing cutting-edge protocols and tools
- **Uncompromising Security** — rigorous protection across all layers of data
- **Full Redundancy** — no single point of failure at any layer of the network

### Expertise

SOYMSA specializes in building complex WAN networks based on BGP and direct connectivity to the global internet backbone. Our areas of expertise include:
- Managing server farms and Data Centers
- Deploying advanced firewalls (Cisco ASA)
- Traffic optimization through hierarchical routing
- Dual-stack IPv4 / IPv6 environments

### The Team

The SOYMSA professional team is composed of specialists in network engineering, cybersecurity, and automation, combining extensive theoretical knowledge with the ability to execute complex, production-grade simulations.

---

## 🛠️ What We Do

### Products & Services

- **Secure File Hosting & Transfer:** FTP and TFTP servers enable encrypted backup and data transfer.
- **Centralized Identity Management (AAA):** Strict authentication and authorization for all employees and clients.
- **Distributed Cloud Infrastructure:** DNS and Web services delivered to clients through a secured, NAT-translated DMZ zone.
- **Secure Connectivity:** Site-to-Site VPN tunnels for encrypted communication between branches and cloud providers.

### Value Proposition

SOYMSA delivers global stability across three countries (Israel, Argentina, and the United States), leveraging real-world ISPs like Movistar, Cellcom, and AT&T to simulate authentic internet peering.

### Our Clients

- **Multinational corporations** requiring reliable global communication infrastructure
- **Startups** needing resilient cloud services
- **Government entities** requiring strict network segmentation and Perimeter Security

---

## 🏆 Why Choose Us?

### Competitive Advantages

- **Dual Redundancy:** HSRP at Layer 3 and STP/EtherChannel at Layer 2 to prevent network downtime.
- **Multi-Layer Cyber Defense:** ASA Firewall, Port Security, and DHCP Snooping to block common attacks.
- **Routing Innovation:** OSPF Multi-Area with Virtual Links to connect geographically dispersed zones.

### Achievements

- Built a full-scale Cisco Packet Tracer simulation covering complete business operations across three branches.
- Successfully implemented BGP inter-continental routing between branches.
- Created internal Email Server infrastructure and HTML-designed internal web portals.

### Our Promise

SOYMSA is committed to intelligent network management, the highest level of information security, and technical support that honors the professional legacy of the past while looking toward the digital future.

---

## 🗺️ Branch Deployment & Network Architecture

The network is designed around **Cisco's three-layer hierarchical model**:

| Layer | Name | Role |
|---|---|---|
| **Core** | Core Layer | High-speed backbone connecting branches; exits to the WAN via BGP |
| **Distribution** | Distribution Layer | Inter-VLAN routing, HSRP redundancy, and ACL traffic filtering |
| **Access** | Access Layer | Connects end users, printers, and wireless APs with Port Security enforcement |

### Our Three Branches

- 🇦🇷 **Buenos Aires** — Headquarters and primary server farm.
- 🇮🇱 **Netanya** — Cloud management branch, IP addressing based on VLSM.
- 🇺🇸 **Frisco, Texas** — R&D branch, built entirely on IPv6 addressing.

---

## 🌐 The Global Internet Backbone (WAN Core)

### ISP Core Routers

| ISP / Router | AS Number | Core Router IP |
|---|---|---|
| **Telefónica de Argentina (Movistar)** | AS10834 | 200.0.224.1 |
| **Cellcom Fixed Line Comm.** | AS1680 | 82.166.0.1 |
| **AT&T Enterprises, LLC** | AS7018 | 70.244.0.1 |

> * IPs are derived from real allocated ranges: Telefónica (200.0.224.0/24), Cellcom (82.166.0.0/16), AT&T (70.244.0.0/14).

### eBGP Inter-Carrier Peering Table (Loopback Method)

| Router (AS) | Interface | Local IP | Core Network (Loopback 0 /32) | Peer IP / Remote AS |
|---|---|---|---|---|
| **Movistar (AS10834)** | Loopback 0 | — | 200.0.224.1 | (Advertised Network) |
| | Gi0/0 (To Cellcom) | 10.1.1.5 | — | 10.1.1.6 / AS1680 |
| | Gi0/1 (To AT&T) | 10.1.1.9 | — | 10.1.1.10 / AS7018 |
| **Cellcom (AS1680)** | Loopback 0 | — | 82.166.0.1 | (Advertised Network) |
| | Gi0/0 (To Movistar) | 10.1.1.6 | — | 10.1.1.5 / AS10834 |
| | Gi0/1 (To AT&T) | 10.1.1.1 | — | 10.1.1.2 / AS7018 |
| **AT&T (AS7018)** | Loopback 0 | — | 70.244.0.1 | (Advertised Network) |
| | Gi0/0 (To Movistar) | 10.1.1.10 | — | 10.1.1.9 / AS10834 |
| | Gi0/1 (To Cellcom) | 10.1.1.2 | — | 10.1.1.1 / AS1680 |

> * This configuration uses Loopback interfaces for BGP stability and core network representation, following standard best practices for carrier simulations.

---

## ⚙️ Network Automation

In the era of **Software-Defined Networking (SDN)**, automation is an inseparable part of modern network and security management — and Cisco Packet Tracer makes it practical to implement.

Rather than manually configuring routers, switches, and firewalls (like the ASA) through individual CLI sessions, end-station computers or servers in the simulation can run **Python scripts**. Using **Object-Oriented Programming (OOP)** principles, these scripts create logical objects representing network devices, interfaces, BGP routes, and ACL rules.

The script packages data from those objects into standard formats like **JSON** and pushes them via **REST API** calls to a central Network Controller. This approach enables:
- **Automated Provisioning** — deploy complex configurations across dozens of devices in parallel
- **Infrastructure as Code** — network management becomes modular and reproducible
- **Reduced Human Error** — no more typos from manual CLI configuration

---

## 🕰️ The Goal: A Living Network Log

Think of this repo as a time machine. Every commit is a snapshot. I'm documenting my entire thought process here, not just the final result.

- Why did I pick this IP schema?
- What's the logic behind my routing protocol choices?
- How am I building the security posture, and what trade-offs am I making?

I'm building the resource I wish I had: a transparent, no-BS guide written by a student, for students. You can grab any `.pkt` file from the history, see the network at that stage, and understand why it was built that way.

---

## 🗂️ The Game Plan

The project grows in stages. Each major milestone gets its own Packet Tracer (`.pkt`) file. The naming is chronological, so you can follow the evolution. Each new file contains everything from the previous one, plus the new stuff.

It's like leveling up:
1. **`Core.pkt`** — The starting zone: ISP backbone, BGP peering, core routing.
2. **`DMZ.pkt`** — Level 2: Add the ASA firewall, DMZ, and NAT.
3. **`Distribution.pkt`** *(Future)* — Distribution layer, HSRP, Inter-VLAN routing.
4. **`Access.pkt`** *(Future)* — Access layer, VLANs, Port Security, wireless.
5. ...and so on. More levels added as I go.

This structure is the key. It lets you walk through the entire network's history, one commit at a time.

---

## 📂 Repository Structure

| Path | Contents |
|---|---|
| `/` | `README.md`, `LICENSE`, and top-level repository configuration |
| `SOYMSA/` | All Cisco Packet Tracer (`.pkt`) files representing different stages of the network |
| `Documentation/` | Detailed network topology, IP schemas, security policies, and diagrams |

---

## 🧭 My Rules of Engagement

Every decision here is deliberate. The "why" is just as important as the "how."

- **Transparent Commits:** Every `git commit` tells a story. `git log` is the project's chronicle. I'm explaining my moves, my reasoning, and my mistakes.
- **Real Documentation:** As things get more complex, I'll add detailed notes on security policies, IP schemas, VLANs, and anything else that needs explaining. No black boxes.

---

## 🤝 How to Follow Along

This is my academic journey, but I'm running it like an open-source project. Feel free to tag along.

- **Watch the repo:** Get notified when I push new changes.
- **Fork it:** Clone the repo and build your own version of SOYMSA. Experiment, break things, make it your own.
- **Open an issue:** Got a question or a suggestion? Hit me up in the issues. Let's talk shop.

---

## 📜 License & Attribution

This project is under the **Apache License 2.0**. The full license is in the `LICENSE` file.

You're free to use, modify, and share this work. But since I'm a student building this for my education, I'd personally appreciate it if you **cite this repo as a source** if you use it for your own school projects. It's not a legal thing, just a friendly request. Thanks.

---

## 🙏 Shoutouts

- To my grandfather, for the original SOYMSA story.
- To my professors and classmates, for the guidance and feedback.
- To the open-source world, for teaching me that sharing knowledge is the best way to learn.

---

Made with ❤️ and a lot of packets.
