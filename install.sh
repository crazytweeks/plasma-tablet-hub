#!/usr/bin/env bash
#
# tablet-hub installer — deploys the tray app and its user-space daemons into
# the current user's home. No root is required for the install itself; the only
# privileged action is retiring a legacy root pen-scroll.service if present.
#
# Usage:
#   ./install.sh          copy files into ~/.local/bin and ~/.config/systemd/user
#   ./install.sh --link   symlink instead of copy (handy while developing)
#   ./install.sh --uninstall
#
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
MODE=copy
case "${1:-}" in
  --link) MODE=link ;;
  --uninstall) exec "$HERE/uninstall.sh" ;;
  "") ;;
  *) echo "usage: $0 [--link|--uninstall]" >&2; exit 2 ;;
esac

BINDIR="$HOME/.local/bin"
UNITDIR="$HOME/.config/systemd/user"
CFGDIR="$HOME/.config/tablet-hub"
PENDIR="$HOME/.config/pen-scroll"
DATADIR="$HOME/.local/share/tablet-hub"

mkdir -p "$BINDIR" "$UNITDIR" "$CFGDIR" "$PENDIR" "$DATADIR"

VERSION=$(cat "$HERE/VERSION" 2>/dev/null || echo unknown)

place() {  # src dst perm
  local src=$1 dst=$2 perm=${3:-755}
  mkdir -p "$(dirname "$dst")"
  if [[ $MODE == link ]]; then
    ln -sfn "$src" "$dst"
  else
    rm -f "$dst"                 # replace any stale symlink with a real file
    install -m "$perm" "$src" "$dst"
  fi
}

echo "tablet-hub: installing ($MODE)"
for f in "$HERE"/bin/*; do
  [[ -f "$f" ]] || continue
  place "$f" "$BINDIR/$(basename "$f")" 755
  echo "  bin  $(basename "$f")"
done
for f in "$HERE"/systemd/user/*.service; do
  [[ -f "$f" ]] || continue
  place "$f" "$UNITDIR/$(basename "$f")" 644
  echo "  unit $(basename "$f")"
done
if [[ -f "$HERE/VERSION" ]]; then
  install -m 644 "$HERE/VERSION" "$DATADIR/VERSION"
  echo "  data VERSION ($VERSION)"
fi

if [[ ! -f "$CFGDIR/config.json" ]]; then
  install -m 644 "$HERE/config/config.json" "$CFGDIR/config.json"
  echo "  cfg  config.json (seeded)"
fi
if [[ ! -f "$PENDIR/env" ]]; then
  printf 'PEN_SCROLL_MM_PER_NOTCH=6\nPEN_SCROLL_INVERT=0\nPEN_SCROLL_START_MM=1.5\n' > "$PENDIR/env"
  echo "  cfg  pen-scroll/env (seeded)"
fi

systemctl --user daemon-reload
for u in tablet-keyboard-guard tablet-hub tabhub-gestures; do
  systemctl --user enable --now "$u.service" >/dev/null 2>&1 || true
  echo "  svc  $u enabled"
done
# pen-scroll can only grab the stylus once the legacy root service is gone.
if systemctl is-enabled pen-scroll.service >/dev/null 2>&1 \
   || systemctl is-active pen-scroll.service >/dev/null 2>&1; then
  systemctl --user disable --now pen-scroll.service >/dev/null 2>&1 || true
else
  systemctl --user enable --now pen-scroll.service >/dev/null 2>&1 || true
  echo "  svc  pen-scroll enabled"
fi

# Legacy root service still holding the stylus?
if systemctl is-enabled pen-scroll.service >/dev/null 2>&1; then
  echo
  echo "NOTE: a legacy root pen-scroll.service is still enabled and holds the"
  echo "      stylus. Retire it once so the user service can grab it:"
  echo
  echo "        sudo systemctl disable --now pen-scroll"
  echo
  echo "      (Or use 'Set up pen scrolling (user service)…' in the tray.)"
fi

echo
echo "tablet-hub $VERSION installed. Look for the tablet icon in the system tray."
