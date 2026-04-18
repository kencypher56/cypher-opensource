import subprocess
import shutil
import os
from errorhandling import CypherError

CADDYFILE_PATH = "/etc/caddy/Caddyfile"
CADDY_SERVICE = "caddy"

def is_caddy_installed() -> bool:
    return shutil.which("caddy") is not None

def install_caddy(package_manager: str = "apt"):
    commands = {
        "apt": [
            "apt-get install -y -qq debian-keyring debian-archive-keyring apt-transport-https curl",
            "curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg",
            'curl -1sLf \'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt\' | tee /etc/apt/sources.list.d/caddy-stable.list',
            "apt-get update -qq",
            "apt-get install -y -qq caddy",
        ],
        "yum": [
            "yum install -y -q yum-plugin-copr",
            "yum copr enable -y @caddy/caddy",
            "yum install -y -q caddy",
        ],
        "dnf": [
            "dnf install -y -q 'dnf-command(copr)'",
            "dnf copr enable -y @caddy/caddy",
            "dnf install -y -q caddy",
        ],
    }

    cmds = commands.get(package_manager, commands["apt"])
    for cmd in cmds:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise CypherError(f"Caddy installation failed: {result.stderr.strip()}")

def read_caddyfile() -> str:
    if not os.path.exists(CADDYFILE_PATH):
        return ""
    with open(CADDYFILE_PATH) as f:
        return f.read()

def write_caddyfile(content: str):
    os.makedirs(os.path.dirname(CADDYFILE_PATH), exist_ok=True)
    with open(CADDYFILE_PATH, "w") as f:
        f.write(content)

def add_reverse_proxy_block(domain: str, upstream_port: int):
    existing = read_caddyfile()
    
    block = f"""
{domain} {{
    reverse_proxy localhost:{upstream_port}
    encode gzip
    header {{
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
    }}
}}
"""
    
    if domain in existing:
        lines = existing.splitlines()
        new_lines = []
        skip = False
        brace_count = 0
        for line in lines:
            if domain in line and "{" in line:
                skip = True
            if skip:
                brace_count += line.count("{") - line.count("}")
                if brace_count <= 0:
                    skip = False
                continue
            new_lines.append(line)
        existing = "\n".join(new_lines)
    
    new_content = existing.strip() + "\n" + block
    write_caddyfile(new_content)

def reload_caddy():
    result = subprocess.run(
        ["systemctl", "reload", CADDY_SERVICE],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["caddy", "reload", "--config", CADDYFILE_PATH],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise CypherError(f"Failed to reload Caddy: {result.stderr.strip()}")

def restart_caddy():
    subprocess.run(["systemctl", "restart", CADDY_SERVICE], capture_output=True)

def ensure_caddy(package_manager: str = "apt"):
    if not is_caddy_installed():
        install_caddy(package_manager)
    
    subprocess.run(["systemctl", "enable", CADDY_SERVICE], capture_output=True)
    subprocess.run(["systemctl", "start", CADDY_SERVICE], capture_output=True)

def configure_domain(domain: str, service_port: int, package_manager: str = "apt"):
    ensure_caddy(package_manager)
    add_reverse_proxy_block(domain, service_port)
    reload_caddy()