#!/bin/bash
# Temperature Sensor Update Script
# Updates sensor script and service from GitHub

set -e  # Exit on any error

# Configuration
REPO_URL="https://raw.githubusercontent.com/jveldboom/raspberry-pi-temperature-system"
INSTALL_DIR="/home/pi"
BRANCH="${1:-main}"  # Default to main, or use first argument

echo "=================================================="
echo "Temperature Sensor Update"
echo "=================================================="
echo "Updating from branch/tag: $BRANCH"
echo ""

# Stop service
echo "[1/3] Stopping sensor service..."
sudo systemctl stop temp-sensor.service

# Download updated files
echo ""
echo "[2/3] Downloading updated files..."
curl -fsSL "${REPO_URL}/${BRANCH}/device/temp-sensor.py" -o "${INSTALL_DIR}/temp-sensor.py"
chmod +x "${INSTALL_DIR}/temp-sensor.py"
chown pi:pi "${INSTALL_DIR}/temp-sensor.py" 2>/dev/null || true

sudo curl -fsSL "${REPO_URL}/${BRANCH}/device/temp-sensor.service" -o /etc/systemd/system/temp-sensor.service

# Restart service
echo ""
echo "[3/3] Restarting sensor service..."
sudo systemctl daemon-reload
sudo systemctl start temp-sensor.service

# Wait for service to start
sleep 2

echo ""
echo "=================================================="
echo "Update Complete!"
echo "=================================================="
echo ""
echo "Service Status:"
sudo systemctl status temp-sensor.service --no-pager -l || true
echo ""
echo "View logs: sudo journalctl -u temp-sensor -f"
echo "=================================================="
