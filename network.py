import socket
import re
import subprocess
from errorhandling import NetworkError

RESERVED_PORTS = {22, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995}

def is_port_in_use(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False

def find_available_port(preferred: int, max_attempts: int = 20) -> int:
    port = preferred
    for _ in range(max_attempts):
        if not is_port_in_use(port) and port not in RESERVED_PORTS:
            return port
        port += 1
    raise NetworkError(f"No available port found near {preferred}.")

def validate_domain(domain: str) -> bool:
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain))

def validate_ip(ip: str) -> bool:
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    parts = ip.split(".")
    return all(0 <= int(p) <= 255 for p in parts)

def validate_host(host: str) -> bool:
    return validate_domain(host) or validate_ip(host)

def is_domain(host: str) -> bool:
    return validate_domain(host)

def ensure_docker_network(network_name: str = "cypher_net"):
    result = subprocess.run(
        ["docker", "network", "ls", "--format", "{{.Name}}"],
        capture_output=True, text=True
    )
    if network_name not in result.stdout.split():
        subprocess.run(
            ["docker", "network", "create", network_name],
            capture_output=True
        )
    return network_name

def get_used_ports() -> set:
    used = set()
    try:
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines()[1:]:
            parts = line.split()
            if len(parts) >= 4:
                addr = parts[3]
                if ":" in addr:
                    try:
                        port = int(addr.rsplit(":", 1)[-1])
                        used.add(port)
                    except ValueError:
                        pass
    except Exception:
        pass
    return used