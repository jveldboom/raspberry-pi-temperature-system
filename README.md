# Raspberry Pi Temperature Sensor

This project creates a temperature and humidity sensor that exports metrics in Prometheus format.

## Hardware Requirements

- Raspberry Pi Zero 2 W
- AM2302 (DHT22) Temperature/Humidity Sensor
- MicroSD card (8GB or larger)
- Power supply (5V, 2A recommended)

## Sensor & Wiring Guide
Originally used the [DHT11](https://www.amazon.com/gp/product/B01H3J3H82/) but wanted something more accurate so went with [AM2302 Temperature & Humidity Sensor](https://www.amazon.com/gp/product/B073F472JL) or a [4 Pack](https://www.amazon.com/dp/B0FCLX5GTZ)

### Wiring Guide

Connect the AM2302 sensor to your Raspberry Pi:
```
AM2302 Sensor → Raspberry Pi Zero 2 W
----------------------------------------
VCC (Pin 1)   → 5V (Pin 1)
DATA (Pin 2)  → GPIO 4 (Pin 7)
GND (Pin 3)   → Ground (Pin 6)
```

[Raspberry Pi Pin Layout Guide](https://pinout.xyz/)
<details>
<summary> AM2302 Diagram</summary>

![wiring](./docs/sensor-AM2302-wiring.jpg)

</details>

## Software Installation

### Step 1: Flash Raspberry Pi OS

1. Download & install [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Insert your microSD card
3. In Raspberry Pi Imager:
  - **Device:** Raspberry Pi Zero 2 W
  - **OS:** Raspberry Pi OS Lite (64-bit) (in Raspberry Pi OS (other))
  - **Storage:** Your SD card
  - **Customization:**
    - **Hostname:** `sensor-pi` (should be unique for each device as we will reference this later)
    - **Localization:** (optional)
    - **User:**
      - Username: `pi`
      - Password: [choose a secure password]
    - **Wi-Fi:**
      - Choose network type (secure or open)
      - SSID: [2.4 GHz wifi network name]
      - Password: [wifi password]
    - **Remote access:** Enable SSH & use password authentication

4. Click **WRITE** to start

### Step 2: Boot and Wait

1. Insert the SD card into your Raspberry Pi Zero 2 W
2. Connect power
3. Wait 2-5 minutes for first boot

### Step 3: Run Automated Setup

SSH into your Pi:
```bash
ssh pi@sensor-pi.local
# pi@<hostname>.local
# Or use IP address: ssh pi@192.168.x.x
```

Then run the automated setup:
```bash
curl -L https://raw.githubusercontent.com/jveldboom/raspberry-pi-temperature-system/main/setup.sh | bash
```

The installation takes 10-15 minutes depending on your internet & SD card speed and will:
- Update the system
- Install required dependencies
- Install the sensor script
- Create and start the systemd service
- Configure automatic startup on boot

## Verification

### Check if the sensor is running:
```bash
sudo systemctl status temp-sensor
```

You should see `Active: active (running)` in green.

### View real-time sensor readings:
```bash
sudo journalctl -u temp-sensor -f
```

You should see output like:
```
Temp: 69.8°F (21.0°C), Humidity: 51.4%
```

### Check Prometheus metrics:
```bash
curl http://localhost:8000/metrics
```

### Test from another device:

From your computer, open a browser and go to:
```bash
http://<HOSTNAME>.local:8000/metrics

# or use ip address
http://192.168.x.x:8000/metrics
```


## Updating
To update to the latest version:

```bash
curl -L https://raw.githubusercontent.com/jveldboom/raspberry-pi-temperature-system/main/update.sh | bash

# Or to update to a specific branch/tag:
curl -L https://raw.githubusercontent.com/jveldboom/raspberry-pi-temperature-system/main/update.sh | bash -s v1.0.0
```

## Useful Commands
```bash
# View live sensor output
sudo journalctl -u temp-sensor -f

# Restart service
sudo systemctl restart temp-sensor

# Stop service
sudo systemctl stop temp-sensor

# Start service
sudo systemctl start temp-sensor

# Disable autostart
sudo systemctl disable temp-sensor

# Re-enable autostart
sudo systemctl enable temp-sensor

# Edit sensor script
nano /home/pi/temp-sensor.py

# Test script manually (stop service first)
sudo systemctl stop temp-sensor
python3 /home/pi/temp-sensor.py
```

## Troubleshooting

### Service won't start
```bash
# Check service status
sudo systemctl status temp-sensor

# View logs
sudo journalctl -u temp-sensor -f
sudo journalctl -u temp-sensor --since today
```

### Sensor Errors
- Check your wiring connections - [Raspberry Pi pinout diagram](https://pinout.xyz/)
  - Avoid GPIO 14 and 15 — these are reserved for UART (serial console) and are active during boot, which can interfere with sensor initialization
  - GPIO 4 is recommended for the data line
- Verify GPIO pin number in config matches your wiring
- Make sure sensor has power (5V recommended for AM2302)
