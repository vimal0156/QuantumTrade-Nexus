import os
import yaml

def get_config():
    """Load config.yaml dynamically based on the environment."""
    # Debugging: Where is this script being executed from?
    print(f"Current working directory: {os.getcwd()}")
    
    # Resolve the base path depending on the environment
    if os.name == "nt":  # Windows (local development)
        config_path = r"config\config.yaml"
    else:  # Default to the container path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.normpath(os.path.join(script_dir, "config", "config.yaml"))

    # Debugging output
    print(f"Resolved config path: {config_path}")

    # Check if the config file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    # Load the config file
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
