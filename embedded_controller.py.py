#main
import leds                         #module
from buttons import Button          #module
from machine import Pin             #library
import dht                          #library
import time                         #library
from ir import IRSensor             #module
from motion_sensing_alarm_system import PIRAlarm #module
import json

#LED Definitions
#############################################
room1 = Pin(16, Pin.OUT)        #Blue       #
room2 = Pin(17, Pin.OUT)        #Green   home_system   #
living_room = Pin(13, Pin.OUT)  #White      #
garage = Pin(22, Pin.OUT)       #Red        #
#############################################

#Buzzer Definition
buzzer = Pin(20, Pin.OUT)       #Passive Buzzer

#PIR Motion Sensor
pir_sensor = Pin(18, Pin.IN)

#DHT11 Temperature and Humidity Sensor Definition
dht11_sensor = dht.DHT11(Pin(15, Pin.IN, Pin.PULL_UP))

#MQTT logging

import network
import time
from simple import MQTTClient

# WiFi & MQTT Config
SSID = "YOUR_SSID"                #Replace with the Access Point's SSID
PASSWORD = "YOUR_PASSWORD"              #Replace with the Access Point's Password
MQTT_BROKER = "10.42.0.1"             #Replace with Pi's IP Address
CLIENT_ID = "PicoW"                   #Name of Device
TOPIC = b"home/sensors"          #The topic of the conversation
CONTROL = b"home/control"       #Control topic

DEVICES = {
    "room1":room1,
    "room2":room2,
    "alarm":garage,
    "livingroom":living_room
    }

# Callback: This function runs when the Pi sends a message
def sub_cb(topic, msg):
    print("Received: ", msg.decode())

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print("Connecting to WiFi...")
    time.sleep(1)

print("Successful Connection to IP:", MQTT_BROKER)

# Connect to MQTT
try:
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.set_callback(sub_cb)              #Set the function to handle incoming messages
    client.connect()
    client.subscribe(CONTROL)                  #Subscribe to the topic to listen for Pi
    print("Connected Successfully to MQTT Broker")
    
    print("Waiting for messages from Pi...")
    
#     while True:
#         client.check_msg()                   #Check for incoming messages from mosquitto_pub
#         time.sleep(0.1)                      #every 0.1s

# --- Helper Functions for Logging ---
except Exception as e:
    print("Error:", e)

def get_temp_data():
    #Read temperature and handles sensor errors.
    try:
        dht11_sensor.measure()
        return dht11_sensor.temperature()
    except OSError:
        return "ERR"

def log_state(t, node, obj, status):
    #Print log in required format: {Time, node_id, object, status}
    
    state = {
        "t": t,
        "node": node,
        "obj": obj,
        "status": status
        }
    
    print(f"{{{t}, {node}, {obj}, {status}}}")
    
    client.publish(TOPIC, json.dumps(state).encode())

def run_system_logs(time_counter):
    #Gather all sensor data and print the logs for this cycle.
    temp = get_temp_data()
    
    # Subsystem status checks
    r1_status = "on" if room1.value() else "off"
    r2_status = "on" if room2.value() else "off"
    lr_status = "on" if living_room.value() else "off"
    alarm_status = "on" if pir_system.alarm_active else "off"

    # Print logs
    log_state(time_counter, "room1", "lights", r1_status)
    log_state(time_counter, "room2", "lights", r2_status)
    log_state(time_counter, "living_room", "lights", lr_status)
    log_state(time_counter, "thermostat", "temperature", temp)
    log_state(time_counter, "garage", "alarm", alarm_status)
    
    print(f"t({time_counter}) messages plublished")

# --- Event Handlers ---

#IR sensor
ir_sensor_pin = Pin(14, Pin.IN)
ir_system = IRSensor(pin_num = ir_sensor_pin, led_pin = living_room)

#PIR Motion Sensor Alarm
pir_system = PIRAlarm(pir_pin = pir_sensor, led_pin = garage, buzzer_pin = buzzer)

#Push-Button selector
def on_button_pressed(button_name):
    if button_name == 1:
        leds.toggle_led(room1)
    elif button_name == 2:
        leds.toggle_led(room2)
    elif button_name == 3:
        # If silence() returns true, it means it just stopped an alarm.
        # If it returns false, we proceed to regular toggle behavior.
        if not pir_system.silence():
            garage.value(0)
            leds.led_off(garage)
    
#Push-Button Definitions
############################################################################################
button1 = Button(pin_num = 28, callback=on_button_pressed, name = 1)     #room1            #
button2 = Button(pin_num = 27, callback=on_button_pressed, name = 2)     #room2            #
button3 = Button(pin_num = 26, callback=on_button_pressed, name = 3)     #garage/alarm     #
############################################################################################

def system_control(topic,msg):
    
    msg = msg.decode()
    
    if msg == "room1:on":
        print("command received")
        leds.led_on(room1)
    elif msg == "room1:off":
        leds.led_off(room1)
    
    if msg == "room2:on":
        leds.led_on(room2)
    elif msg == "room2:off":
        leds.led_off(room2)
        
    if msg == "alarm:on":
        pir_system.trigger_alarm()
    elif msg == "alarm:off":
        pir_system.silence()
    
    if msg == "livingroom:on":
        leds.led_on(living_room)
    elif msg == "livingroom:off":
        leds.led_off(living_room)
    
        
    
def main():
    print("START SYSTEM\n")
    time_counter = 0
    
    client.set_callback(system_control)
    client.subscribe(CONTROL)
    
    while True:
        # Executes all data logging requirements
        for _ in range(10):      
            client.check_msg()                   #Check for incoming messages from mosquitto_pub
            time.sleep(0.1)                      #every 0.1s
        
        run_system_logs(time_counter)
        
        time_counter += 1
#         time.sleep(1) # Frequency of logging: 1 second
        
        
    
if __name__ == "__main__":
    main()
    
    

