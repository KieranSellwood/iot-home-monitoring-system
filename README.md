# iot-home-monitoring-system
An Iot System built with two components on a Raspberry Pi Pico W and Raspberry Pi 5, using MQTT to stream sensro data from embedded hardware to a structured SQLite database in real time.

## System Architecture
embedded_controller.py runs on the Raspberry Pi Pico W and handles all embedded hardware interaction. It reads temperature and humidity from a DHT11 sensor, detects motion via a PIR sensor, monitors an IR sensor for presence detection, and controls four LED outputs representing rooms in a simulated smart home. Push buttons toggle room lights, and a passive buzzer triggers a security alarm on motion detection. Component states are serialized as JSON and published to an MQTT broker once per second. The system also subscribes to a control topic, allowing remote actuation of lights and the alarm via MQTT messages from the Pi.
mqtt_logger.py runs on the Raspberry Pi 5 and acts as the data pipeline backend. It subscribes to the MQTT sensor topic, parses incoming JSON payloads, and writes structured records to a SQLite database with timestamps. The persistent database connection handles continuous high-frequency writes reliably.

## Hardware
- Raspberry Pi Pico W (MicroPython)
- Raspberry Pi 5
- DHT11 temperature and humidity sensor
- PIR motion sensor
- IR proximity sensor
- Passive buzzer
- LEDs and push buttons

## Dependencies
### Pico W
- MicroPython standard library
- umqtt.simple

### Pi 5
pip install paho-mqtt

## Configuration
Before running, update the following in pico_controller.py:
pythonSSID = "YOUR_SSID"
PASSWORD = "YOUR_PASSWORD"
MQTT_BROKER = "YOUR_PI_IP_ADDRESS"
