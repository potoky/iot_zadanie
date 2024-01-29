#taky saleny dalsi commit cez ota, lebo ma porazuje
from machine import Pin, PWM
from time import sleep
import network
import time
import utime
import ntptime
from umqtt.simple import MQTTClient
from PICO_CONFIG import *

buzzer = PWM(Pin(14))
ledka=Pin(15,Pin.OUT)
sensor = Pin(16, Pin.IN, Pin.PULL_DOWN)

f = 349
g = 392
a = 440

ledka.value(True)

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

        msg = '{\"sound\":' + str(sound_value) + ',' + '\"date\":\"' + datetime_str +'\"}'
        return msg
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
        
    print(f'Message is: {message}')

do_connect(SSID, PASSWORD)

# ntptime.settime()
rtc = machine.RTC()

mqtt_client = connect_mqtt()
mqtt_client.set_callback(subscribe_callback)
mqtt_client.connect()
mqtt_client.subscribe(MQTT_TOPIC_SOUND_111201_SET)

while True:
    mqtt_client.check_msg()
    measures = measure()
    send_mqtt(mqtt_client, measures)
    sleep(2)
    print(f'in_f: {in_f}')
