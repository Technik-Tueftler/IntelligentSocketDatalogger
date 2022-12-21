# pylint: skip-file

import time
import urequests
from machine import Pin, ADC
import _thread
import parameter

URL = f'http://192.168.178.39:8086/write?db={parameter.DB_NAME}'

print("Start main programm")

led = Pin(22, Pin.IN, Pin.PULL_UP)
communication = {"counted_pulses": 0, "toggle_transmitted_flag": False, "running": True}


def write_db(data):
    response = urequests.post(URL, data=data)
    response.close()


def write_log(message):
    with open('logging.txt', 'a') as f:
        log_message = str(time.localtime()) + ": " + str(message) + "\n"
        f.write(log_message)


def count_pulses():
    transmitted_ll = communication["toggle_transmitted_flag"]
    led_value_ll = None
    while communication["running"]:
        if communication["toggle_transmitted_flag"] != transmitted_ll:
            communication["counted_pulses"] = 0
            print("loeschen")
        led_value = led.value()
        if led_value != led_value_ll:
            if not led_value:
                print("Neuer Wert")
                communication["counted_pulses"] += 1


        led_value_ll = led_value
        transmitted_ll = communication["toggle_transmitted_flag"]
        time.sleep(0.001)


_thread.start_new_thread(count_pulses, ())

start_measurement_time = time.time()
latch_energy_wh_after_crash = 0
while communication["running"]:
    try:
        end_measurement_time = time.time()
        while ((end_measurement_time - start_measurement_time) < parameter.UPDATE_TIME):
            end_measurement_time = time.time()
            time.sleep(0.1)
        print("Datenbankeintrag")
        impulses = communication["counted_pulses"]
        energy_wh = impulses / parameter.CONVERSION_FACTOR_METER
        power = (energy_wh * 60 * 60)/60
        print(impulses)
        print(energy_wh)
        if communication["toggle_transmitted_flag"] == True:
            communication["toggle_transmitted_flag"] = False
        else:
            communication["toggle_transmitted_flag"] = True
        data = "census,device=server01 energy_wh=" + str(energy_wh) + ",impulse=" + str(impulses) + ",power=" + str(power)
        start_measurement_time = time.time()
        write_db(data)
    except OSError as err:
        # OSError: [Errno 113] ECONNABORTED
        write_log("OSError " + str(err))
        print(f"Fehler OSError: {err}")
        communication["running"] = False
    except KeyboardInterrupt:
        print("Abbruch über Tastatur")
        write_log("Abbruch über Tastatur")
        communication["running"] = False
    except:
        write_log(err)
        communication["running"] = False

print("Programm Ende")
