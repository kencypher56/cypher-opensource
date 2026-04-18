import subprocess
import time
from docker import get_compose_dir, deploy_compose, pull_images, is_container_running
from composing import write_compose_file
from network import ensure_docker_network
from errorhandling import ServiceError

SERVICE_CONTAINERS = {
    "n8n": "cypher_n8n",
    "supabase": "cypher_supabase_studio",
    "kong": "cypher_kong",
    "mailcow": "cypher_mailcow_nginx",
    "mattermost": "cypher_mattermost",
    "jenkins": "cypher_jenkins",
    "gitea": "cypher_gitea",
    "gitlab": "cypher_gitlab",
    "jitsi": "cypher_jitsi_web",
    "openproject": "cypher_openproject",
}

HEAVY_SERVICES = {"gitlab", "supabase", "jitsi"}

MATTERMOST_PLUGINS = [
    "com.mattermost.calls",
    "com.mattermost.nps",
    "playbooks",
]

def deploy_service(service: str, config: dict, on_step=None):
    def step(msg):
        if on_step:
            on_step(msg)

    step("Setting up Docker network...")
    ensure_docker_network()

    step("Generating service configuration...")
    compose_dir = get_compose_dir(service)
    compose_path = write_compose_file(service, config, compose_dir)

    step("Pulling Docker images...")
    pull_images(compose_path)

    step(f"Deploying {service}...")
    deploy_compose(compose_path, f"cypher_{service}")

    step("Waiting for service to start...")
    _wait_for_container(service, timeout=60)

    if service == "mattermost":
        step("Installing Mattermost plugins...")
        _install_mattermost_plugins()

    step("Finalizing setup...")
    return compose_path

def _wait_for_container(service: str, timeout: int = 60):
    container = SERVICE_CONTAINERS.get(service)
    if not container:
        return
    
    start = time.time()
    while time.time() - start < timeout:
        if is_container_running(container):
            return
        time.sleep(3)

def _install_mattermost_plugins():
    time.sleep(10)
    for plugin in MATTERMOST_PLUGINS:
        subprocess.run(
            ["docker", "exec", "cypher_mattermost",
             "/mattermost/bin/mmctl", "plugin", "install-url",
             f"https://plugins.mattermost.com/{plugin}/latest"],
            capture_output=True
        )

def get_service_warnings(service: str) -> list:
    warnings = []
    
    if service == "gitlab":
        warnings.append("GitLab requires at least 4GB RAM and 2 CPU cores.")
        warnings.append("Initial startup may take 3-5 minutes.")
        warnings.append("First login: use 'root' and password from docker logs.")
    
    if service == "mailcow":
        warnings.append("Mailcow requires ports 25, 143, 465, 587, 993, 995.")
        warnings.append("Ensure your server's DNS MX record points to this host.")
        warnings.append("Port 25 must not be blocked by your hosting provider.")
    
    if service == "jitsi":
        warnings.append("Jitsi requires UDP port 10000 for media traffic.")
        warnings.append("For best performance, ensure the server has a public IP.")
    
    if service == "supabase":
        warnings.append("Supabase deploys multiple containers (DB, Auth, REST, Studio).")
        warnings.append("Initial startup may take 2-3 minutes.")
    
    return warnings