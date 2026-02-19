#!/bin/bash
# Temperature Sensor Automated Setup Script
# For Raspberry Pi Zero 2 W with AM2302 (DHT22) sensor

set -e  # Exit on any error

# Configuration
REPO_URL="https://raw.githubusercontent.com/jveldboom/raspberry-pi-temperature-system/main"
INSTALL_DIR="/home/pi"

echo "=================================================="
echo "Temperature Sensor Setup - Starting Installation"
echo "=================================================="

# Check if running as correct user
if [ "$USER" != "pi" ] && [ "$SUDO_USER" != "pi" ]; then
    echo "Warning: This script should be run as user 'pi'"
    echo "Some file permissions may need manual adjustment"
fi

# Update system
echo ""
echo "[1/6] Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo ""
echo "[2/6] Installing system dependencies..."
sudo apt install -y python3-pip python3-dev python3-venv git curl

# Install Python libraries
echo ""
echo "[3/6] Installing Python libraries..."
pip3 install --break-system-packages adafruit-circuitpython-dht prometheus-client

# Download sensor script
echo ""
echo "[4/6] Downloading sensor script..."
curl -fsSL "${REPO_URL}/device/temp-sensor.py" -o "${INSTALL_DIR}/temp-sensor.py"
chmod +x "${INSTALL_DIR}/temp-sensor.py"
chown pi:pi "${INSTALL_DIR}/temp-sensor.py" 2>/dev/null || true

# Download and install systemd service
echo ""
echo "[5/6] Installing systemd service..."
sudo curl -fsSL "${REPO_URL}/device/temp-sensor.service" -o /etc/systemd/system/temp-sensor.service

# Enable and start service
echo ""
echo "[6/6] Enabling and starting sensor service..."
sudo systemctl daemon-reload
sudo systemctl enable temp-sensor.service
sudo systemctl start temp-sensor.service

# Wait a moment for service to start
sleep 3

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Service Status:"
sudo systemctl status temp-sensor.service --no-pager -l || true

echo ""
echo "Useful commands:"
echo "  View real-time logs:    sudo journalctl -u temp-sensor -f"
echo "  Check metrics:          curl http://localhost:8000/metrics"
echo "  Restart service:        sudo systemctl restart temp-sensor"
echo "  Stop service:           sudo systemctl stop temp-sensor"
echo "  View service status:    sudo systemctl status temp-sensor"
echo ""
echo "To customize the sensor location label:"
echo "  sudo systemctl edit temp-sensor"
echo "  Add: Environment=\"SENSOR_LOCATION=living_room\""
echo "  Then: sudo systemctl restart temp-sensor"
echo ""
echo "Configuration files:"
echo "  Sensor script:    ${INSTALL_DIR}/temp-sensor.py"
echo "  Service file:     /etc/systemd/system/temp-sensor.service"
echo ""
echo "Your sensor is now running and exporting Prometheus metrics!"
echo "Access metrics at: http://$(hostname -I | awk '{print $1}'):8000/metrics"
echo "=================================================="
