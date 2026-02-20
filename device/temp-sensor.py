#!/usr/bin/env python3
"""
Temperature and Humidity Sensor - Prometheus Exporter
Reads from AM2302 (DHT22) sensor and exports metrics for Prometheus
"""

from prometheus_client import start_http_server, Gauge
import board
import adafruit_dht
import time
import os

# Configuration
CONFIG = {
    "gpio_pin": board.D4,       # GPIO4 (physical pin 7)
    "port": 8000,               # Prometheus metrics port
    "read_interval": 10,        # Seconds between readings
    "location": "default",      # Default location (can be overridden by SENSOR_LOCATION env var)
}

# Prometheus metrics
temperature_celsius = Gauge(
    'sensor_temperature_celsius',
    'Temperature reading in Celsius',
    ['location']
)

temperature_fahrenheit = Gauge(
    'sensor_temperature_fahrenheit',
    'Temperature reading in Fahrenheit',
    ['location']
)

humidity = Gauge(
    'sensor_humidity_percent',
    'Relative humidity percentage',
    ['location']
)

read_errors = Gauge(
    'sensor_read_errors_total',
    'Total number of failed sensor reads'
)

last_successful_read = Gauge(
    'sensor_last_successful_read_timestamp_seconds',
    'Timestamp of last successful sensor read'
)

# Initialize sensor
dht_device = adafruit_dht.DHT22(CONFIG["gpio_pin"])

# Track metrics
error_count = 0

def read_sensor():
    """Read temperature and humidity from sensor. Returns (temp_c, humidity) or (None, None) on error."""
    try:
        temp_c = dht_device.temperature
        humid = dht_device.humidity
        if temp_c is not None and humid is not None:
            return temp_c, humid
    except Exception as e:
        print(f"Sensor read error: {e}")
    return None, None

def update_metrics():
    """Read sensor and update Prometheus metrics"""
    global error_count
    temp_c, humid = read_sensor()

    if temp_c is not None and humid is not None:
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        temperature_celsius.labels(location=LOCATION).set(temp_c)
        temperature_fahrenheit.labels(location=LOCATION).set(temp_f)
        humidity.labels(location=LOCATION).set(humid)
        last_successful_read.set(time.time())
        print(f"Temp: {temp_f:.1f}°F ({temp_c:.1f}°C), Humidity: {humid:.1f}%")
    else:
        error_count += 1
        read_errors.set(error_count)
        print(f"Failed to read sensor (total errors: {error_count})")

def main():
    global LOCATION
    LOCATION = os.environ.get('SENSOR_LOCATION', CONFIG["location"])

    # Verify sensor is working before starting server
    print("Checking sensor...")
    if read_sensor() == (None, None):
        raise Exception("Sensor not responding, will retry")

    print(f"Starting sensor on port {CONFIG['port']}, location: {LOCATION}")
    start_http_server(CONFIG["port"])

    while True:
        update_metrics()
        time.sleep(CONFIG["read_interval"])

if __name__ == '__main__':
    main()
