from pathlib import Path
from sys import platform
from os import makedirs
import subprocess

if platform == "win32":
    FLOWAT_FILES_PATH = Path.home().joinpath("AppData", "Local", "Flowat")
    CONFIG_PATH = Path(FLOWAT_FILES_PATH, "configs")
    LOG_PATH = Path(FLOWAT_FILES_PATH, "logs")
else:
    FLOWAT_FILES_PATH = Path.home().joinpath(".local", "share", "Flowat")
    CONFIG_PATH = Path.home().joinpath(".config", "Flowat")
    LOG_PATH = Path.home().joinpath(".local", "state", "Flowat", "logs")

for dirpath in [FLOWAT_FILES_PATH, CONFIG_PATH, LOG_PATH]:
    makedirs(dirpath, exist_ok=True)


def sys_dark_mode() -> bool:
    """Detects if dark mode is currently enabled in the OS.

    :returns: `True` if dark mode is enabled, `False` otherwise.
    """
    match platform:
        case "linux":
            return _linux_dark_mode()
        case "win32":
            return False  # ignore while dark theme is not implemented for winforms
            # return _windows_dark_mode()
        case _:
            Warning(f"Not capable of detecting {platform=} dark mode.")
            return False


def _windows_dark_mode() -> bool:
    """Dectects if dark mode is enabled in a Windows system."""
    # stackoverflow.com/a/65349866
    # github.com/albertosottile/darkdetect/blob/master/darkdetect/_windows_detect.py
    try:
        import winreg
    except ImportError:
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        subkey = winreg.QueryValueEx(key=key, name="AppsUseLightTheme")[0]
        # subkey value is 1 when the system is using light mode
        return subkey == 0
    except FileNotFoundError:
        # assume light mode when key is not found
        return False


def _linux_dark_mode() -> bool:
    """Detects if dark mode is enabled in a GTK3/4 based GNU/Linux system.
    Will depend on `gsettings` being installed in the system to work properly.
    """
    result = subprocess.run(
        ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
        capture_output=True,
        text=True,
    )
    return "dark" in result.stdout.lower()


if sys_dark_mode():
    BG_COLOR = "#1e1e1e"
    FG_COLOR = "#e1e1e1"
else:
    if platform == "win32":
        BG_COLOR = "#f0f0f0"
    else:
        BG_COLOR = "#fff"
    FG_COLOR = "#1e1e1e"
