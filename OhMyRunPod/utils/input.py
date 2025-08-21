import sys
from typing import Union, Dict

from .term import supports_raw_input


Key = Union[str, Dict[str, int], Dict[str, str]]


def _read_key_raw() -> Key:
    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        # Handle escape sequences for arrows
        if ch == "\x1b":
            next1 = sys.stdin.read(1)
            if next1 == "[":
                next2 = sys.stdin.read(1)
                if next2 == "A":
                    return "UP"
                if next2 == "B":
                    return "DOWN"
            # Bare ESC
            return "ESC"
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch.isdigit():
            return {"number": int(ch)}
        if ch.isalpha():
            return {"letter": ch.lower()}
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _read_line() -> Key:
    try:
        line = input("")
    except EOFError:
        return "ESC"
    line = line.strip()
    if not line:
        return "ENTER"
    # Multi-digit support
    if line.isdigit():
        try:
            return {"number": int(line)}
        except Exception:
            return "ENTER"
    if len(line) == 1 and line.isalpha():
        return {"letter": line.lower()}
    return {"text": line}


def read_key() -> Key:
    """Read a single key or line depending on terminal capabilities.

    Returns one of:
    - "UP" | "DOWN" | "ENTER" | "ESC"
    - {"number": int}
    - {"letter": str}
    - {"text": str}
    """
    if supports_raw_input():
        try:
            return _read_key_raw()
        except Exception:
            # Fallback to line input
            return _read_line()
    else:
        return _read_line()

