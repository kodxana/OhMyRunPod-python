import os
import sys


def is_tty() -> bool:
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except Exception:
        return False


def is_jupyter() -> bool:
    try:
        # Detect common Jupyter/Colab indicators
        from IPython import get_ipython  # type: ignore

        if get_ipython() is not None:
            return True
    except Exception:
        pass
    # Environment variables often present in notebook contexts
    for key in ("JPY_PARENT_PID", "COLAB_GPU", "BINDER_SERVICE_PORT"):
        if os.environ.get(key):
            return True
    return False


def simple_ui_enabled() -> bool:
    return os.environ.get("OHMYRUNPOD_SIMPLE_UI", "0") in ("1", "true", "True")


def supports_raw_input() -> bool:
    # Raw input is best avoided in notebook-like environments
    return is_tty() and not is_jupyter() and not simple_ui_enabled()


def supports_unicode() -> bool:
    try:
        # Try encoding a common glyph used in menus
        "\u25BA".encode(sys.stdout.encoding or "utf-8", errors="strict")
        return True
    except Exception:
        return False

