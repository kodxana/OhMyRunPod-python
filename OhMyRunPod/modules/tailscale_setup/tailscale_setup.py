import subprocess
from pkg_resources import resource_filename
import os

def run_tailscale_setup_script(auth_key):
    script_path = resource_filename('OhMyRunPod', 'modules/tailscale_setup/tailscale-setup.sh')
    os.chmod(script_path, 0o755)
    subprocess.run(["bash", script_path, auth_key])

def get_auth_key():
    auth_key = input("Please enter your Tailscale API key: ")
    return auth_key
