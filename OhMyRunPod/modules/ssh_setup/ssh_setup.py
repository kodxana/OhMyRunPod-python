import subprocess
from pkg_resources import resource_filename
import os

def run_ssh_setup_script():
    script_path = resource_filename('OhMyRunPod', 'modules/ssh_setup/ssh-setup.sh')
    os.chmod(script_path, 0o755)  # Ensure the script is executable
    subprocess.run(["bash", script_path])
