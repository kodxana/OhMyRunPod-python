from typing import List, Tuple, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

from .input import read_key
from .term import supports_raw_input, supports_unicode


Option = Tuple[str, Optional[str]]


class BaseMenu:
    def __init__(
        self,
        title: str,
        options: List[Option],
        subtitle: Optional[str] = None,
        breadcrumbs: Optional[List[str]] = None,
        help_lines: Optional[List[str]] = None,
    ):
        self.console = Console()
        self.title = title
        self.subtitle = subtitle
        self.options = options
        self.current_option = 0
        self.breadcrumbs = breadcrumbs or []
        self._arrow_marker = "►" if supports_unicode() else ">"
        self.help_lines = help_lines or [
            "Navigation: ↑/↓ to move, Enter to select.",
            "Selection: Type a number (1-9) then Enter.",
            "Exit/Back: Press B for back or Q to quit.",
            "Help: Press H to toggle this help.",
            "Tip: In limited terminals, use numbers + Enter.",
        ]

    def _render_header(self):
        if self.breadcrumbs:
            crumbs = " > ".join(self.breadcrumbs)
            self.console.print(Text(crumbs, style="dim"))
        header_text = Text()
        header_text.append(self.title + "\n", style="bold blue")
        if self.subtitle:
            header_text.append(self.subtitle, style="dim")
        header_panel = Panel(header_text, border_style="blue", padding=(0, 1), box=box.ROUNDED)
        self.console.print(header_panel)

    def display_menu(self):
        try:
            if supports_raw_input():
                self.console.clear()
        except Exception:
            pass

        self._render_header()

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("", style="cyan", no_wrap=True)
        table.add_column("", style="white")

        for i, (label, desc) in enumerate(self.options):
            if i == self.current_option:
                marker = self._arrow_marker
                option_style = "bold green"
                desc_style = "green"
            else:
                marker = " "
                option_style = "white"
                desc_style = "dim"
            table.add_row(
                f"{marker} {label}",
                desc or "",
                style=option_style if i == self.current_option else None,
            )

        panel = Panel(Align.center(table), border_style="blue", padding=(1, 2), box=box.ROUNDED)
        self.console.print(panel)

        footer = Text(
            "1-9 select • ↑/↓ navigate • Enter confirm • B back • Q quit • H help",
            style="dim",
        )
        self.console.print(Align.center(footer))

    def show_help(self):
        try:
            if supports_raw_input():
                self.console.clear()
        except Exception:
            pass

        content = Text()
        for line in self.help_lines:
            content.append("• " + line + "\n")

        panel = Panel(
            content,
            title=Text(f"{self.title} Help", style="bold blue"),
            border_style="blue",
            padding=(1, 1),
            box=box.ROUNDED,
        )
        self.console.print(panel)
        self.console.print(Align.center(Text("Press Enter (or ESC) to return", style="dim")))

        # Wait for a confirming key
        while True:
            key = read_key()
            if key in ("ENTER", "ESC"):
                break
            if isinstance(key, dict) and key.get("letter") in ("q", "b", "h"):
                break
        self.display_menu()

    def run(self) -> int:
        """Render menu and return selected option index.

        ESC/Q returns the last option, which should be Back/Exit by convention.
        """
        self.display_menu()
        digit_buffer = ""

        while True:
            key = read_key()
            if key == "UP":
                if self.current_option > 0:
                    self.current_option -= 1
                self.display_menu()
                digit_buffer = ""
            elif key == "DOWN":
                if self.current_option < len(self.options) - 1:
                    self.current_option += 1
                self.display_menu()
                digit_buffer = ""
            elif key == "ENTER":
                if digit_buffer:
                    try:
                        idx = int(digit_buffer) - 1
                        if 0 <= idx < len(self.options):
                            return idx
                    except Exception:
                        pass
                    digit_buffer = ""
                    self.display_menu()
                    continue
                return self.current_option
            elif key == "ESC":
                return len(self.options) - 1
            elif isinstance(key, dict) and "number" in key:
                # Support multi-digit by buffering until Enter in raw mode, or immediate select in line mode
                n = key["number"]
                if supports_raw_input():
                    digit_buffer += str(n)
                    try:
                        idx = int(digit_buffer) - 1
                        if 0 <= idx < len(self.options):
                            self.current_option = idx
                            self.display_menu()
                    except Exception:
                        pass
                else:
                    idx = n - 1
                    if 0 <= idx < len(self.options):
                        return idx
            elif isinstance(key, dict) and "letter" in key:
                letter = key["letter"]
                if letter == "q":
                    return len(self.options) - 1
                if letter == "b":
                    return len(self.options) - 1
                if letter == "h":
                    self.show_help()
            else:
                # Ignore other keys
                pass
