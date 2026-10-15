#!/bin/bash
# Frees disk space on the GitHub runner and picks the biggest free disk for work.
set -e
echo "Disk before cleanup:"; df -h / /mnt 2>/dev/null || df -h /
sudo rm -rf /usr/share/dotnet /usr/local/lib/android /opt/ghc /usr/local/.ghcup \
  /opt/hostedtoolcache/CodeQL /usr/local/share/boost /usr/share/swift /usr/local/share/powershell || true
sudo docker image prune -af >/dev/null 2>&1 || true
ROOT_FREE=$(df --output=avail -k / | tail -1)
MNT_FREE=$(df --output=avail -k /mnt 2>/dev/null | tail -1 || echo 0)
if [ "${MNT_FREE:-0}" -gt "$ROOT_FREE" ]; then WORK=/mnt/work; else WORK=$HOME/work; fi
sudo mkdir -p "$WORK" && sudo chown -R "$USER" "$WORK"
echo "WORK=$WORK" >> "$GITHUB_ENV"
echo "Disk after cleanup:"; df -h / /mnt 2>/dev/null || df -h /
echo "Working in $WORK"
