import sys
import signal
from cli import print_banner, print_error
from interactive import run_interactive_flow
from errorhandling import handle_interrupt, CypherError

def main():
    signal.signal(signal.SIGINT, handle_interrupt)
    
    try:
        print_banner()
        run_interactive_flow()
    except CypherError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()