#!/bin/bash
# Backup to Seagate — LABEL/UUID safety, never sd letters.
# Seagate Cauldron: LABEL=Cauldron, UUID=EEDE-FDE7 (verify before every run).
# This script COPIES, it never deletes, formats, or erases any drive.
# Usage: bash scripts/backup-to-seagate.sh [source-dir] [dest-subdir]
# Default source: $HOME ; default dest: Seagate mount / chromebook-backup-<date>
set -e
SRC="${1:-$HOME}"
echo "Checking Seagate by LABEL (never by /dev/sdX)..."
SEAGATE_MOUNT="$(findmnt -n -o TARGET -S LABEL=Cauldron 2>/dev/null || true)"
if [ -z "$SEAGATE_MOUNT" ]; then
  echo "ERROR: Seagate (LABEL=Cauldron) is NOT mounted. Mount it in the file"
  echo "manager / by label first, then re-run. Do NOT guess a /dev/sdX device."
  echo "Refusing to copy from an empty or guessed mount."
  exit 1
fi
echo "Seagate mount: $SEAGATE_MOUNT"
echo "Source: $SRC  (size: $(du -sh "$SRC" 2>/dev/null | cut -f1))"
DEST="$SEAGATE_MOUNT/chromebook-backup-$(date +%Y-%m-%d)"
mkdir -p "$DEST"
echo "Copying to: $DEST"
rsync -a --info=progress2 "$SRC/" "$DEST/" || cp -a "$SRC/." "$DEST/"
echo "Verifying: file counts"
echo "  source files: $(find "$SRC" -type f | wc -l)"
echo "  dest files:   $(find "$DEST" -type f | wc -l)"
echo "Backup copy done. Source was NOT deleted. Verify the counts above"
echo "before any later erase step."
