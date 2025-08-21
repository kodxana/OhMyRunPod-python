import subprocess
import os
import platform
import secrets
import string
import shutil
import tempfile
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
                # Tighten permissions if possible
                try:
                    os.chmod(key_path, 0o600)
                    pub = key_path + '.pub'
                    if Path(pub).exists():
                        os.chmod(pub, 0o644)
                except Exception:
                    pass
            except subprocess.CalledProcessError:
                print_status(f"Failed to generate {key_type} host key.", "error")
                return False
    
    if keys_generated:
        print_status("SSH host keys generated successfully.", "success")
    else:
        print_status("SSH host keys are already present.", "success")
    
    return True

def _detect_service_names():
    """Detect usable service tool and ssh service name (containers: no systemd)."""
    managers = []
    if shutil.which("service"):
        managers.append("service")
    if shutil.which("rc-service"):
        managers.append("rc-service")
    # Fallback: try init.d script paths
    services = ["sshd", "ssh"]
    return managers, services

def _restart_ssh_service():
    managers, services = _detect_service_names()
    errors = []
    for mgr in managers:
        for svc in services:
            try:
                if mgr == "service":
                    subprocess.run([mgr, svc, "restart"], check=True)
                elif mgr == "rc-service":
                    subprocess.run([mgr, svc, "restart"], check=True)
                print_status(f"SSH service restarted via {mgr} ({svc}).", "success")
                return True
            except subprocess.CalledProcessError as e:
                errors.append(f"{mgr} {svc}: {e}")
                continue
    # Fallback: init.d script
    for svc in ("sshd", "ssh"):
        path = f"/etc/init.d/{svc}"
        if Path(path).exists():
            try:
                subprocess.run([path, "restart"], check=True)
                print_status(f"SSH service restarted via {path}.", "success")
                return True
            except subprocess.CalledProcessError as e:
                errors.append(f"{path}: {e}")
    print_status("Could not restart SSH service automatically. Try manually.", "warning")
    if errors:
        print_status("; ".join(errors), "warning")
    return False

def _set_directives_idempotent(lines, directives):
    """Return new sshd_config content lines with directives set before any Match blocks.

    Removes existing occurrences of these directives outside Match blocks,
    then inserts desired directives before first Match block (or at end).
    """
    out = []
    in_match = False
    inserted = False
    cleaned = []
    keys = {k.lower() for k in directives.keys()}
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("match "):
            in_match = True
        if not stripped or stripped.startswith("#"):
            cleaned.append(line)
            continue
        key = stripped.split()[0].lower()
        if key in keys and not in_match:
            # skip existing directive outside Match; we'll add ours
            continue
        cleaned.append(line)

    # Find insertion point
    for idx, line in enumerate(cleaned):
        if line.strip().lower().startswith("match "):
            new_block = [f"{k} {v}\n" for k, v in directives.items()]
            out = cleaned[:idx] + new_block + cleaned[idx:]
            inserted = True
            break
    if not inserted:
        out = cleaned + ["\n"] + [f"{k} {v}\n" for k, v in directives.items()]
    return out

def configure_ssh():
    """Configure SSH robustly and validate before applying."""
    print_status("Configuring SSH to allow root login with a password...", "info")

    config_path = Path('/etc/ssh/sshd_config')
    backup_path = Path('/etc/ssh/sshd_config.ohmyrunpod.bak')
    desired = {
        "PermitRootLogin": "yes",
        "PasswordAuthentication": "yes",
    }

    try:
        original = config_path.read_text().splitlines(keepends=True)
        new_lines = _set_directives_idempotent(original, desired)

        # Validate using a temp file
        with tempfile.NamedTemporaryFile('w', delete=False) as tmp:
            tmp.writelines(new_lines)
            tmp_path = tmp.name

        try:
            subprocess.run(['sshd', '-t', '-f', tmp_path], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            msg = e.stderr.decode() if getattr(e, 'stderr', None) else str(e)
            print_status(f"New SSH config invalid: {msg}", "error")
            os.unlink(tmp_path)
            return False

        # Backup once and apply
        if not backup_path.exists():
            try:
                shutil.copy2(config_path, backup_path)
                print_status(f"Backup saved to {backup_path}", "success")
            except Exception:
                pass

        Path(tmp_path).replace(config_path)
        print_status("SSH Configuration Updated.", "success")

        # Restart/reload service
        _restart_ssh_service()
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
