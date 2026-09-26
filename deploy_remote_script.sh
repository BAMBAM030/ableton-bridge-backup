#!/usr/bin/env bash
# Deploy AbletonBridge_Remote_Script -> Live User Library (with backup + verify).
# Usage: ./deploy_remote_script.sh [--dry-run]
# Touches ONLY "Remote Scripts/AbletonBridge". Live must be restarted afterwards.
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
SRC="$REPO/AbletonBridge_Remote_Script"
RS_ROOT="$HOME/Music/Ableton/User Library/Remote Scripts"
DST="$RS_ROOT/AbletonBridge"
BACKUPS="$RS_ROOT/Backups"
DRY=0; [[ "${1:-}" == "--dry-run" ]] && DRY=1

[[ "$DST" == */"Remote Scripts/AbletonBridge" ]] || { echo "Unsafe target: $DST"; exit 1; }
[[ -f "$SRC/__init__.py" ]] || { echo "Source missing: $SRC"; exit 1; }

echo "1/4 Syntax check"
python3 -m compileall -q -x '__pycache__' "$SRC" >/dev/null
find "$SRC" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true

echo "2/4 Changes:"
rsync -an --delete --exclude '__pycache__' --exclude '*.pyc' --itemize-changes "$SRC/" "$DST/" | sed 's/^/   /'
if [[ $DRY -eq 1 ]]; then echo "Dry run - nothing written."; exit 0; fi

echo "3/4 Backup + copy"
mkdir -p "$BACKUPS"
STAMP="$(date +%Y%m%d-%H%M%S)"
if [[ -d "$DST" ]]; then
  tar -czf "$BACKUPS/AbletonBridge-$STAMP.tgz" -C "$RS_ROOT" --exclude '__pycache__' AbletonBridge
  echo "   Backup: $BACKUPS/AbletonBridge-$STAMP.tgz"
fi
mkdir -p "$DST"
if ! rsync -a --delete --exclude '__pycache__' --exclude '*.pyc' "$SRC/" "$DST/"; then
  echo "Copy failed - restoring backup"; rm -rf "$DST"; tar -xzf "$BACKUPS/AbletonBridge-$STAMP.tgz" -C "$RS_ROOT"; exit 1
fi
rm -rf "$DST/__pycache__" "$DST/handlers/__pycache__"

echo "4/4 Verify"
if diff -rq -x '__pycache__' "$SRC" "$DST"; then
  echo "OK - identical. Restart Ableton Live to load the new script."
else
  echo "Verify FAILED"; exit 1
fi
