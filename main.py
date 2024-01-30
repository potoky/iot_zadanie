#odznova
from machine import Pin, PWM
from time import sleep
import network
import time
import utime
import json
import machine
from umqtt.simple import MQTTClient
from PICO_CONFIG import *

buzzer = PWM(Pin(14))
ledka=Pin(15,Pin.OUT)
sensor = Pin(16, Pin.IN, Pin.PULL_DOWN)
pico_led = Pin('LED', Pin.OUT)
pico_led.off()

led_state = False
delay = 2
f = 349
g = 392
a = 440

buzzer.freq(g)
buzzer.duty_u16(0)

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
    
    
def do_update():
    try:
        machine.reset()
    except RuntimeError as e:
        print(e)
    
# Connect to MQTT Broker
def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, PORT, MQTT_USERNAME, MQTT_PASSWORD)
    return client

# Send Data to MQTT Broker
def send_mqtt(client, message):
    client.publish(MQTT_TOPIC_SOUND_111201, message)
    print(f'Sent to MQTT Broker: {message}')
    
def measure():
    try:
        sound_value = sensor.value()
        
        rtc_time = rtc.datetime()
        
        datetime_str = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.{:06d}Z".format(
            rtc_time[0], rtc_time[1], rtc_time[2], rtc_time[4], rtc_time[5], rtc_time[6], rtc_time[7]
        )
        
        print(f'Sound is: {sound_value}')
        
        if sound_value == 1:
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
        
        return {
                "dt": datetime_str,
                "name":"MariaDB zvukovy senzor",
                "id": "111201",
                "sound":sound_value
                }
    except OSError as e:
        return 'Failed to read sensor.'
    
    
def subscribe_callback(topic, message):
    global delay
    global led_state
    topic = topic.decode('utf-8')
    message = message.decode('utf-8')
    
    data = json.loads(message)
    if 'delay' in data:
        delay = data['delay']
        
    if 'led1' in data:
        led_state = data['led1']
        pico_led.value(int(led_state))
        
        print(led_state)
        
        sleep(2)
        if led_state == True:
            do_update()
        
#     if 'update' in data:
#         if data['update'] == True:
#             do_update()
    
        
    print(f'Message is: {message}')

do_connect(SSID, PASSWORD)

rtc = machine.RTC()

mqtt_client = connect_mqtt()
mqtt_client.set_callback(subscribe_callback)
mqtt_client.connect()
mqtt_client.subscribe(MQTT_TOPIC_SOUND_111201_SET)
mqtt_client.subscribe(MQTT_TOPIC_LED_111205_SET)

while True:
    mqtt_client.check_msg()
    ledka.value(led_state)
    measures = measure()
    send_mqtt(mqtt_client, json.dumps(measures))
    sleep(delay)
    
