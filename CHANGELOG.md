# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0-alpha.1] - 2026-10-16

First public alpha. Everything here has only been exercised on the hardware
listed in the README, so treat it as experimental.

### Added

- `tablet-hub` — a KDE system-tray control panel with a finger-sized tablet
  panel, a compact right-click menu, and settings tabs for tablet mode, pen,
  gestures, and touch feedback. Includes a live pen/gesture test window and a
  "Repair services…" action.
- `tablet-keyboard-guard` — exclusively grabs the built-in keyboard (and
  optional touchpad) while the lid is folded, using `SW_TABLET_MODE`, so stray
  presses never reach applications. Grabs the live node when another tool
  (e.g. `vocalinux`) re-emits a clone.
- `pen-scroll` — grabs the stylus and re-emits it via `uinput`, remapping the
  two side buttons and adding drag-to-scroll with the pen tip. Front button is
  reported as `BTN_STYLUS`; the rear button is reported by the firmware as a
  switch to the eraser tool, which is intercepted and mapped to an action
  (`right_click` by default) instead of letting the compositor erase.
- `tabhub-gestures` — read-only multi-finger touchscreen gestures (3/4/5-finger
  swipe and pinch) mapped to desktop, overview, zoom, and media actions.
- A small newline-JSON unix-socket event bus (`tabhub_bus.py`) shared by the
  daemons and the tray for live state and activity.
- `install.sh` / `uninstall.sh` — user-space install into `~/.local/bin` and
  `~/.config/systemd/user`, with a copy or symlink mode.

### Notes

- No root required: everything runs as user systemd services. The only
  privileged action is retiring a legacy root `pen-scroll.service` if present.
- Devices are matched by evdev name and capabilities, never by
  `/dev/input/eventN`.

[Unreleased]: https://github.com/crazytweeks/plasma-tablet-hub/compare/v0.1.0-alpha.1...HEAD
[0.1.0-alpha.1]: https://github.com/crazytweeks/plasma-tablet-hub/releases/tag/v0.1.0-alpha.1
