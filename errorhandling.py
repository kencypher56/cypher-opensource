import sys

class CypherError(Exception):
    pass

class DockerError(CypherError):
    pass

class NetworkError(CypherError):
    pass

class ConfigError(CypherError):
    pass

class ServiceError(CypherError):
    pass

def handle_interrupt(signum, frame):
    print(f"\n\n  \033[93m⚠\033[0m  \033[93mInterrupted by user. Exiting gracefully...\033[0m\n")
    sys.exit(0)

def safe_run(func, error_class=CypherError, message=None):
    try:
        return func()
    except CypherError:
        raise
    except Exception as e:
        raise error_class(message or str(e)) from e