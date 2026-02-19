#!/usr/bin/env python3
"""
Temperature and Humidity Sensor - Prometheus Exporter
Reads from AM2302 (DHT22) sensor and exports metrics for Prometheus
"""

from prometheus_client import start_http_server, Gauge, Info
import board
import adafruit_dht
import time
import sys
from datetime import datetime

# Configuration
CONFIG = {
    "sensor_type": "AM2302",  # AM2302, DHT22, or DHT11
    "gpio_pin": board.D14,     # GPIO14 (physical pin 8)
    "port": 8000,
    "read_interval": 10,       # seconds between readings
}

# Prometheus metrics with proper naming and descriptions
temperature_celsius = Gauge(
    'sensor_temperature_celsius',
    'Temperature reading in Celsius',
    ['sensor_type', 'location']
)

temperature_fahrenheit = Gauge(
    'sensor_temperature_fahrenheit',
    'Temperature reading in Fahrenheit',
    ['sensor_type', 'location']
)

humidity = Gauge(
    'sensor_humidity_percent',
    'Relative humidity percentage',
    ['sensor_type', 'location']
)

read_errors = Count(
    'sensor_read_errors_total',
    'Total number of failed sensor reads'
)

last_successful_read = Gauge(
    'sensor_last_successful_read_timestamp_seconds',
    'Timestamp of last successful sensor read'
)

sensor_info = Info(
    'sensor',
    'Information about the sensor'
)

# Initialize sensor
dht_device = adafruit_dht.DHT22(CONFIG["gpio_pin"])

# Track metrics
error_count = 0
LOCATION = "default"


def read_sensor():
    """
    Read temperature and humidity from sensor.
    Returns: (temperature_c, humidity_pct) or (None, None) on error
    """
    try:
        temp_c = dht_device.temperature
        humid = dht_device.humidity

        if temp_c is not None and humid is not None:
            return temp_c, humid
        return None, None

    except RuntimeError as e:
        print(f"RuntimeError reading sensor (this is normal occasionally): {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error reading sensor: {e}")
        return None, None


def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit"""
    return celsius * 9.0 / 5.0 + 32.0


def update_metrics():
    """Read sensor and update Prometheus metrics"""
    global error_count

    temp_c, humid = read_sensor()

    if temp_c is not None and humid is not None:
        temp_f = celsius_to_fahrenheit(temp_c)

        labels = {'sensor_type': CONFIG["sensor_type"], 'location': LOCATION}
        temperature_celsius.labels(**labels).set(temp_c)
        temperature_fahrenheit.labels(**labels).set(temp_f)
        humidity.labels(**labels).set(humid)

        last_successful_read.set(time.time())

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Temp: {temp_f:.1f}°F ({temp_c:.1f}°C), Humidity: {humid:.1f}%")
    else:
        error_count += 1
        read_errors.set(error_count)
        print(f"Failed to read sensor (total errors: {error_count})")


def main():
    """Main function"""
    global LOCATION

    import os
    LOCATION = os.environ.get('SENSOR_LOCATION', 'default')

    sensor_info.info({
        'type': CONFIG["sensor_type"],
        'gpio_pin': str(CONFIG["gpio_pin"]),
        'location': LOCATION,
        'version': '2.0'
    })

    print(f"Starting Prometheus metrics server on port {CONFIG['port']}...")
    start_http_server(CONFIG["port"])
    print(f"Metrics available at http://<raspberry-pi-ip>:{CONFIG['port']}/metrics")
    print(f"Reading sensor every {CONFIG['read_interval']} seconds...")
    print(f"Location: {LOCATION}")
    print("Press Ctrl+C to exit\n")

    try:
        while True:
            update_metrics()
            time.sleep(CONFIG["read_interval"])

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        dht_device.exit()
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        dht_device.exit()
        sys.exit(1)


if __name__ == '__main__':
    main()
