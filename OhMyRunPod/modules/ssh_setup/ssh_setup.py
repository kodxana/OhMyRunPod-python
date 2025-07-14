import subprocess
import os
import platform
import secrets
import string
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

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

def detect_os():
    """Detect the operating system and distribution"""
    print_status("Detecting Linux Distribution...", "info")
    
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = f.read().lower()
        
        if 'ubuntu' in os_info or 'debian' in os_info:
            return 'debian'
        elif 'redhat' in os_info or 'centos' in os_info or 'rhel' in os_info:
            return 'redhat'
        else:
            return 'unknown'
    except FileNotFoundError:
        return 'unknown'

def install_ssh_server():
    """Install SSH server if not present"""
    if shutil.which('sshd'):
        print_status("SSH Server is already installed.", "success")
        return True
    
    print_status("SSH server not found. Installing...", "warning")
    
    os_type = detect_os()
    
    try:
        if os_type == 'debian':
            subprocess.run(['apt-get', 'update'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'openssh-server'], check=True)
        elif os_type == 'redhat':
            subprocess.run(['yum', 'install', '-y', 'openssh-server'], check=True)
        else:
            print_status("Unsupported Linux distribution for automatic SSH installation.", "error")
            return False
        
        print_status("SSH Server Installed Successfully.", "success")
        return True
    except subprocess.CalledProcessError:
        print_status("Failed to install SSH server.", "error")
        return False

def generate_ssh_host_keys():
    """Generate SSH host keys if not present"""
    print_status("Checking for SSH host keys...", "info")
    
    keys_to_generate = [
        ('/etc/ssh/ssh_host_ed25519_key', 'ed25519'),
        ('/etc/ssh/ssh_host_rsa_key', 'rsa')
    ]
    
    keys_generated = False
    
    for key_path, key_type in keys_to_generate:
        if not Path(key_path).exists():
            print_status(f"Generating {key_type} host key...", "info")
            try:
                cmd = ['ssh-keygen', '-t', key_type, '-f', key_path, '-N', '']
                if key_type == 'rsa':
                    cmd.extend(['-b', '4096'])
                subprocess.run(cmd, check=True)
                keys_generated = True
            except subprocess.CalledProcessError:
                print_status(f"Failed to generate {key_type} host key.", "error")
                return False
    
    if keys_generated:
        print_status("SSH host keys generated successfully.", "success")
    else:
        print_status("SSH host keys are already present.", "success")
    
    return True

def configure_ssh():
    """Configure SSH to allow root login"""
    print_status("Configuring SSH to allow root login with a password...", "info")
    
    config_path = Path('/etc/ssh/sshd_config')
    
    try:
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Update SSH configuration
        content = content.replace('#PermitRootLogin prohibit-password', 'PermitRootLogin yes')
        content = content.replace('#PasswordAuthentication no', 'PasswordAuthentication yes')
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        # Restart SSH service
        subprocess.run(['service', 'ssh', 'restart'], check=True)
        print_status("SSH Configuration Updated.", "success")
        return True
    except Exception as e:
        print_status(f"Failed to configure SSH: {e}", "error")
        return False

def generate_random_password():
    """Generate a secure random password"""
    print_status("Generating a secure random password for root...", "info")
    
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    try:
        # Set root password
        subprocess.run(['chpasswd'], input=f'root:{password}', text=True, check=True)
        
        # Save password to file
        password_file = Path('/workspace/root_password.txt')
        password_file.write_text(password)
        
        print_status("Root password generated and saved in /workspace/root_password.txt", "success")
        return password
    except Exception as e:
        print_status(f"Failed to set root password: {e}", "error")
        return None

def check_environment_variables():
    """Check if required environment variables are set"""
    print_status("Checking environment variables...", "info")
    
    required_vars = ['RUNPOD_PUBLIC_IP', 'RUNPOD_TCP_PORT_22']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print_status(f"Environment variables missing: {', '.join(missing_vars)}", "error")
        return False
    
    print_status("Environment variables are set.", "success")
    return True

def create_connection_scripts(password):
    """Create connection scripts for different platforms"""
    public_ip = os.getenv('RUNPOD_PUBLIC_IP')
    port = os.getenv('RUNPOD_TCP_PORT_22')
    
    workspace = Path('/workspace')
    
    # Windows batch script
    print_status("Creating connection script for Windows...", "info")
    windows_script = workspace / 'connect_windows.bat'
    windows_content = f"""@echo off
echo Root password: {password}
ssh root@{public_ip} -p {port}
"""
    windows_script.write_text(windows_content)
    print_status("Windows connection script created in /workspace.", "success")
    
    # Linux/Mac shell script
    print_status("Creating connection script for Linux/Mac...", "info")
    linux_script = workspace / 'connect_linux.sh'
    linux_content = f"""#!/bin/bash
echo Root password: {password}
ssh root@{public_ip} -p {port}
"""
    linux_script.write_text(linux_content)
    linux_script.chmod(0o755)
    print_status("Linux/Mac connection script created in /workspace.", "success")

def run_ssh_setup():
    """Main SSH setup function"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task("Setting up SSH...", total=None)
        
        # Check environment variables first
        if not check_environment_variables():
            return False
        
        # Install SSH server
        if not install_ssh_server():
            return False
        
        # Generate host keys
        if not generate_ssh_host_keys():
            return False
        
        # Configure SSH
        if not configure_ssh():
            return False
        
        # Generate password
        password = generate_random_password()
        if not password:
            return False
        
        # Create connection scripts
        create_connection_scripts(password)
        
        progress.update(task, completed=True)
    
    print_status("Setup Completed Successfully!", "success")
    return True

def run_ssh_setup_script():
    """Legacy function for backward compatibility"""
    return run_ssh_setup()
