#!/usr/bin/env python3
"""tabhub_actions: the shared action registry used by gestures and the tray.

Every gesture (and, later, pen buttons) maps to an action id from ACTIONS.
run_action() executes it with the best tool available on the system, silently
degrading if a helper is missing.

Run `tabhub-actions --list` to print the catalogue.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

HOME = os.path.expanduser("~")
ROTATE = os.path.join(HOME, ".local/bin/rotate-screen")

# id -> human label. Keep ids stable; they are stored in config.json.
ACTIONS: dict[str, str] = {
    "none": "Nothing",
    "prev_desktop": "Previous desktop",
    "next_desktop": "Next desktop",
    "overview": "Overview",
    "grid": "Window grid",
    "present_windows": "Present windows",
    "show_desktop": "Show desktop",
    "switch_window": "Switch window (Alt+Tab)",
    "close_window": "Close window (Alt+F4)",
    "zoom_in": "Zoom in",
    "zoom_out": "Zoom out",
    "volume_up": "Volume up",
    "volume_down": "Volume down",
    "volume_mute": "Mute",
    "play_pause": "Play / pause",
    "next_track": "Next track",
    "prev_track": "Previous track",
    "brightness_up": "Brightness up",
    "brightness_down": "Brightness down",
    "keyboard_toggle": "Toggle keyboard guard",
    "rotate_cycle": "Rotate screen (cycle)",
    "rotate_normal": "Rotate: landscape",
    "rotate_left": "Rotate: portrait left",
    "rotate_inverted": "Rotate: inverted",
    "rotate_right": "Rotate: portrait right",
    "screenshot": "Screenshot",
    "onscreen_keyboard": "On-screen keyboard",
    "lock_screen": "Lock screen",
}


def _spawn(cmd: list[str]) -> None:
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        pass


def _qdbus(*args: str) -> None:
    if shutil.which("qdbus6"):
        _spawn(["qdbus6", *args])


def _ydotool(*keys: str) -> None:
    if shutil.which("ydotool"):
        _spawn(["ydotool", "key", *keys])


def _have(tool: str) -> bool:
    return shutil.which(tool) is not None


def run_action(name: str) -> None:
    if not name or name == "none":
        return

    if name == "prev_desktop":
        _qdbus("org.kde.KWin", "/KWin", "org.kde.KWin.previousDesktop")
    elif name == "next_desktop":
        _qdbus("org.kde.KWin", "/KWin", "org.kde.KWin.nextDesktop")
    elif name == "show_desktop":
        _qdbus("org.kde.KWin", "/KWin", "org.kde.KWin.showDesktop", "true")
    elif name in ("overview", "grid", "present_windows"):
        label = {"overview": "Overview", "grid": "Grid View", "present_windows": "Present Windows"}[name]
        _qdbus(
            "org.kde.kglobalaccel", "/component/kwin",
            "org.kde.kglobalaccel.Component.invokeShortcut", label,
        )
    elif name == "switch_window":
        _ydotool("56:1", "15:1", "15:0", "56:0")  # Alt+Tab
    elif name == "close_window":
        _ydotool("56:1", "62:1", "62:0", "56:0")  # Alt+F4
    elif name == "zoom_in":
        _ydotool("29:1", "13:1", "13:0", "29:0")  # Ctrl+=
    elif name == "zoom_out":
        _ydotool("29:1", "12:1", "12:0", "29:0")  # Ctrl+-
    elif name in ("volume_up", "volume_down"):
        step = "5%+" if name == "volume_up" else "5%-"
        if _have("wpctl"):
            _spawn(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", step])
        elif _have("pactl"):
            _spawn(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "5%+" if name == "volume_up" else "-5%"])
    elif name == "volume_mute":
        if _have("wpctl"):
            _spawn(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
        elif _have("pactl"):
            _spawn(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
    elif name == "play_pause":
        _ydotool("164")
    elif name == "next_track":
        _ydotool("163")
    elif name == "prev_track":
        _ydotool("165")
    elif name == "brightness_up":
        _ydotool("225")
    elif name == "brightness_down":
        _ydotool("224")
    elif name == "keyboard_toggle":
        import json
        path = os.path.join(HOME, ".config/tablet-hub/config.json")
        try:
            with open(path) as fh:
                cfg = json.load(fh)
        except Exception:  # noqa: BLE001
            cfg = {}
        kg = cfg.setdefault("keyboard_guard", {})
        kg["enabled"] = not kg.get("enabled", True)
        try:
            with open(path, "w") as fh:
                json.dump(cfg, fh, indent=2)
        except Exception:  # noqa: BLE001
            pass
        _spawn(["systemctl", "--user", "restart", "tablet-keyboard-guard.service"])
    elif name == "screenshot":
        if _have("spectacle"):
            _spawn(["spectacle", "-b", "-n"])
    elif name == "lock_screen":
        _spawn(["loginctl", "lock-session"])
    elif name == "onscreen_keyboard":
        _qdbus("org.kde.kwin", "/VirtualKeyboard", "org.kde.kwin.VirtualKeyboard.setActive", "true")
    elif name.startswith("rotate_"):
        if os.path.exists(ROTATE):
            arg = {"rotate_cycle": "cycle", "rotate_normal": "normal", "rotate_left": "left",
                   "rotate_inverted": "inverted", "rotate_right": "right"}[name]
            if arg == "cycle":
                _spawn([ROTATE, "cycle"])
            else:
                _spawn([ROTATE, "set", arg])


if __name__ == "__main__":
    if "--list" in sys.argv:
        for k, v in ACTIONS.items():
            print(f"{k:20} {v}")
    else:
        run_action(sys.argv[1] if len(sys.argv) > 1 else "none")
