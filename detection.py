import subprocess
import os
import platform
from errorhandling import CypherError

SUPPORTED_DISTROS = {
    "ubuntu": "apt",
    "debian": "apt",
    "linuxmint": "apt",
    "pop": "apt",
    "centos": "yum",
    "rhel": "yum",
    "fedora": "dnf",
    "rocky": "dnf",
    "almalinux": "dnf",
    "arch": "pacman",
    "manjaro": "pacman",
}

def detect_distro() -> dict:
    info = {
        "id": "unknown",
        "name": "Unknown",
        "version": "0",
        "package_manager": "apt",
        "is_supported": False,
    }

    if platform.system() != "Linux":
        raise CypherError("Cypher only supports Linux systems.")

    os_release_path = "/etc/os-release"
    if not os.path.exists(os_release_path):
        return info

    with open(os_release_path) as f:
        lines = f.readlines()

    release = {}
    for line in lines:
        if "=" in line:
            key, _, value = line.strip().partition("=")
            release[key] = value.strip('"')

    distro_id = release.get("ID", "").lower()
    distro_id_like = release.get("ID_LIKE", "").lower()

    info["id"] = distro_id
    info["name"] = release.get("NAME", distro_id)
    info["version"] = release.get("VERSION_ID", "0")

    for key in [distro_id] + distro_id_like.split():
        if key in SUPPORTED_DISTROS:
            info["package_manager"] = SUPPORTED_DISTROS[key]
            info["is_supported"] = True
            break

    return info

def is_root() -> bool:
    return os.geteuid() == 0

def get_architecture() -> str:
    return platform.machine()

def get_total_ram_gb() -> float:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    kb = int(line.split()[1])
                    return round(kb / 1024 / 1024, 1)
    except Exception:
        pass
    return 0.0

def get_cpu_count() -> int:
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1