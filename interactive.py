import sys
from cli import (
    print_service_menu, print_section, print_step, print_success,
    print_warning, print_error, print_info, print_completion, print_divider,
    prompt, prompt_choice, prompt_confirm, spinner, SERVICES_DISPLAY
)
from detection import detect_distro, is_root, get_total_ram_gb, get_cpu_count
from network import (
    validate_host, is_domain, find_available_port, is_port_in_use, get_used_ports
)
from docker import ensure_docker
from services import deploy_service, get_service_warnings
from caddy import configure_domain
from errorhandling import CypherError, DockerError

SERVICE_DEFAULT_PORTS = {
    "n8n": 5678,
    "supabase": 8000,
    "kong": 8080,
    "mailcow": 443,
    "mattermost": 8065,
    "jenkins": 8090,
    "gitea": 3000,
    "gitlab": 8929,
    "jitsi": 8443,
    "openproject": 8070,
}

def run_interactive_flow():
    _check_system()
    service = _select_service()
    use_defaults = _ask_defaults()
    
    if use_defaults:
        config = _build_default_config(service)
    else:
        config = _build_custom_config(service)
    
    _show_warnings(service)
    _confirm_deploy(service, config)
    _run_deployment(service, config)

def _check_system():
    print_section("System Check")
    
    distro = detect_distro()
    if not distro["is_supported"]:
        raise CypherError(f"Unsupported Linux distribution: {distro['name']}")
    
    print_success(f"Detected: {distro['name']} {distro['version']}")
    
    ram = get_total_ram_gb()
    cpus = get_cpu_count()
    print_info(f"Resources: {ram}GB RAM  |  {cpus} CPU cores")
    
    if not is_root():
        print_warning("Not running as root. Some operations may require sudo.")
    
    print_step("Checking Docker...")
    try:
        ensure_docker()
        print_success("Docker is ready")
    except DockerError as e:
        raise CypherError(f"Docker setup failed: {e}")

def _select_service() -> str:
    print_section("Select a Service")
    print_service_menu()
    
    services = list(SERVICES_DISPLAY.keys())
    
    try:
        raw = input(f"  \033[96m?\033[0m  \033[97mEnter service number\033[0m: ").strip()
        choice = int(raw)
        if 1 <= choice <= len(services):
            service = services[choice - 1]
            print_success(f"Selected: {SERVICES_DISPLAY[service]}")
            return service
    except (ValueError, EOFError):
        pass
    
    raise CypherError("Invalid service selection.")

def _ask_defaults() -> bool:
    print()
    return prompt_confirm("Use default configuration?", default=False)

def _build_default_config(service: str) -> dict:
    default_port = SERVICE_DEFAULT_PORTS.get(service, 8080)
    port = find_available_port(default_port)
    
    config = {
        "host": "localhost",
        "port": port,
        "protocol": "http",
        "use_caddy": False,
    }
    
    if service == "gitea":
        config["ssh_port"] = find_available_port(2222)
    elif service == "gitlab":
        config["ssh_port"] = find_available_port(2224)
    elif service == "kong":
        config["admin_port"] = find_available_port(port + 1)
    elif service == "jenkins":
        config["agent_port"] = find_available_port(50000)
    
    return config

def _build_custom_config(service: str) -> dict:
    print_section("Configure Service")
    config = {}
    
    host = prompt("Domain or IP address", default="localhost")
    if not validate_host(host):
        print_warning("Invalid host. Using 'localhost'.")
        host = "localhost"
    
    config["host"] = host
    
    default_port = SERVICE_DEFAULT_PORTS.get(service, 8080)
    if is_port_in_use(default_port):
        suggested = find_available_port(default_port)
        print_warning(f"Port {default_port} is in use. Suggested: {suggested}")
        default_port = suggested
    
    port_raw = prompt(f"Port", default=str(default_port))
    try:
        port = int(port_raw)
        if is_port_in_use(port):
            alt = find_available_port(port)
            print_warning(f"Port {port} in use. Switching to {alt}.")
            port = alt
    except ValueError:
        port = default_port
    
    config["port"] = port
    
    use_https = False
    use_caddy = False
    
    if is_domain(host):
        protocol_choice = prompt_choice(
            "Connection type",
            ["HTTPS (recommended, auto TLS via Caddy)", "HTTP only"],
            default=1
        )
        use_https = "HTTPS" in protocol_choice
        use_caddy = use_https
    
    config["protocol"] = "https" if use_https else "http"
    config["use_caddy"] = use_caddy
    
    if service == "gitea":
        ssh_raw = prompt("Git SSH port", default="2222")
        try:
            ssh_port = int(ssh_raw)
            config["ssh_port"] = find_available_port(ssh_port)
        except ValueError:
            config["ssh_port"] = find_available_port(2222)
    
    elif service == "gitlab":
        ssh_raw = prompt("GitLab SSH port", default="2224")
        try:
            ssh_port = int(ssh_raw)
            config["ssh_port"] = find_available_port(ssh_port)
        except ValueError:
            config["ssh_port"] = find_available_port(2224)
    
    elif service == "kong":
        admin_raw = prompt("Kong Admin API port", default=str(port + 1))
        try:
            config["admin_port"] = find_available_port(int(admin_raw))
        except ValueError:
            config["admin_port"] = find_available_port(port + 1)
    
    elif service == "jenkins":
        agent_raw = prompt("Jenkins agent port", default="50000")
        try:
            config["agent_port"] = find_available_port(int(agent_raw))
        except ValueError:
            config["agent_port"] = find_available_port(50000)
    
    return config

def _show_warnings(service: str):
    warnings = get_service_warnings(service)
    if warnings:
        print_section("Important Notes")
        for w in warnings:
            print_warning(w)

def _confirm_deploy(service: str, config: dict):
    print_section("Deployment Summary")
    print_info(f"Service:   {service.upper()}")
    print_info(f"Host:      {config['host']}")
    print_info(f"Port:      {config['port']}")
    print_info(f"Protocol:  {config['protocol'].upper()}")
    print_info(f"Caddy:     {'Yes' if config.get('use_caddy') else 'No'}")
    print()
    print_divider()
    
    confirmed = prompt_confirm("Proceed with deployment?", default=True)
    if not confirmed:
        print_info("Deployment cancelled.")
        sys.exit(0)

def _run_deployment(service: str, config: dict):
    print_section("Deployment")
    
    distro = detect_distro()
    pm = distro.get("package_manager", "apt")
    
    def on_step(msg):
        spinner(msg, duration=1.2)
    
    try:
        deploy_service(service, config, on_step=on_step)
        
        if config.get("use_caddy") and is_domain(config["host"]):
            spinner("Configuring Caddy reverse proxy...", duration=1.5)
            configure_domain(config["host"], config["port"], pm)
            access_url = f"https://{config['host']}"
        else:
            access_url = f"http://{config['host']}:{config['port']}"
        
        print_completion(service, access_url)
    
    except CypherError as e:
        print_error(f"Deployment failed: {e}")
        sys.exit(1)