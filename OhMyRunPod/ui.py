import sys
import os
import termios
import tty
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.prompt import Prompt

class InteractiveMenu:
    def __init__(self):
        self.console = Console()
        self.current_option = 0
        self.options = [
            ("SSH Setup", "Configure SSH server and create connection scripts"),
            ("Pod Information", "Display RunPod environment information"),
            ("Tailscale Setup", "Install and configure Tailscale VPN"),
            ("File Transfer", "Setup file transfer with croc or SFTP"),
            ("ComfyUI", "Install and manage ComfyUI"),
            ("Exit", "Exit the application")
        ]
        
    def display_menu(self):
        self.console.clear()
        
        # Title
        title = Text("OhMyRunPod", style="bold blue")
        subtitle = Text("Runpod Environment Management Tool", style="dim")
        
        # Create menu table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("", style="cyan", no_wrap=True)
        table.add_column("", style="white")
        
        for i, (option, description) in enumerate(self.options):
            if i == self.current_option:
                marker = "►"
                option_style = "bold green"
                desc_style = "green"
            else:
                marker = " "
                option_style = "white"
                desc_style = "dim"
            
            table.add_row(
                f"{marker} {option}",
                description,
                style=option_style if i == self.current_option else None
            )
        
        # Create main panel
        panel_content = Align.center(table)
        panel = Panel(
            panel_content,
            title=title,
            subtitle=subtitle,
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        # Instructions
        instructions = Text("\nUse ↑/↓ arrows to navigate, Enter to select, ESC to exit, or type option number:", style="dim")
        self.console.print(Align.center(instructions))
        
        # Credits
        credits = Text("\nCreated by Madiator2011", style="dim italic")
        self.console.print(Align.center(credits))
    
    def navigate_up(self):
        if self.current_option > 0:
            self.current_option -= 1
    
    def navigate_down(self):
        if self.current_option < len(self.options) - 1:
            self.current_option += 1
    
    def get_selected_option(self):
        return self.current_option
    
    def get_char(self):
        """Get a single character from stdin"""
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return char
        except:
            # Fallback to input() if termios is not available
            return input()
    
    def run(self):
        """Run the interactive menu and return the selected option"""
        self.display_menu()
        
        while True:
            try:
                char = self.get_char()
                
                if char == '\x1b':  # ESC sequence
                    # Try to read the next two characters for arrow keys
                    try:
                        char2 = self.get_char()
                        char3 = self.get_char()
                        if char2 == '[':
                            if char3 == 'A':  # Up arrow
                                self.navigate_up()
                                self.display_menu()
                            elif char3 == 'B':  # Down arrow
                                self.navigate_down()
                                self.display_menu()
                    except:
                        # Just ESC key pressed
                        return len(self.options) - 1  # Exit option
                
                elif char == '\r' or char == '\n':  # Enter key
                    return self.current_option
                
                elif char == 'q' or char == 'Q':  # Q to quit
                    return len(self.options) - 1  # Exit option
                
                elif char.isdigit():  # Number selection
                    option_num = int(char)
                    if 1 <= option_num <= len(self.options):
                        return option_num - 1
                    
            except KeyboardInterrupt:
                return len(self.options) - 1  # Exit option
            except:
                # Fallback to number-based selection
                self.console.print("\n[yellow]Arrow keys not supported in this environment.[/yellow]")
                self.console.print("Please select an option by number:")
                for i, (option, _) in enumerate(self.options):
                    self.console.print(f"  [cyan]{i+1}[/cyan]. {option}")
                
                try:
                    choice = Prompt.ask("Enter your choice", choices=[str(i+1) for i in range(len(self.options))])
                    return int(choice) - 1
                except:
                    return len(self.options) - 1  # Exit option