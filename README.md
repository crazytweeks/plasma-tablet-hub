# tablet-hub

Small user-space daemons + a tray app that make a **convertible Linux laptop**
genuinely usable in tablet mode on **KDE Plasma 6 Wayland**.

[![status: alpha](https://img.shields.io/badge/status-alpha-orange)](#status)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![platform: Linux](https://img.shields.io/badge/platform-Linux-informational)](#supported-systems)

> **Status: alpha (v0.1.0-alpha.1).** Only exercised on the hardware below.
> Expect rough edges; please report what breaks. See [CHANGELOG.md](CHANGELOG.md).

## Supported systems

Developed and tested on the combination below. Other Arch-based / KDE Plasma 6
Wayland setups will probably work, but the device names in the default config
are matched to this machine and may need editing for yours.

| | Tested on |
|---|---|
| **Laptop** | HP OmniBook X Flip Laptop **14-fm0xxx** (convertible), board `8D9F` |
| **Touchscreen digitizer** | ELAN `ELAN2514:00 04F3:442A` (with `... Stylus`, `... Keyboard`, `... Mouse` sub-devices) |
| **Touchpad** | ELAN `ELAN012A:00 04F3:32ED` |
| **Lid switch** | `Intel HID switches` (`SW_TABLET_MODE`) |
| **Distribution** | CachyOS Linux (Arch-based, `ID=arch`) |
| **Session** | KDE Plasma **6.7.5** / KWin **6.7.5**, Wayland (`XDG_SESSION_TYPE=wayland`) |
| **Kernel** | `7.2.9-2-cachyos`, x86_64 |

## Supported stylus

| | Tested on |
|---|---|
| **Stylus** | HP USB-C Rechargeable MBP2.0 pen (Microsoft Pen Protocol 2.0, MPP2.0) |
| **Model no.** | **TPA-M005P** |
| **Reports as** | `ELAN2514:00 04F3:442A Stylus` |

This pen has **two side buttons and no physical eraser**. Worth knowing because
the firmware reports them differently from what you might expect:

- The **front** side button (nearer the tip) emits `BTN_STYLUS`.
- The **rear** side button does **not** emit `BTN_STYLUS2` — instead the pen
  switches to the "eraser" tool (`BTN_TOOL_PEN=0`, then `BTN_TOOL_RUBBER=1`)
  and back. tablet-hub intercepts that toggle and maps it to an action
  (`right_click` by default) instead of letting the compositor erase, and
  handles the matching proximity events so the cursor does not flicker.
- Setting that button's action to **"Eraser (native tool)"** restores the
  original eraser behaviour for drawing apps.

If your pen reports a real `BTN_STYLUS2`, tablet-hub uses it directly and the
"rear button" behaves like any other button.

## What it does

| Piece | Purpose |
|---|---|
| `tablet-hub` (tray) | Control panel: toggles, screen rotation, settings, live pen/gesture test. Tap the tray icon for a finger-sized panel; right-click for the compact menu. |
| `tablet-keyboard-guard` | While the lid is folded (`SW_TABLET_MODE`), exclusively grabs the built-in keyboard so stray presses never reach apps. |
| `pen-scroll` | Stylus side-button + drag-scroll behaviour (grabs the pen, re-emits via `uinput` + a virtual pointer/wheel). |
| `tabhub-gestures` | Multi-finger touchscreen gestures (3/4/5-finger swipe/pinch) via KDE D-Bus + `ydotool`. |

## Install

```sh
git clone https://github.com/crazytweeks/plasma-tablet-hub.git ~/tablet-hub
cd ~/tablet-hub
./install.sh            # copy into ~/.local/bin + ~/.config/systemd/user
./install.sh --link     # symlink instead (for development)
./install.sh --uninstall
```

The installer enables the tray and keyboard guard, seeds config, and (if a
legacy root `pen-scroll.service` is present) prints the one command to retire
it:

```sh
sudo systemctl disable --now pen-scroll
```

## Requirements

- KDE Plasma 6 on Wayland (uses `qdbus6`, `kwriteconfig6`, `kcmshell6`).
- Python 3 with `PyQt6`, `evdev`, and `libevdev`
  (`python-pyqt6 python-evdev python-libevdev` on Arch).
- `ydotool` + a running `ydotoold` (for key-emitting gesture actions).
- Your user in the `input` group, and `/dev/uinput` writable by the user
  (usually via a `uaccess` udev rule).

## Config

`~/.config/tablet-hub/config.json` — seeded on install, edited by the tray.

- `keyboard_guard`: which evdev names to grab while folded, and the switch
  device/code used for detection.
- `pen_scroll`: `button1` (front side button, reported as `BTN_STYLUS`) and
  `button2` (rear side button — see the stylus notes above), plus `mm_per_notch`
  (scroll speed), `invert`, `start_mm` (click vs scroll threshold), `tip_scroll`
  (drag the tip to scroll), and `stylus_name`.
- `gestures`: `fingers`, thresholds, and `map` from gesture → action.
  Actions: `prev_desktop`, `next_desktop`, `overview`, `grid`, `show_desktop`,
  `zoom_in`, `zoom_out`, `volume_up`, `volume_down`, `play_pause`, `none`.
- `effects`: KWin `touch_points` and `show_click`.

## Design notes

- **No root, no device-number guessing.** Devices are matched by evdev *name*
  and capabilities, not `/dev/input/eventN` (which changes across reboots).
- **Grab safety.** `EVIOCGRAB` is dropped by the kernel if the grabber dies, so
  the keyboard or pen can never get stuck disabled.
- **Live-node grabbing.** If another tool (e.g. `vocalinux`) already holds the
  physical keyboard and re-emits a clone, the guard grabs the *clone* — the node
  the compositor actually reads.
- **Gestures don't grab.** `tabhub-gestures` reads the touchscreen read-only, so
  ordinary touch keeps working; only ≥N-finger motions trigger actions.

## Troubleshooting

- **Nothing happens / `[raw]` lines missing** — check the services:
  `systemctl --user status tablet-hub pen-scroll tabhub-gestures tablet-keyboard-guard`.
  Use the tray's **Live pen / gesture test…** window to see live events.
- **Pen buttons dead** — the pen must be in range and un-touched by another
  grabber. Confirm the stylus name with `libinput list-devices` or
  `grep -i stylus /proc/bus/input/devices`, and set `pen_scroll.stylus_name`
  to match.
- **Gestures need keys** — start `ydotoold` (or enable `ydotoold.service`).
- **Keyboard stays disabled** — the grab is released on exit; stop the guard
  with `systemctl --user stop tablet-keyboard-guard`.

## Status

Alpha. The event plumbing has been verified on the hardware above (button,
tip-scroll, and gesture paths), but behaviour on other digitizers, distros, and
Plasma versions is untested. Issues and hardware reports are welcome.

## License

[MIT](LICENSE).
