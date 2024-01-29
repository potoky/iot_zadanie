#ahoj jany
from machine import Pin, PWM
from time import sleep
import network
import time
from umqtt.simple import MQTTClient
from PICO_CONFIG import *
from ota_test import *

buzzer = PWM(Pin(14))
ledka=Pin(15,Pin.OUT)
sensor = Pin(16, Pin.IN, Pin.PULL_DOWN)

f = 349
g = 392
a = 440

buzzer.freq(g)
buzzer.duty_u16(0)

in_f = False

def do_connect(ssid, password):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    
    
# Connect to MQTT Broker
def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    return client

# Send Data to MQTT Broker
def send_mqtt(client, message):
    client.publish(MQTT_TOPIC, message)
    print(f'Sent to MQTT Broker: {message}')
    
def measure():
    try:
        sound = sensor.value()
        
        if sound == 1:
            buzzer.freq(g)
            buzzer.duty_u16(500)
            sleep(1)
            buzzer.freq(a)
            sleep(1)
            buzzer.duty_u16(0)
        else:
            buzzer.freq(g)
            buzzer.duty_u16(500)
            sleep(1)
            buzzer.freq(f)
            sleep(1)
            buzzer.duty_u16(0)
        return f'Sound is: {sound}'
    except OSError as e:
        return 'Failed to read sensor.'
    
    
def subscribe_callback(topic, message):
    global in_f
    
    topic = topic.decode('utf-8')
    message = message.decode('utf-8')
    
    if message == "f":
        in_f = True
    if message == "c":
        in_f = False
        
    print(message)  

# do_connect(SSID, PASSWORD)

mqtt_client = connect_mqtt()
mqtt_client.set_callback(subscribe_callback)
mqtt_client.connect()
mqtt_client.subscribe(MQTT_TOPIC_SOUND_1)

i = 0

while True:
    mqtt_client.check_msg()
    measures = measure()
    send_mqtt(mqtt_client, measures)
    check_ota_updates()
    sleep(10)
    print(f'in_f: {in_f}')
    
    i+=1
    if i == 4:
        break
