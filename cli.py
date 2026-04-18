import sys
import time

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"

SERVICES_DISPLAY = {
    "n8n": "n8n — Workflow Automation",
    "supabase": "Supabase — Open Source Firebase",
    "kong": "Kong — API Gateway",
    "mailcow": "Mailcow — Email Server Suite",
    "mattermost": "Mattermost — Team Messaging",
    "jenkins": "Jenkins — CI/CD Automation",
    "gitea": "Gitea — Lightweight Git Service",
    "gitlab": "GitLab — DevOps Platform",
    "jitsi": "Jitsi — Video Conferencing",
    "openproject": "OpenProject — Project Management",
}

def print_banner():
    banner = f"""
{CYAN}{BOLD}
   ██████╗██╗   ██╗██████╗ ██╗  ██╗███████╗██████╗ 
  ██╔════╝╚██╗ ██╔╝██╔══██╗██║  ██║██╔════╝██╔══██╗
  ██║      ╚████╔╝ ██████╔╝███████║█████╗  ██████╔╝
  ██║       ╚██╔╝  ██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗
  ╚██████╗   ██║   ██║     ██║  ██║███████╗██║  ██║
   ╚═════╝   ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{RESET}
{DIM}  Open-Source Deployment Automation for Linux Servers{RESET}
{DIM}  ─────────────────────────────────────────────────{RESET}
"""
    print(banner)

def print_step(message: str):
    print(f"  {CYAN}→{RESET}  {WHITE}{message}{RESET}")

def print_success(message: str):
    print(f"  {GREEN}✔{RESET}  {GREEN}{message}{RESET}")

def print_warning(message: str):
    print(f"  {YELLOW}⚠{RESET}  {YELLOW}{message}{RESET}")

def print_error(message: str):
    print(f"  {RED}✖{RESET}  {RED}{message}{RESET}")

def print_info(message: str):
    print(f"  {BLUE}ℹ{RESET}  {DIM}{message}{RESET}")

def print_section(title: str):
    print(f"\n{BOLD}{MAGENTA}  ▸ {title}{RESET}\n")

def print_divider():
    print(f"  {DIM}{'─' * 52}{RESET}")

def print_service_menu():
    print_section("Available Services")
    services = list(SERVICES_DISPLAY.items())
    for i, (key, label) in enumerate(services, 1):
        print(f"  {DIM}{i:2}.{RESET}  {WHITE}{label}{RESET}")
    print()

def print_completion(service: str, access_url: str):
    print(f"""
{GREEN}{BOLD}  ╔══════════════════════════════════════════════════╗
  ║              ✅  Setup Complete!                 ║
  ╚══════════════════════════════════════════════════╝{RESET}

  {WHITE}Service:{RESET}    {CYAN}{service.upper()}{RESET}
  {WHITE}Access at:{RESET}  {CYAN}{BOLD}{access_url}{RESET}

{DIM}  The service is now running in the background.
  Use Docker commands to manage the containers.{RESET}
""")

def prompt(label: str, default: str = "") -> str:
    if default:
        formatted = f"  {CYAN}?{RESET}  {WHITE}{label}{RESET} {DIM}[{default}]{RESET}: "
    else:
        formatted = f"  {CYAN}?{RESET}  {WHITE}{label}{RESET}: "
    
    try:
        value = input(formatted).strip()
    except EOFError:
        return default
    
    return value if value else default

def prompt_choice(label: str, options: list, default: int = 1) -> str:
    print(f"  {CYAN}?{RESET}  {WHITE}{label}{RESET}")
    for i, opt in enumerate(options, 1):
        marker = f"{GREEN}▸{RESET}" if i == default else " "
        print(f"    {marker} {i}. {opt}")
    
    try:
        raw = input(f"  {DIM}Enter number [{default}]{RESET}: ").strip()
        choice = int(raw) if raw else default
        if 1 <= choice <= len(options):
            return options[choice - 1]
    except (ValueError, EOFError):
        pass
    
    return options[default - 1]

def prompt_confirm(label: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    try:
        raw = input(f"  {CYAN}?{RESET}  {WHITE}{label}{RESET} {DIM}[{hint}]{RESET}: ").strip().lower()
    except EOFError:
        return default
    
    if not raw:
        return default
    return raw in ("y", "yes")

def spinner(message: str, duration: float = 1.5):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r  {CYAN}{frames[i % len(frames)]}{RESET}  {WHITE}{message}{RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write(f"\r  {GREEN}✔{RESET}  {GREEN}{message}{RESET}\n")
    sys.stdout.flush()