import subprocess
import os
import shutil
from detection import detect_distro
from errorhandling import DockerError

DOCKER_INSTALL_SCRIPTS = {
    "apt": [
        "apt-get update -qq",
        "apt-get install -y -qq ca-certificates curl gnupg lsb-release",
        "install -m 0755 -d /etc/apt/keyrings",
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg",
        "chmod a+r /etc/apt/keyrings/docker.gpg",
        'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] '
        'https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | '
        'tee /etc/apt/sources.list.d/docker.list > /dev/null',
        "apt-get update -qq",
        "apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
    ],
    "yum": [
        "yum install -y -q yum-utils",
        "yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo",
        "yum install -y -q docker-ce docker-ce-cli containerd.io docker-compose-plugin",
        "systemctl start docker",
        "systemctl enable docker",
    ],
    "dnf": [
        "dnf install -y -q dnf-plugins-core",
        "dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo",
        "dnf install -y -q docker-ce docker-ce-cli containerd.io docker-compose-plugin",
        "systemctl start docker",
        "systemctl enable docker",
    ],
}

def is_docker_installed() -> bool:
    return shutil.which("docker") is not None

def is_docker_compose_available() -> bool:
    result = subprocess.run(
        ["docker", "compose", "version"],
        capture_output=True
    )
    return result.returncode == 0

def install_docker():
    distro = detect_distro()
    pm = distro.get("package_manager", "apt")
    commands = DOCKER_INSTALL_SCRIPTS.get(pm)
    
    if not commands:
        raise DockerError(f"Automatic Docker installation not supported for '{pm}' package manager.")
    
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise DockerError(f"Docker installation failed: {result.stderr.strip()}")

def ensure_docker():
    if not is_docker_installed():
        install_docker()
    
    if not is_docker_compose_available():
        raise DockerError("Docker Compose plugin not available. Please install docker-compose-plugin.")
    
    result = subprocess.run(["docker", "info"], capture_output=True)
    if result.returncode != 0:
        subprocess.run(["systemctl", "start", "docker"], capture_output=True)
        result = subprocess.run(["docker", "info"], capture_output=True)
        if result.returncode != 0:
            raise DockerError("Docker daemon is not running and could not be started.")

def deploy_compose(compose_path: str, project_name: str):
    compose_dir = os.path.dirname(compose_path)
    result = subprocess.run(
        ["docker", "compose", "-p", project_name, "up", "-d", "--remove-orphans"],
        cwd=compose_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise DockerError(f"Docker Compose deployment failed:\n{result.stderr.strip()}")

def stop_compose(compose_path: str, project_name: str):
    compose_dir = os.path.dirname(compose_path)
    subprocess.run(
        ["docker", "compose", "-p", project_name, "down"],
        cwd=compose_dir,
        capture_output=True
    )

def pull_images(compose_path: str):
    compose_dir = os.path.dirname(compose_path)
    subprocess.run(
        ["docker", "compose", "pull"],
        cwd=compose_dir,
        capture_output=True
    )

def is_container_running(container_name: str) -> bool:
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True, text=True
    )
    return container_name in result.stdout.split()

def get_compose_dir(service: str) -> str:
    base = os.path.expanduser(f"~/.cypher/{service}")
    os.makedirs(base, exist_ok=True)
    return base