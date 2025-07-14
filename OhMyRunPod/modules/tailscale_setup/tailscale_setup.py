import subprocess
import os
import time
import urllib.request
import tempfile
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt

console = Console()

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "info": "blue",
        "success": "green", 
        "warning": "yellow",
        "error": "red"
    }
    console.print(f"[{colors.get(status, 'white')}]{message}[/]")

def download_tailscale_installer():
    """Download and install Tailscale"""
    print_status("Downloading Tailscale installer...", "info")
    
    try:
        # Download the install script
        install_url = "https://tailscale.com/install.sh"
        with urllib.request.urlopen(install_url) as response:
            install_script = response.read().decode('utf-8')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as tmp_file:
            tmp_file.write(install_script)
            script_path = tmp_file.name
        
        # Make executable and run
        os.chmod(script_path, 0o755)
        result = subprocess.run(['bash', script_path], capture_output=True, text=True)
        
        # Clean up
        os.unlink(script_path)
        
        if result.returncode == 0:
            print_status("Tailscale installed successfully.", "success")
            return True
        else:
            print_status(f"Failed to install Tailscale: {result.stderr}", "error")
            return False
            
    except Exception as e:
        print_status(f"Error downloading Tailscale: {e}", "error")
        return False

def start_tailscale_daemon():
    """Start Tailscale daemon in userspace networking mode"""
    print_status("Starting Tailscale daemon in userspace networking mode...", "info")
    
    try:
        # Start tailscaled in background
        cmd = [
            'tailscaled',
            '--tun=userspace-networking',
            '--socks5-server=localhost:1055',
            '--outbound-http-proxy-listen=localhost:1055'
        ]
        
        # Start process in background
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for daemon to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print_status("Tailscale daemon started successfully.", "success")
            return True
        else:
            stdout, stderr = process.communicate()
            print_status(f"Failed to start Tailscale daemon: {stderr.decode()}", "error")
            return False
            
    except Exception as e:
        print_status(f"Error starting Tailscale daemon: {e}", "error")
        return False

def connect_tailscale(auth_key):
    """Connect to Tailscale network using auth key"""
    print_status("Connecting to Tailscale network...", "info")
    
    try:
        # Connect with auth key
        result = subprocess.run(['tailscale', 'up', f'--authkey={auth_key}'], 
                              capture_output=True, text=True, check=True)
        
        # Enable SSH
        result = subprocess.run(['tailscale', 'up', '--ssh'], 
                              capture_output=True, text=True, check=True)
        
        print_status("Tailscale connected successfully.", "success")
        return True
        
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to connect Tailscale: {e.stderr}", "error")
        return False
    except Exception as e:
        print_status(f"Error connecting Tailscale: {e}", "error")
        return False

def run_tailscale_setup(auth_key):
    """Main Tailscale setup function"""
    if not auth_key:
        print_status("No Tailscale auth key provided.", "error")
        return False
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task("Setting up Tailscale...", total=None)
        
        # Download and install Tailscale
        if not download_tailscale_installer():
            return False
        
        # Start Tailscale daemon
        if not start_tailscale_daemon():
            return False
        
        # Connect to Tailscale network
        if not connect_tailscale(auth_key):
            return False
        
        progress.update(task, completed=True)
    
    print_status("Tailscale setup completed successfully.", "success")
    return True

def get_auth_key():
    """Get Tailscale auth key from user input"""
    auth_key = Prompt.ask("Please enter your Tailscale auth key", password=True)
    return auth_key

def run_tailscale_setup_script(auth_key):
    """Legacy function for backward compatibility"""
    return run_tailscale_setup(auth_key)
