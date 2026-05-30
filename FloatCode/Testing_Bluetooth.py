from machine import *
import os as os
import sdcard as sdcard
import time as time
import bluetooth

'''
IMPORTANT INFO:
gatts_write allows to write data but not send it immediately
gatts_notify allows for immediate data send
'''

### BLUETOOTH MODULE ###
ble = bluetooth.BLE() # create ble variable
ble.active(True) # active bluetooth

SERVICE_UUID = bluetooth.UUID("ABCDABCD-1234-ABCD-BBBB-123412341234") #defines category
CHAR_UUID    = bluetooth.UUID("ABCDABCD-1234-ABDD-CCCC-123412341235") #defines data

FLAG_NOTIFY = const(0x0010)
FLAG_READ   = const(0x0002)

#Characteristics
((char_handle,),) = ble.gatts_register_services((
    (SERVICE_UUID, ((CHAR_UUID, FLAG_READ | FLAG_NOTIFY),)),
))


ble.config(gap_name="TeamOceanus") # sets name to TeamOceanus
ble.gap_advertise(100000) # advertises every 0.1 second


conn_handle = None

def irq(event, data):
    global conn_handle

    if event == 1:   # central connected
        conn_handle = data[0]
        print("Laptop connected!")

    elif event == 2:  # central disconnected
        conn_handle = None
        print("Laptop disconnected")
        ble.gap_advertise(100000)  # re-advertise after disconnect

ble.irq(irq)
