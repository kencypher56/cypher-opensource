<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Cinzel+Decorative&size=13&duration=3000&pause=1000&color=8B0000&center=true&vCenter=true&width=700&lines=Every+hunter+needs+their+arsenal.;Every+server+needs+its+keeper.;This+is+the+Colt.+This+kills+anything." alt="Typing SVG" />

<br/>

```
██████╗██╗   ██╗██████╗ ██╗  ██╗███████╗██████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██║  ██║██╔════╝██╔══██╗
██║      ╚████╔╝ ██████╔╝███████║█████╗  ██████╔╝
██║       ╚██╔╝  ██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗
╚██████╗   ██║   ██║     ██║  ██║███████╗██║  ██║
 ╚═════╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

<h3><em>"I know what I'm doing. I'm a professional."</em><br/><sup>— Dean Winchester, probably about his server setup</sup></h3>

<br/>

[![Made with Python](https://img.shields.io/badge/Python-3.10+-8B0000?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Required-2C2C2C?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Linux](https://img.shields.io/badge/Linux-Only-1a1a1a?style=for-the-badge&logo=linux&logoColor=white)](https://kernel.org)
[![Made by kencypher](https://img.shields.io/badge/Made_by-kencypher-8B0000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/kencypher)

<br/>

> *"Saving people. Deploying services. The family business."*

</div>

---

<div align="center">
<h2>🕯️ &nbsp; What Darkness Dwells Here &nbsp; 🕯️</h2>
</div>

**Cypher** is a Python 3.10 CLI automation tool that deploys and manages popular open-source services on Linux servers using Docker — in one place, with one command, like a hunter who knows exactly which sigil to draw.

No YAML hell. No tab-hunting across 14 browser windows. No duct-taped shell scripts held together by prayers and caffeine.

You run it. It asks you a few questions. Then it handles everything — Docker, networking, ports, volumes, HTTPS, reverse proxy — while you sit back and drink your terrible gas station coffee.

> *The same reason Sam and Dean keep everything in the Impala's trunk — because when something shows up at 2 AM, you don't want to be running to three different stores. Everything you need, one place.*

---

<div align="center">
<h2>💀 &nbsp; The Arsenal (Supported Services) &nbsp; 💀</h2>
</div>

| # | Service | What it does |
|---|---------|-------------|
| `01` | **n8n** | Workflow automation — your Bobby Singer, connecting everything |
| `02` | **Supabase** | Open-source Firebase — the full stack, no deals with demons |
| `03` | **Kong** | API Gateway — the Devil's Trap for your traffic |
| `04` | **Mailcow** | Full email server suite — old-fashioned, reliable, iron-warded |
| `05` | **Mattermost** | Team messaging with auto-plugin install — bunker comms |
| `06` | **Jenkins** | CI/CD pipelines — the ritual that runs itself |
| `07` | **Gitea** | Lightweight Git — a personal archive of every sigil you've ever drawn |
| `08` | **GitLab** | Full DevOps platform — heavy. Like the Impala. Worth it. |
| `09` | **Jitsi** | Self-hosted video conferencing — no wiretapping, no demons listening |
| `10` | **OpenProject** | Project management — every hunt needs a board |

---

<div align="center">
<h2>🩸 &nbsp; Why This Was Built &nbsp; 🩸</h2>
</div>

The same nightmare played out every single time.

You need to spin up a service. So you open the docs. Then a Docker Hub page. Then a StackOverflow answer from 2019. Then a blog post that's half-wrong. Then you're editing compose files by hand, guessing port numbers, wondering if 8080 is already taken, setting up Nginx config that you'll forget the syntax of by next week.

**That's not hunting. That's being the monster.**

**Cypher exists because everything should live in one place.**

One tool. One flow. You pick your service, answer three questions, and it's running — with persistent volumes, proper networking, secure secrets, and if you're using a domain, automatic HTTPS through Caddy.

No 14-tab setup. No half-finished tutorials. No shell scripts written at 3 AM that you find six months later and can't read.

> *Dean didn't carry seventeen different cars. He had one. He knew every inch of it.*

---

<div align="center">
<h2>🔱 &nbsp; Why Caddy (Not Nginx) &nbsp; 🔱</h2>
</div>

Because Nginx config files are written in a language only angels can read, and even they get it wrong sometimes.

**Caddy was chosen deliberately:**

- **Automatic HTTPS** — you give it a domain, it handles TLS certificates via Let's Encrypt. Zero configuration. Zero renewal crons. It just works.
- **Zero ceremony** — the Caddyfile format is human. It reads like you wrote it on a napkin and it still works.
- **Dynamic reload** — Cypher adds new services to the Caddyfile and reloads Caddy live, no restarts, no downtime.
- **One less thing to maintain** — because every piece of infrastructure you don't have to babysit is a demon that didn't get back up.

> *"Work smarter." — Castiel, probably, if he'd ever had to configure a reverse proxy*

---

<div align="center">
<h2>⚡ &nbsp; Features That Matter &nbsp; ⚡</h2>
</div>

```
🖥️  OS Detection          Reads /etc/os-release. Ubuntu, Debian, CentOS, Fedora, Arch.
                          Adapts package manager automatically. No guessing.

💬  Clean CLI             No raw Docker logs. No scrolling walls of text.
                          Step messages. Success/failure. That's it.

🐳  Docker Management     Installs Docker if missing. Creates shared network.
                          Runs everything detached. Manages volumes.

📄  Compose Generation    You never write a compose file.
                          Cypher generates it — ports, volumes, envs, secrets, all of it.

🌐  Port Intelligence     Scans what's in use. Suggests alternatives automatically.
                          No conflicts. No "address already in use" at midnight.

🔐  HTTPS via Caddy       Domain detected → Caddy installed → TLS configured → done.
                          One flow. Automatic certificates.

⚠️  Error Handling        Ctrl+C? Caught. Port conflict? Handled. Docker down? Told clearly.
                          Centralized. Clean. No stack traces dumped on you.
```

---

<div align="center">
<h2>🗡️ &nbsp; Project Structure &nbsp; 🗡️</h2>
</div>

```
cypher-opensource/
│
├── main.py           ← Entry point. Loads the Impala. Fires the engine.
├── cli.py            ← Every color, spinner, banner, and prompt you see.
├── interactive.py    ← The hunt flow. Questions → config → deployment.
├── services.py       ← Service logic. Mattermost plugins. GitLab warnings. Orchestration.
├── detection.py      ← Reads the room. Distro, RAM, CPU, root access.
├── caddy.py          ← Caddy install, Caddyfile management, domain routing.
├── docker.py         ← Docker install, compose deploy, container control.
├── network.py        ← Port scanning, conflict detection, IP/domain validation.
├── composing.py      ← Generates every Docker Compose file for every service.
├── errorhandling.py  ← Custom exceptions, SIGINT handler, the panic room.
└── requirements.txt  ← One dependency. Barely even counts.
```

> *Every item in Bobby's salvage yard had a purpose. Nothing wasted. Nothing missing.*

---

<div align="center">
<h2>🕸️ &nbsp; How to Use It &nbsp; 🕸️</h2>
</div>

**Requirements before you start the ritual:**
- Linux server (Ubuntu, Debian, CentOS, Fedora, Arch — all recognized)
- Python 3.10+
- Root or sudo access
- A working internet connection

<br/>

**Step 1 — Clone the repository**

```bash
git clone https://github.com/kencypher/cypher-opensource.git
cd cypher-opensource
```

**Step 2 — Install the single dependency**

```bash
pip install -r requirements.txt
```

**Step 3 — Run it**

```bash
sudo python3 main.py
```

<br/>

**What happens next:**

```
  → System Check
    ✔  Detected: Ubuntu 22.04
    ℹ  Resources: 8.0GB RAM  |  4 CPU cores
    ✔  Docker is ready

  ▸ Select a Service

     1.  n8n — Workflow Automation
     2.  Supabase — Open Source Firebase
     3.  Kong — API Gateway
    ...

  ? Enter service number: 1

  ? Domain or IP address [localhost]: myserver.com
  ? Port [5678]:
  ? Connection type
    ▸ 1. HTTPS (recommended, auto TLS via Caddy)
      2. HTTP only

  ▸ Deployment

    ✔  Setting up Docker network...
    ✔  Generating service configuration...
    ✔  Pulling Docker images...
    ✔  Deploying n8n...
    ✔  Waiting for service to start...
    ✔  Configuring Caddy reverse proxy...
    ✔  Finalizing setup...

  ╔══════════════════════════════════════════════════╗
  ║              ✅  Setup Complete!                 ║
  ╚══════════════════════════════════════════════════╝

  Service:    N8N
  Access at:  https://myserver.com
```

---

<div align="center">
<h2>🌑 &nbsp; Service-Specific Knowledge &nbsp; 🌑</h2>
</div>

Some creatures need special preparation. Cypher knows this.

| Service | Special Handling |
|---------|-----------------|
| **Mattermost** | Automatically installs Calls, NPS, and Playbooks plugins after deploy |
| **GitLab** | Warns about 4GB RAM minimum. Notes 3–5 min startup time. |
| **Mailcow** | Warns about ports 25/143/465/587/993/995. DNS MX record notice. |
| **Jitsi** | Opens UDP 10000 for media. Warns about public IP requirement. |
| **Supabase** | Full stack — DB + Auth + REST + Studio + Meta all orchestrated together |
| **Kong** | Deploys with separate migration container, admin API on adjacent port |

---

<div align="center">
<h2>🔥 &nbsp; The Philosophy &nbsp; 🔥</h2>
</div>

<table>
<tr>
<td width="50%">

**What Cypher is NOT:**
- A hosting panel
- A SaaS product
- A managed service
- Something that phones home
- Something that hides what it's doing

</td>
<td width="50%">

**What Cypher IS:**
- A local CLI tool
- Runs entirely on your machine
- Generates readable compose files in `~/.cypher/`
- Open source, always
- Yours

</td>
</tr>
</table>

> *The Winchesters never trusted someone else to guard the door. Neither should you.*

---

<div align="center">
<h2>📖 &nbsp; The Compose Files &nbsp; 📖</h2>
</div>

Every deployed service saves its generated `docker-compose.yml` to:

```
~/.cypher/<service>/docker-compose.yml
```

You can inspect it, edit it, version-control it, and manage containers with standard Docker commands at any time. Cypher generates it — you own it.

```bash
# View running containers
docker ps

# Stop a service
docker compose -p cypher_n8n down

# View logs (if you actually want them)
docker logs cypher_n8n
```

---

<div align="center">

<br/>

---

*Built with the kind of horror that comes from doing things the hard way too many times.*

<br/>

<img src="https://readme-typing-svg.demolab.com?font=Cinzel&size=14&duration=4000&pause=2000&color=8B0000&center=true&vCenter=true&width=600&lines=Made+by+kencypher;With+horror.;Saving+servers.+Deploying+services.;The+family+business." alt="footer" />

<br/>

**`kencypher`** — *because every hunter needs a handle*

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-kencypher-8B0000?style=flat-square&logo=github&logoColor=white)](https://github.com/kencypher)

<br/><br/>

<sup><em>"Driver picks the music. Passenger shuts his laptop and lets the deployment finish."</em></sup>

---

<sub>No angels were harmed in the making of this tool. Several demons were.</sub>

</div>
