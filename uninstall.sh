#!/usr/bin/env bash
#
# tablet-hub uninstaller — stops and removes the user services and the files
# the installer placed in the home directory. Leaves your config in place.
#
set -euo pipefail

BINDIR="$HOME/.local/bin"
UNITDIR="$HOME/.config/systemd/user"

for u in tablet-hub tablet-keyboard-guard pen-scroll tabhub-gestures; do
  systemctl --user disable --now "$u.service" >/dev/null 2>&1 || true
done

rm -f "$UNITDIR/tablet-hub.service" \
      "$UNITDIR/tablet-keyboard-guard.service" \
      "$UNITDIR/pen-scroll.service" \
      "$UNITDIR/tabhub-gestures.service"
for f in tablet-hub tablet-keyboard-guard pen-scroll tabhub-gestures tabhub_actions.py; do
  rm -f "$BINDIR/$f"
done
rm -f "$HOME/.local/share/tablet-hub/VERSION"
rmdir "$HOME/.local/share/tablet-hub" 2>/dev/null || true

systemctl --user daemon-reload
echo "tablet-hub removed. Config kept at ~/.config/tablet-hub and ~/.config/pen-scroll."
