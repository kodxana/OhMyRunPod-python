import subprocess
import os
import shutil
import urllib.request
import tempfile
import platform
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from OhMyRunPod.utils.menu import BaseMenu

from OhMyRunPod.modules.ssh_setup.ssh_setup import run_ssh_setup

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

def detect_architecture():
    """Detect system architecture for croc download"""
    machine = platform.machine().lower()
    if machine in ['x86_64', 'amd64']:
        return 'amd64'
    elif machine in ['aarch64', 'arm64']:
        return 'arm64'
    elif machine in ['armv7l', 'armv6l']:
        return 'arm'
    elif machine in ['i386', 'i686']:
        return '386'
    else:
        return 'amd64'  # Default fallback

def install_croc():
    """Install croc file transfer tool"""
    print_status("Checking if croc is installed...", "info")
    
    if shutil.which('croc'):
        print_status("croc is already installed.", "success")
        return True
    
    print_status("croc not found. Installing...", "warning")
    
    try:
        # Get the latest release URL for Linux
        arch = detect_architecture()
        base_url = "https://github.com/schollz/croc/releases/latest/download"
        filename = f"croc_Linux_{arch}.tar.gz"
        download_url = f"{base_url}/{filename}"
        
        print_status(f"Downloading croc for {arch} architecture...", "info")
        
        # Download croc
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_path = temp_path / filename
            
            urllib.request.urlretrieve(download_url, archive_path)
            
            # Extract the archive
            extract_result = subprocess.run(
                ['tar', 'xzf', str(archive_path), '-C', str(temp_path)],
                capture_output=True, text=True
            )
            
            if extract_result.returncode != 0:
                print_status(f"Failed to extract croc: {extract_result.stderr}", "error")
                return False
            
            # Move croc to /usr/local/bin
            croc_binary = temp_path / 'croc'
            if croc_binary.exists():
                subprocess.run(['sudo', 'mv', str(croc_binary), '/usr/local/bin/croc'], check=True)
                subprocess.run(['sudo', 'chmod', '+x', '/usr/local/bin/croc'], check=True)
                print_status("croc installed successfully to /usr/local/bin/croc", "success")
                return True
            else:
                print_status("croc binary not found in archive", "error")
                return False
                
    except Exception as e:
        print_status(f"Failed to install croc: {e}", "error")
        return False

def setup_croc():
    """Setup croc for file transfers"""
    console.print("\n[bold blue]Croc File Transfer Setup[/bold blue]")
    console.print("=" * 50)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        
        task = progress.add_task("Setting up croc...", total=None)
        
        if not install_croc():
            return False
        
        progress.update(task, completed=True)
    
    # Show usage instructions
    console.print("\n[bold green]Croc Setup Complete![/bold green]")
    console.print("\n[bold cyan]How to use croc for file transfers:[/bold cyan]")
    
    usage_table = Table(show_header=True, header_style="bold blue")
    usage_table.add_column("Action", style="cyan", no_wrap=True)
    usage_table.add_column("Command", style="black")
    usage_table.add_column("Description", style="black")
    
    usage_table.add_row(
        "Send files",
        "croc send <file/folder>",
        "Send files to another device"
    )
    usage_table.add_row(
        "Receive files",
        "croc <code>",
        "Receive files using the code from sender"
    )
    usage_table.add_row(
        "Send with custom code",
        "croc send --code mycode <file>",
        "Send with a custom code phrase"
    )
    usage_table.add_row(
        "Send to specific IP",
        "croc --relay <IP:port> send <file>",
        "Use specific relay server"
    )
    
    console.print(usage_table)
    
    console.print("\n[bold blue]Example workflow:[/bold blue]")
    console.print("1. [cyan]On this pod:[/cyan] croc send myfile.txt")
    console.print("2. [cyan]On your computer:[/cyan] croc <code-shown-above>")
    console.print("3. Files will be transferred securely!")
    
    console.print("\n[dim]Note: croc uses end-to-end encryption and works through NAT/firewalls[/dim]")
    
    return True

def setup_sftp():
    """Setup SFTP by running SSH setup and providing connection details"""
    console.print("\n[bold blue]SFTP Setup[/bold blue]")
    console.print("=" * 50)
    
    # First run SSH setup
    print_status("Setting up SSH server for SFTP access...", "info")
    if not run_ssh_setup():
        print_status("SSH setup failed. SFTP cannot be configured.", "error")
        return False
    
    # Get connection details
    public_ip = os.getenv('RUNPOD_PUBLIC_IP')
    port = os.getenv('RUNPOD_TCP_PORT_22')
    
    if not public_ip or not port:
        print_status("Missing environment variables for connection details", "error")
        return False
    
    # Read the generated password
    password_file = Path('/workspace/root_password.txt')
    if password_file.exists():
        password = password_file.read_text().strip()
    else:
        password = "Check /workspace/root_password.txt"
    
    # Display connection information
    console.print("\n[bold green]SFTP Setup Complete![/bold green]")
    console.print("\n[bold cyan]Connection Details:[/bold cyan]")
    
    # Create connection details panel
    connection_info = Table(show_header=False, box=None, padding=(0, 1))
    connection_info.add_column("Field", style="cyan", no_wrap=True)
    connection_info.add_column("Value", style="black")
    
    connection_info.add_row("Server Address:", f"sftp://{public_ip}")
    connection_info.add_row("Port:", port)
    connection_info.add_row("Username:", "root")
    connection_info.add_row("Password:", password)
    
    panel = Panel(
        connection_info,
        title="[bold blue]SFTP Connection Information[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    )
    
    console.print(panel)
    
    # SFTP client instructions
    console.print("\n[bold cyan]How to connect with SFTP clients:[/bold cyan]")
    
    clients_table = Table(show_header=True, header_style="bold blue")
    clients_table.add_column("Client", style="cyan", no_wrap=True)
    clients_table.add_column("Configuration", style="black")
    
    clients_table.add_row(
        "FileZilla",
        f"Host: sftp://{public_ip} | Port: {port} | User: root"
    )
    clients_table.add_row(
        "WinSCP",
        f"Host: {public_ip} | Port: {port} | Protocol: SFTP | User: root"
    )
    clients_table.add_row(
        "Command Line",
        f"sftp -P {port} root@{public_ip}"
    )
    clients_table.add_row(
        "VS Code",
        f"sftp://root@{public_ip}:{port}"
    )
    
    console.print(clients_table)
    
    console.print("\n[bold blue]Important Notes:[/bold blue]")
    console.print("• [dim]Password is saved in /workspace/root_password.txt[/dim]")
    console.print("• [dim]Root directory is accessible via SFTP[/dim]")
    console.print("• [dim]Files can be uploaded/downloaded to/from any directory[/dim]")
    console.print("• [dim]Connection is secured with SSH encryption[/dim]")
    
    return True

class FileTransferMenu:
    def __init__(self):
        self.console = Console()
        self.options = [
            ("Croc", "Easy peer-to-peer transfer (may use relays)"),
            ("SFTP", "Direct SSH/SFTP transfer (often faster)"),
            ("Back", "Return to main menu"),
        ]

    def run(self) -> int:
        menu = BaseMenu(
            title="File Transfer Options",
            options=self.options,
            breadcrumbs=["Home", "File Transfer"],
            help_lines=[
                "Croc: Simple, secure peer-to-peer file transfer with codes.",
                "Croc may use relays, which can be slower than direct SFTP.",
                "SFTP: Direct transfer via SSH; often faster on the same network.",
                "SFTP details are printed after setup (server, port, user, password).",
                "Tip: Use numbers + Enter to select options.",
            ],
        )
        return menu.run()

def show_file_transfer_menu():
    """Show file transfer options menu with arrow key navigation"""
    menu = FileTransferMenu()
    
    while True:
        try:
            selected_option = menu.run()
            
            if selected_option == 0:  # Croc
                console.clear()
                setup_croc()
                break
            elif selected_option == 1:  # SFTP
                console.clear()
                setup_sftp()
                break
            elif selected_option == 2:  # Back
                break
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            continue
