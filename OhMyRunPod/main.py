import argparse
import sys
from OhMyRunPod.modules.ssh_setup.ssh_setup import run_ssh_setup_script
from OhMyRunPod.modules.pod_info import print_pod_info
from OhMyRunPod.modules.tailscale_setup import run_tailscale_setup_script, get_auth_key
from OhMyRunPod.modules.file_transfer import show_file_transfer_menu
from OhMyRunPod.modules.comfyui import show_comfyui_menu
from OhMyRunPod.ui import InteractiveMenu
from rich.console import Console

console = Console()

def run_interactive_mode():
    """Run the interactive menu mode"""
    menu = InteractiveMenu()
    
    while True:
        try:
            selected_option = menu.run()
            
            if selected_option == 0:  # SSH Setup
                console.clear()
                console.print("[bold blue]SSH Setup[/bold blue]")
                console.print("=" * 50)
                run_ssh_setup_script()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 1:  # Pod Information
                console.clear()
                console.print("[bold blue]Pod Information[/bold blue]")
                console.print("=" * 50)
                print_pod_info()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 2:  # Tailscale Setup
                console.clear()
                console.print("[bold blue]Tailscale Setup[/bold blue]")
                console.print("=" * 50)
                auth_key = get_auth_key()
                if auth_key:
                    run_tailscale_setup_script(auth_key)
                else:
                    console.print("[red]No auth key provided. Setup cancelled.[/red]")
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 3:  # File Transfer
                console.clear()
                show_file_transfer_menu()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 4:  # ComfyUI
                console.clear()
                show_comfyui_menu()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 5:  # Exit
                console.print("[yellow]Goodbye![/yellow]")
                sys.exit(0)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("\n[dim]Press any key to continue...[/dim]")
            input()

def main():
    parser = argparse.ArgumentParser(description="OhMyRunPod Command Line Tool")
    parser.add_argument('--setup-ssh', action='store_true', help='Run the SSH setup script')
    parser.add_argument('--info', action='store_true', help='Display information about the Pod')
    parser.add_argument('--setup-tailscale', action='store_true', help='Run the Tailscale setup script')
    parser.add_argument('--file-transfer', action='store_true', help='Setup file transfer options')
    parser.add_argument('--comfyui', action='store_true', help='ComfyUI management options')

    args = parser.parse_args()

    # Check if any arguments were provided
    if len(sys.argv) == 1:
        # No arguments provided, run interactive mode
        run_interactive_mode()
    else:
        # Arguments provided, run in CLI mode
        if args.setup_ssh:
            run_ssh_setup_script()

        if args.info:
            print_pod_info()

        if args.setup_tailscale:
            auth_key = get_auth_key()
            run_tailscale_setup_script(auth_key)
        
        if args.file_transfer:
            show_file_transfer_menu()
        
        if args.comfyui:
            show_comfyui_menu()

if __name__ == "__main__":
    main()
