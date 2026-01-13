#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_SRC="$ROOT/systemd/leetcode-bot.service"
TIMER_SRC="$ROOT/systemd/leetcode-bot.timer"
sudo cp "$SERVICE_SRC" /etc/systemd/system/
sudo cp "$TIMER_SRC" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now leetcode-bot.timer
echo "Enabled and started leetcode-bot.timer"
