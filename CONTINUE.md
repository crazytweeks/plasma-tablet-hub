# CONTINUE — tablet-hub

Handoff file. Written 2026-10-17. Intended resume date: **2026-10-19** (about two
days later), in a **clean new session**. Read this first, then the README.

## Where this stands

- Repo: `crazytweeks/plasma-tablet-hub`, branch `main`, working tree clean.
- Version: `0.1.0-alpha.1`.
- Machine: the HP OmniBook X Flip 16 convertible, CachyOS, KDE Plasma 6 on
  Wayland.
- Config: `~/.config/tablet-hub/config.json` (seeded on install, edited by the
  tray).
- State: **installed and running**. Four user services active:
  `tablet-hub`, `tablet-keyboard-guard`, `pen-scroll`, `tabhub-gestures`.
- No root anywhere: everything is a user systemd service. The only privileged
  action is retiring a legacy root `pen-scroll.service` if one is present.

**Owner's own words:** "not working perfect, but seems to be working fine, I do
need some time to get used to it and test." So this session is about *use and
observation*, not a rewrite. Do not start refactoring until the owner has
actually exercised it.

## What works (verified on hardware)

- **Keyboard guard** — exclusively grabs the built-in keyboard via
  `SW_TABLET_MODE` while the lid is folded; grabs the live node if another tool
  re-emits a clone.
- **Pen scroll** — stylus grabbed and re-emitted through `uinput`; front side
  button → `left_click`, rear button (firmware reports it as an eraser switch)
  → `right_click`, tip-drag → scroll.
- **Gestures** — read-only 3/4/5-finger swipe and pinch mapped to desktops,
  overview, zoom, media. Does not grab, so ordinary touch is unaffected.
- **Tray** — control panel, compact right-click menu, settings tabs (tablet
  mode, pen, gestures, touch feedback), and a "Repair services…" action.

## Added just before this handoff

- `bin/tabhub_bus.py` — newline-JSON unix-socket event bus
  (`Broadcaster` / `Client`, `default_paths()`), sockets at
  `$XDG_RUNTIME_DIR/tabhub-pen.sock` and `tabhub-gestures.sock`. Both were
  verified `ESTABLISHED` with the tray.
- **Live test window** — Pen tab (Tip / Button 1 / Button 2 / Hover indicators,
  position pad, pressure bar, action log) and Gestures tab (live finger count,
  detected gesture → action, log), fed by the two buses.

Note there are deliberately **two live-test surfaces**: the preview tabs inside
`SettingsDialog` and the standalone `TestWindow` opened by the tray's
"Live test…" action. If one looks stale compared to the other, that is the bug
to chase — not a duplicated class to delete.

## The one thing that was silently wrong

`gestures.enabled` had been switched **off** in the live config. That is why
gestures appeared dead. It has been re-enabled and `tabhub-gestures` restarted.
If gestures stop responding again, check that flag first — the tray writes this
file.

## What the owner still needs to test (ask for these first)

1. Open the tray's **Live test…** window.
2. Pen: press Button 1, press Button 2, hover, then tip-drag to scroll. Does the
   log show the right event for each?
3. Touchscreen: 3-finger and 4-finger swipes and pinches. Does the log show the
   detected gesture and the action it fired?
4. Anything that feels wrong while using the laptop normally as a tablet.

The owner's answers to these decide what gets built next.

## Planned next features

- **Feature C — pen visual feedback.** A ripple at the stylus point, optional
  haptics, long-press → context menu. Groundwork already exists: the config has
  a `pen_visual` block (`enabled: false`, `style: "ripple"`, `size`, `color`)
  and `effects.touch_points` already drives KWin's "ripple under each finger"
  for touch. No UI or daemon path consumes `pen_visual` yet.
- **Feature D — OS polish.** On-screen keyboard auto-show when the lid folds,
  and touch scaling.

## Constraints and ground rules

- Python 3 + `PyQt6`, `evdev`, `libevdev`; `ydotool` + `ydotoold` for
  key-emitting actions. User must be in the `input` group with `/dev/uinput`
  writable.
- Devices are matched by evdev **name**, never by `/dev/input/eventN`.
- Installation is **copy** by default; after editing anything, re-run
  `./install.sh` (or use `./install.sh --link` while developing).
- Do not run builds, installs, or watchers inside a network mount.
- Never leave a grab able to outlive the daemon — the kernel drops `EVIOCGRAB`
  on death, which is the safety net; keep it that way.

## Commands

```sh
# state of everything
systemctl --user status tablet-hub pen-scroll tabhub-gestures tablet-keyboard-guard

# follow one daemon's output
journalctl --user -u tabhub-gestures -f

# re-install after edits
cd ~/tablet-hub && ./install.sh

# see the raw event buses
ls -l "$XDG_RUNTIME_DIR"/tabhub-*.sock
```

## Don't

- Don't touch the `flash-lightning` monorepo, Coolify, or anything under
  `apps/` from this session.
- Don't start `mesh-hub` work here — that is a separate repo
  (`crazytweeks/mesh-hub`, `~/mesh-hub`) and a separate session.
- Don't rewrite working parts to "clean them up". Report, get the owner's
  read, then change one thing at a time.
