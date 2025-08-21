import argparse
import os
import sys
from OhMyRunPod.modules.ssh_setup.ssh_setup import run_ssh_setup_script
from OhMyRunPod.modules.pod_info import print_pod_info
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
                
            elif selected_option == 2:  # File Transfer
                console.clear()
                show_file_transfer_menu()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 3:  # ComfyUI
                console.clear()
                show_comfyui_menu()
                console.print("\n[dim]Press any key to continue...[/dim]")
                input()
                
            elif selected_option == 4:  # Exit
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
    parser.add_argument('--file-transfer', action='store_true', help='Setup file transfer options')
    parser.add_argument('--comfyui', action='store_true', help='ComfyUI management options')
    parser.add_argument('--simple-ui', action='store_true', help='Force simple UI mode (no arrow keys)')

    args = parser.parse_args()

    # Check if any arguments were provided
    if len(sys.argv) == 1:
        # No arguments provided, run interactive mode
        if args.simple_ui:
            os.environ['OHMYRUNPOD_SIMPLE_UI'] = '1'
        run_interactive_mode()
    else:
        # Arguments provided, run in CLI mode
        if args.simple_ui and not any([args.setup_ssh, args.info, args.file_transfer, args.comfyui]):
            os.environ['OHMYRUNPOD_SIMPLE_UI'] = '1'
            run_interactive_mode()
            return
        if args.setup_ssh:
            run_ssh_setup_script()

        if args.info:
            print_pod_info()

        if args.file_transfer:
            show_file_transfer_menu()
        
        if args.comfyui:
            show_comfyui_menu()

if __name__ == "__main__":
    main()
