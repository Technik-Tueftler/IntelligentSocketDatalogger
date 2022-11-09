# pylint: skip-file

import time
import urequests
from machine import Pin, ADC

print("Start main programm")

print(time.time())
time.sleep(2)
print(time.time())
time.sleep(2)
print(time.localtime())
import ntptime

ntptime.settime()
now = time.localtime()
print(now)
print(time.mktime(now))

data = 'census,device=server01 power=0.99,device_temperature=9.9'
response = urequests.post("http://192.168.178.39:8086/write?db=test", data=data)
print(response)

led = Pin(22, Pin.IN)
# dis = ADC(Pin(34))
# dis.atten(ADC.ATTN_11DB)

while True:
    print(led.value())
    # print(dis.read())
    time.sleep(0.2)