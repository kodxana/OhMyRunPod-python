import subprocess
import os
import sys
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from OhMyRunPod.utils.menu import BaseMenu

console = Console()

# Settings file path
SETTINGS_FILE = Path("/workspace/ohmyrunpod_comfyui_settings.json")

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "info": "blue",
        "success": "green", 
        "warning": "yellow",
        "error": "red"
    }
    console.print(f"[{colors.get(status, 'white')}]{message}[/]")

def load_settings():
    """Load ComfyUI settings from file"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"configurations": [], "last_used": None}
    return {"configurations": [], "last_used": None}

def save_settings(settings):
    """Save ComfyUI settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print_status(f"Failed to save settings: {e}", "error")
        return False

def detect_comfyui_templates():
    """Detect known ComfyUI templates"""
    templates = []
    
    # Aitrepreneur template detection
    if Path("/workspace/logs/runpod-uploader.log").exists():
        comfyui_path = Path("/workspace/ComfyUI")
        venv_path = Path("/workspace/ComfyUI/venv")
        if comfyui_path.exists():
            templates.append({
                "name": "Aitrepreneur Template",
                "type": "aitrepreneur",
                "comfyui_path": str(comfyui_path),
                "venv_path": str(venv_path),
                "detected": True
            })
    
    # Standard ComfyUI with .venv
    comfyui_path = Path("/workspace/ComfyUI")
    venv_path = Path("/workspace/ComfyUI/.venv")
    if comfyui_path.exists() and venv_path.exists():
        templates.append({
            "name": "Standard ComfyUI (.venv)",
            "type": "standard_venv",
            "comfyui_path": str(comfyui_path),
            "venv_path": str(venv_path),
            "detected": True
        })
    elif comfyui_path.exists():
        # Standard without .venv (might be the aitrepreneur if already detected)
        existing_names = [t["name"] for t in templates]
        if "Aitrepreneur Template" not in existing_names:
            templates.append({
                "name": "Standard ComfyUI",
                "type": "standard",
                "comfyui_path": str(comfyui_path),
                "venv_path": str(Path("/workspace/ComfyUI/venv")),
                "detected": True
            })
    
    # Madiator2011's Better Slim template
    comfyui_path = Path("/workspace/madapps/ComfyUI")
    venv_path = Path("/workspace/madapps/ComfyUI/.venv")
    if comfyui_path.exists():
        templates.append({
            "name": "Madiator2011's Better Slim Template",
            "type": "madiator_slim",
            "comfyui_path": str(comfyui_path),
            "venv_path": str(venv_path),
            "detected": True
        })
    
    return templates

def validate_comfyui_installation(comfyui_path, venv_path):
    """Validate ComfyUI installation"""
    comfyui_path = Path(comfyui_path)
    venv_path = Path(venv_path)
    
    issues = []
    
    # Check ComfyUI directory
    if not comfyui_path.exists():
        issues.append(f"ComfyUI directory not found: {comfyui_path}")
    else:
        # Check for main.py
        main_py = comfyui_path / "main.py"
        if not main_py.exists():
            issues.append(f"main.py not found in ComfyUI directory")
        
        # Check for basic directories
        for dir_name in ["models", "custom_nodes"]:
            if not (comfyui_path / dir_name).exists():
                issues.append(f"{dir_name} directory not found")
    
    # Check virtual environment
    if not venv_path.exists():
        issues.append(f"Virtual environment not found: {venv_path}")
    else:
        # Check for Python executable
        python_exe = venv_path / "bin" / "python"
        if not python_exe.exists():
            # Try Windows path
            python_exe = venv_path / "Scripts" / "python.exe"
            if not python_exe.exists():
                issues.append("Python executable not found in virtual environment")
    
    return issues

def get_current_configuration():
    """Get the current ComfyUI configuration"""
    settings = load_settings()
    
    # Try to find a configuration
    if settings.get("last_used"):
        # Use last used configuration
        for config in settings["configurations"]:
            if config["name"] == settings["last_used"]:
                return config
    
    # Try auto-detection
    detected = detect_comfyui_templates()
    if detected:
        return detected[0]
    
    return None

def add_custom_configuration():
    """Add a custom ComfyUI configuration"""
    console.print("\n[bold blue]Add Custom ComfyUI Configuration[/bold blue]")
    console.print("=" * 50)
    
    name = Prompt.ask("Configuration name")
    comfyui_path = Prompt.ask("ComfyUI directory path", default="/workspace/ComfyUI")
    venv_path = Prompt.ask("Virtual environment path", default=f"{comfyui_path}/venv")
    
    # Validate paths
    issues = validate_comfyui_installation(comfyui_path, venv_path)
    if issues:
        console.print("\n[bold red]Validation Issues:[/bold red]")
        for issue in issues:
            console.print(f"• [red]{issue}[/red]")
        
        if not Confirm.ask("Do you want to save this configuration anyway?"):
            return False
    
    # Save configuration
    settings = load_settings()
    
    # Check if name already exists
    for config in settings["configurations"]:
        if config["name"] == name:
            if not Confirm.ask(f"Configuration '{name}' already exists. Overwrite?"):
                return False
            settings["configurations"].remove(config)
            break
    
    new_config = {
        "name": name,
        "type": "custom",
        "comfyui_path": comfyui_path,
        "venv_path": venv_path,
        "detected": False
    }
    
    settings["configurations"].append(new_config)
    settings["last_used"] = name
    
    if save_settings(settings):
        print_status(f"Configuration '{name}' saved successfully!", "success")
        return True
    else:
        print_status("Failed to save configuration", "error")
        return False

def list_configurations():
    """List all available ComfyUI configurations"""
    console.print("\n[bold blue]Available ComfyUI Configurations[/bold blue]")
    console.print("=" * 50)
    
    # Get detected templates
    detected = detect_comfyui_templates()
    
    # Get saved configurations
    settings = load_settings()
    saved_configs = settings.get("configurations", [])
    
    if not detected and not saved_configs:
        console.print("[yellow]No ComfyUI installations detected or configured.[/yellow]")
        return
    
    # Display detected templates
    if detected:
        console.print("\n[bold cyan]Auto-detected Templates:[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="white", no_wrap=True)
        table.add_column("ComfyUI Path", style="black")
        table.add_column("Venv Path", style="black")
        table.add_column("Status", style="green")
        
        for template in detected:
            issues = validate_comfyui_installation(template["comfyui_path"], template["venv_path"])
            status = "✓ Valid" if not issues else "⚠ Issues"
            status_color = "green" if not issues else "yellow"
            
            table.add_row(
                template["name"],
                template["type"],
                template["comfyui_path"],
                template["venv_path"],
                f"[{status_color}]{status}[/{status_color}]"
            )
        
        console.print(table)
    
    # Display saved configurations
    if saved_configs:
        console.print("\n[bold cyan]Saved Configurations:[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="white", no_wrap=True)
        table.add_column("ComfyUI Path", style="black")
        table.add_column("Venv Path", style="black")
        table.add_column("Status", style="green")
        
        for config in saved_configs:
            issues = validate_comfyui_installation(config["comfyui_path"], config["venv_path"])
            status = "✓ Valid" if not issues else "⚠ Issues"
            status_color = "green" if not issues else "yellow"
            
            table.add_row(
                config["name"],
                config["type"],
                config["comfyui_path"],
                config["venv_path"],
                f"[{status_color}]{status}[/{status_color}]"
            )
        
        console.print(table)
    
    # Show current configuration
    current = get_current_configuration()
    if current:
        console.print(f"\n[bold green]Current Configuration:[/bold green] {current['name']}")
    else:
        console.print("\n[bold yellow]No configuration currently selected[/bold yellow]")

class ConfigurationSelector:
    def __init__(self, configurations):
        self.console = Console()
        self.configurations = configurations

    def run(self):
        """Select a configuration using the shared BaseMenu."""
        if not self.configurations:
            self.console.print("[yellow]No ComfyUI configurations available.[/yellow]")
            self.console.print("Use 'Add Custom Configuration' to add one.")
            self.console.print("\n[dim]Press Enter to continue...[/dim]")
            input()
            return None

        options = []
        for cfg in self.configurations:
            issues = validate_comfyui_installation(cfg["comfyui_path"], cfg["venv_path"])
            status = "✓ Valid" if not issues else "⚠ Issues"
            options.append((f"{cfg['name']} ({status})", f"ComfyUI: {cfg['comfyui_path']} | Venv: {cfg['venv_path']}"))
        options.append(("Back", "Cancel selection"))

        menu = BaseMenu(
            title="Select ComfyUI Configuration",
            options=options,
            breadcrumbs=["ComfyUI", "Configuration"],
        )
        idx = menu.run()
        if idx == len(options) - 1:
            return None
        return self.configurations[idx]

def select_configuration():
    """Select a ComfyUI configuration with arrow key navigation"""
    # Get all available configurations
    detected = detect_comfyui_templates()
    settings = load_settings()
    saved_configs = settings.get("configurations", [])
    
    # Remove duplicates (detected templates that are already saved)
    all_configs = detected.copy()
    for saved_config in saved_configs:
        if saved_config["name"] not in [d["name"] for d in detected]:
            all_configs.append(saved_config)
    
    # Create and run selector
    selector = ConfigurationSelector(all_configs)
    selected = selector.run()
    
    if selected:
        # Update settings
        settings["last_used"] = selected["name"]
        
        # Add to saved configs if it's a detected template
        if selected.get("detected") and selected["name"] not in [c["name"] for c in saved_configs]:
            settings["configurations"].append(selected)
        
        if save_settings(settings):
            print_status(f"Selected configuration: {selected['name']}", "success")
            return True
        else:
            print_status("Failed to save configuration selection", "error")
            return False
    else:
        print_status("Configuration selection cancelled", "warning")
        return False

def setup_comfy_cli(config):
    """Setup comfy-cli in the ComfyUI virtual environment"""
    print_status("Setting up comfy-cli...", "info")
    
    venv_path = Path(config["venv_path"])
    comfyui_path = Path(config["comfyui_path"])
    
    # Determine Python executable path
    python_exe = venv_path / "bin" / "python"
    if not python_exe.exists():
        python_exe = venv_path / "Scripts" / "python.exe"
    
    if not python_exe.exists():
        print_status("Python executable not found in virtual environment", "error")
        return False
    
    try:
        # Check if comfy-cli is already installed
        result = subprocess.run([str(python_exe), "-m", "pip", "show", "comfy-cli"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print_status("Installing comfy-cli...", "info")
            # Install comfy-cli
            result = subprocess.run([str(python_exe), "-m", "pip", "install", "comfy-cli"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print_status(f"Failed to install comfy-cli: {result.stderr}", "error")
                return False
            print_status("comfy-cli installed successfully", "success")
        else:
            print_status("comfy-cli is already installed", "success")
        
        # Set default ComfyUI path
        print_status("Setting default ComfyUI path...", "info")
        comfy_exe = venv_path / "bin" / "comfy"
        if not comfy_exe.exists():
            comfy_exe = venv_path / "Scripts" / "comfy.exe"
        
        # Set the default path
        result = subprocess.run([str(comfy_exe), "--skip-prompt", "--no-enable-telemetry", 
                               "set-default", str(comfyui_path)], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print_status(f"Failed to set default path: {result.stderr}", "error")
            return False
        
        print_status("Default ComfyUI path set successfully", "success")
        return True
        
    except Exception as e:
        print_status(f"Error setting up comfy-cli: {e}", "error")
        return False

def run_comfy_command(config, command_args):
    """Run a comfy command in the virtual environment"""
    venv_path = Path(config["venv_path"])
    
    # Determine comfy executable path
    comfy_exe = venv_path / "bin" / "comfy"
    if not comfy_exe.exists():
        comfy_exe = venv_path / "Scripts" / "comfy.exe"
    
    if not comfy_exe.exists():
        print_status("comfy-cli not found. Setting up...", "warning")
        if not setup_comfy_cli(config):
            return False
    
    try:
        # Prepare command
        cmd = [str(comfy_exe), "--skip-prompt", "--no-enable-telemetry"] + command_args
        
        # Run command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout:
                console.print(result.stdout)
            return True
        else:
            print_status(f"Command failed: {result.stderr}", "error")
            return False
            
    except Exception as e:
        print_status(f"Error running comfy command: {e}", "error")
        return False

def start_comfyui():
    """Start ComfyUI server"""
    console.print("\n[bold blue]ComfyUI Server Start[/bold blue]")
    console.print("=" * 50)
    
    # Get current configuration
    config = get_current_configuration()
    if not config:
        console.print("[red]No ComfyUI configuration found.[/red]")
        console.print("Please configure ComfyUI first using 'Configure ComfyUI' option.")
        return False
    
    print_status(f"Using configuration: {config['name']}", "info")
    
    # Validate installation
    issues = validate_comfyui_installation(config["comfyui_path"], config["venv_path"])
    if issues:
        console.print("\n[bold red]Configuration Issues:[/bold red]")
        for issue in issues:
            console.print(f"• [red]{issue}[/red]")
        return False
    
    # Setup comfy-cli if needed
    if not setup_comfy_cli(config):
        return False
    
    # Placeholder for ComfyUI server start
    console.print("[yellow]ComfyUI server start functionality will be implemented here.[/yellow]")
    console.print("This will include:")
    console.print("• [dim]Start ComfyUI with proper arguments[/dim]")
    console.print("• [dim]Configure network settings[/dim]")
    console.print("• [dim]Display access URLs[/dim]")
    console.print("• [dim]Monitor server status[/dim]")
    
    return True

def manage_custom_nodes():
    """Manage ComfyUI custom nodes"""
    console.print("\n[bold blue]ComfyUI Custom Node Management[/bold blue]")
    console.print("=" * 50)
    
    # Get current configuration
    config = get_current_configuration()
    if not config:
        console.print("[red]No ComfyUI configuration found.[/red]")
        console.print("Please configure ComfyUI first using 'Configure ComfyUI' option.")
        return False
    
    print_status(f"Using configuration: {config['name']}", "info")
    
    # Setup comfy-cli if needed
    if not setup_comfy_cli(config):
        return False
    
    options = [
        ("Show all custom nodes", "comfy node show all"),
        ("Show installed nodes", "comfy node simple-show installed"),
        ("Show available nodes", "comfy node show not-installed"),
        ("Update all nodes", "comfy node update all"),
        ("Install custom node", "comfy node install"),
        ("Save snapshot", "comfy node save-snapshot"),
        ("Restore snapshot", "comfy node restore-snapshot"),
        ("Back", None),
    ]

    subtitle = f"Active: {config['name']}"
    node_menu = BaseMenu(
        title="Custom Node Management",
        subtitle=subtitle,
        options=options,
        breadcrumbs=["ComfyUI", "Custom Nodes"],
        help_lines=[
            "Show all: List every known custom node repository.",
            "Installed: Show nodes currently installed in your setup.",
            "Available: Nodes that are known but not installed.",
            "Update all: Pull latest changes for all custom nodes.",
            "Install: Install a node by name (e.g., ComfyUI-Impact-Pack).",
            "Snapshots: Save or restore the custom_nodes folder state.",
        ],
    )
    
    while True:
        try:
            choice_idx = node_menu.run()
            
            if choice_idx == len(options) - 1:  # Back
                break
            
            desc, base_cmd = options[choice_idx]
            
            if choice_idx == 0:  # Show all custom nodes
                print_status("Fetching all custom nodes...", "info")
                run_comfy_command(config, ["node", "show", "all"])
                
            elif choice_idx == 1:  # Show installed nodes
                print_status("Fetching installed nodes...", "info")
                run_comfy_command(config, ["node", "simple-show", "installed"])
                
            elif choice_idx == 2:  # Show available nodes
                print_status("Fetching available nodes...", "info")
                run_comfy_command(config, ["node", "show", "not-installed"])
                
            elif choice_idx == 3:  # Update all nodes
                if Confirm.ask("Update all custom nodes?"):
                    print_status("Updating all custom nodes...", "info")
                    run_comfy_command(config, ["node", "update", "all"])
                
            elif choice_idx == 4:  # Install custom node
                node_name = Prompt.ask("Enter custom node name (e.g., ComfyUI-Impact-Pack)")
                if node_name:
                    print_status(f"Installing {node_name}...", "info")
                    run_comfy_command(config, ["node", "install", node_name])
                
            elif choice_idx == 5:  # Save snapshot
                snapshot_name = Prompt.ask("Enter snapshot name", default="default")
                print_status(f"Saving snapshot: {snapshot_name}...", "info")
                run_comfy_command(config, ["node", "save-snapshot", snapshot_name])
                
            elif choice_idx == 6:  # Restore snapshot
                # First show available snapshots
                print_status("Available snapshots:", "info")
                run_comfy_command(config, ["node", "snapshot-list"])
                
                snapshot_name = Prompt.ask("Enter snapshot name to restore")
                if snapshot_name:
                    if Confirm.ask(f"Restore snapshot '{snapshot_name}'?"):
                        print_status(f"Restoring snapshot: {snapshot_name}...", "info")
                        run_comfy_command(config, ["node", "restore-snapshot", snapshot_name])
            
            console.print("\n[dim]Press any key to continue...[/dim]")
            input()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("\n[dim]Press any key to continue...[/dim]")
            input()
    
    return True

def manage_models():
    """Manage ComfyUI models"""
    console.print("\n[bold blue]ComfyUI Model Management[/bold blue]")
    console.print("=" * 50)
    
    # Get current configuration
    config = get_current_configuration()
    if not config:
        console.print("[red]No ComfyUI configuration found.[/red]")
        console.print("Please configure ComfyUI first using 'Configure ComfyUI' option.")
        return False
    
    print_status(f"Using configuration: {config['name']}", "info")
    
    # Setup comfy-cli if needed
    if not setup_comfy_cli(config):
        return False
    
    options = [("Download model", "comfy model download"), ("Back", None)]
    subtitle = f"Active: {config['name']}"
    model_menu = BaseMenu(
        title="Model Management",
        subtitle=subtitle,
        options=options,
        breadcrumbs=["ComfyUI", "Models"],
        help_lines=[
            "Download model: Provide a CivitAI or HuggingFace URL.",
            "Relative path: Optional subfolder under models/ to place the file.",
            "Tokens: Set API tokens when prompted for protected downloads.",
        ],
    )
    
    while True:
        try:
            choice_idx = model_menu.run()
            
            if choice_idx == len(options) - 1:  # Back
                break
            
            desc, base_cmd = options[choice_idx]
            
            if choice_idx == 0:  # Download model
                url = Prompt.ask("Enter model URL (CivitAI, HuggingFace, etc.)")
                if url:
                    relative_path = Prompt.ask("Enter relative path (optional, press Enter to skip)", default="")
                    cmd = ["model", "download", "--url", url]
                    if relative_path:
                        cmd.extend(["--relative-path", relative_path])
                    
                    # Handle tokens for different platforms
                    if "civitai.com" in url.lower():
                        token = Prompt.ask("Enter CivitAI API token (required for most models, press Enter to skip)", default="")
                        if token:
                            cmd.extend(["--set-civitai-api-token", token])
                    elif "huggingface.co" in url.lower():
                        token = Prompt.ask("Enter HuggingFace token (optional, press Enter to skip)", default="")
                        if token:
                            cmd.extend(["--set-hf-api-token", token])
                    
                    print_status(f"Downloading model from {url}...", "info")
                    run_comfy_command(config, cmd)
            
            console.print("\n[dim]Press any key to continue...[/dim]")
            input()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("\n[dim]Press any key to continue...[/dim]")
            input()
    
    return True

def manage_comfyui_manager():
    """Manage ComfyUI-Manager"""
    console.print("\n[bold blue]ComfyUI-Manager Management[/bold blue]")
    console.print("=" * 50)
    
    # Get current configuration
    config = get_current_configuration()
    if not config:
        console.print("[red]No ComfyUI configuration found.[/red]")
        console.print("Please configure ComfyUI first using 'Configure ComfyUI' option.")
        return False
    
    print_status(f"Using configuration: {config['name']}", "info")
    
    # Setup comfy-cli if needed
    if not setup_comfy_cli(config):
        return False
    
    options = [
        ("Enable GUI", "comfy manager enable-gui"),
        ("Disable GUI", "comfy manager disable-gui"),
        ("Clear reserved startup action", "comfy manager clear"),
        ("Back", None),
    ]
    subtitle = f"Active: {config['name']}"
    manager_menu = BaseMenu(
        title="ComfyUI-Manager Management",
        subtitle=subtitle,
        options=options,
        breadcrumbs=["ComfyUI", "Manager"],
        help_lines=[
            "Enable GUI: Start ComfyUI-Manager web UI when ComfyUI launches.",
            "Disable GUI: Turn off Manager UI integration.",
            "Clear: Remove any reserved startup action for Manager.",
        ],
    )
    
    while True:
        try:
            choice_idx = manager_menu.run()
            
            if choice_idx == len(options) - 1:  # Back
                break
            
            desc, base_cmd = options[choice_idx]
            
            if choice_idx == 0:  # Enable GUI
                print_status("Enabling ComfyUI-Manager GUI...", "info")
                run_comfy_command(config, ["manager", "enable-gui"])
                
            elif choice_idx == 1:  # Disable GUI
                print_status("Disabling ComfyUI-Manager GUI...", "info")
                run_comfy_command(config, ["manager", "disable-gui"])
                
            elif choice_idx == 2:  # Clear reserved startup action
                print_status("Clearing reserved startup action...", "info")
                run_comfy_command(config, ["manager", "clear"])
            
            console.print("\n[dim]Press any key to continue...[/dim]")
            input()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("\n[dim]Press any key to continue...[/dim]")
            input()
    
    return True

def show_status():
    """Show ComfyUI status"""
    console.print("\n[bold blue]ComfyUI Status[/bold blue]")
    console.print("=" * 50)
    
    # Get current configuration
    config = get_current_configuration()
    if not config:
        console.print("[red]No ComfyUI configuration found.[/red]")
        console.print("Please configure ComfyUI first using 'Configure ComfyUI' option.")
        return False
    
    print_status(f"Using configuration: {config['name']}", "info")
    
    # Show configuration details
    console.print(f"\n[bold cyan]Configuration Details:[/bold cyan]")
    console.print(f"• Name: {config['name']}")
    console.print(f"• Type: {config['type']}")
    console.print(f"• ComfyUI Path: {config['comfyui_path']}")
    console.print(f"• Venv Path: {config['venv_path']}")
    
    # Validate installation
    issues = validate_comfyui_installation(config["comfyui_path"], config["venv_path"])
    if issues:
        console.print("\n[bold red]Issues Found:[/bold red]")
        for issue in issues:
            console.print(f"• [red]{issue}[/red]")
    else:
        console.print("\n[bold green]✓ Configuration is valid[/bold green]")
    
    # Check if ComfyUI is running
    console.print("\n[bold cyan]Process Status:[/bold cyan]")
    try:
        # Check for running ComfyUI processes
        result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
        if result.returncode == 0:
            console.print("• [green]ComfyUI appears to be running[/green]")
        else:
            console.print("• [yellow]ComfyUI is not running[/yellow]")
    except:
        console.print("• [dim]Unable to check process status[/dim]")
    
    return True

class ComfyUIMenu:
    def __init__(self):
        self.console = Console()
        self.options = [
            ("Configure ComfyUI", "Detect or configure ComfyUI installation"),
            ("Manage Custom Nodes", "Install and manage custom nodes"),
            ("Manage Models", "Download and manage models"),
            ("Manage ComfyUI-Manager", "Enable/disable ComfyUI-Manager GUI"),
            ("Show Status", "Check ComfyUI status and info"),
            ("Back", "Return to main menu"),
        ]

    def run(self) -> int:
        current_config = get_current_configuration()
        subtitle = (
            f"Active: {current_config['name']}" if current_config else "No active configuration"
        )
        menu = BaseMenu(
            title="ComfyUI Management",
            subtitle=subtitle,
            options=self.options,
            breadcrumbs=["ComfyUI"],
            help_lines=[
                "Configure ComfyUI: Detect or add your ComfyUI installation paths.",
                "Manage Custom Nodes: Install/update nodes, save/restore snapshots.",
                "Manage Models: Download models from CivitAI/HuggingFace.",
                "ComfyUI-Manager: Enable/disable the GUI manager extension.",
                "Status: Validate installation and view process status.",
            ],
        )
        return menu.run()

class ConfigurationMenu:
    def __init__(self):
        self.console = Console()
        self.options = [
            ("Auto-detect Templates", "Automatically detect ComfyUI installations"),
            ("List Configurations", "Show all available configurations"),
            ("Select Configuration", "Choose a configuration to use"),
            ("Add Custom Configuration", "Manually add a configuration"),
            ("Back", "Return to ComfyUI menu"),
        ]

    def run(self) -> int:
        current_config = get_current_configuration()
        subtitle = (
            f"Active: {current_config['name']}" if current_config else "No active configuration"
        )
        menu = BaseMenu(
            title="ComfyUI Configuration",
            subtitle=subtitle,
            options=self.options,
            breadcrumbs=["ComfyUI", "Configuration"],
            help_lines=[
                "Auto-detect: Search common paths for ComfyUI installations.",
                "List: View all detected and saved configurations.",
                "Select: Choose which configuration to use by default.",
                "Add Custom: Manually specify ComfyUI and venv paths.",
            ],
        )
        return menu.run()

def show_configuration_menu():
    """Show configuration submenu"""
    menu = ConfigurationMenu()
    
    while True:
        try:
            selected_option = menu.run()
            
            if selected_option == 0:  # Auto-detect Templates
                console.clear()
                detected = detect_comfyui_templates()
                if detected:
                    console.print(f"\n[bold green]Found {len(detected)} ComfyUI installation(s):[/bold green]")
                    
                    # Display detected templates with paths
                    for i, template in enumerate(detected, 1):
                        console.print(f"\n[bold cyan]{i}. {template['name']}[/bold cyan]")
                        console.print(f"   ComfyUI Path: [black]{template['comfyui_path']}[/black]")
                        console.print(f"   Venv Path: [black]{template['venv_path']}[/black]")
                        
                        # Validate installation
                        issues = validate_comfyui_installation(template["comfyui_path"], template["venv_path"])
                        if issues:
                            console.print(f"   Status: [yellow]⚠ Issues found[/yellow]")
                            for issue in issues:
                                console.print(f"     • [red]{issue}[/red]")
                        else:
                            console.print(f"   Status: [green]✓ Valid installation[/green]")
                    
                    # Ask user to confirm and optionally set as current
                    console.print("\n[bold blue]Actions:[/bold blue]")
                    if len(detected) == 1:
                        if Confirm.ask(f"Set '{detected[0]['name']}' as current configuration?"):
                            settings = load_settings()
                            settings["last_used"] = detected[0]["name"]
                            
                            # Add to saved configs if not already there
                            if detected[0]["name"] not in [c["name"] for c in settings["configurations"]]:
                                settings["configurations"].append(detected[0])
                            
                            if save_settings(settings):
                                print_status(f"Configuration '{detected[0]['name']}' set as current!", "success")
                            else:
                                print_status("Failed to save configuration", "error")
                    else:
                        console.print("Multiple installations found. Use 'Select Configuration' to choose one.")
                else:
                    console.print("\n[yellow]No ComfyUI installations detected.[/yellow]")
                    console.print("\nMake sure ComfyUI is installed in one of these locations:")
                    console.print("• /workspace/ComfyUI (Standard)")
                    console.print("• /workspace/madapps/ComfyUI (Madiator2011's Better Slim)")
                    console.print("• Or use 'Add Custom Configuration' to specify custom paths")
                
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 1:  # List Configurations
                console.clear()
                list_configurations()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 2:  # Select Configuration
                console.clear()
                select_configuration()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 3:  # Add Custom Configuration
                console.clear()
                add_custom_configuration()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 4:  # Back
                break
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            continue

def show_comfyui_menu():
    """Show ComfyUI options menu with arrow key navigation"""
    menu = ComfyUIMenu()
    
    while True:
        try:
            selected_option = menu.run()
            
            if selected_option == 0:  # Configure ComfyUI
                console.clear()
                show_configuration_menu()
                
            elif selected_option == 1:  # Manage Custom Nodes
                console.clear()
                manage_custom_nodes()
                
            elif selected_option == 2:  # Manage Models
                console.clear()
                manage_models()
                
            elif selected_option == 3:  # Manage ComfyUI-Manager
                console.clear()
                manage_comfyui_manager()
                
            elif selected_option == 4:  # Show Status
                console.clear()
                show_status()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 5:  # Back
                break
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled by user[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            continue
