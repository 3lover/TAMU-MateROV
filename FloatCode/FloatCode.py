from machine import Pin, UART, I2C, SPI, ADC # This module allows us to set up the Pico W pins to specify I2C, UART, SPI, etc.
import time # We need this in order to keep track of timestamps during the mission
import os # Needed for reading/writing files to sd card
import vfs
import sdcard # Connects SD card to the Pico W using sdcard.py


### Activate Pico W pins ###
def setup_pins():
    uart0 = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1)) # Initialize UART0 pins for Ultrasonic Sensor
    i2c0 = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000) # Initialize I2C pins for Pressure Sensor
    spi0 = SPI(0, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16)) # Initialize SPI pins for SD Card Reader
    cs0 = Pin(17, Pin.OUT, value=1) # Initialize cs pin for SD Card Reader
    adc1 = ADC()

    return uart0, i2c0, spi0, cs0, adc1

def setup_sd_card(spi0, cs0):
    try:
        # 1. Initialize the SD card driver
        sd = sdcard.SDCard(spi0, cs0)
        # 2. Use the vfs module explicitly
        vfs_obj = vfs.VfsFat(sd)
        # 3. Mount it to the Pico's file system
        vfs.mount(vfs_obj, "/sd")
        print("SD Card successfully mounted at /sd")
    except Exception as e:
        print("SD Card Error:", e)

### Code for reading Pressure Sensor data and converting it to depth ###
def read_pressure_sensor(i2c0):
    # MS5837 Sensor Address
    SENSOR_ADDR = 0x76
    # Reset the sensor
    i2c0.writeto(SENSOR_ADDR, bytes([0x1E]))
    time.sleep(0.1)

def calculate_depth(pressure_pa):
    surface_pressure = 101325 # Pascals at sea level
    density = 1000
    gravity = 9.81
    depth = (pressure_pa - surface_pressure) / (density * gravity)
    return max(0, depth) # Return 0 if negative



### Code for reading Ultrasonic Sensor data ###
def read_ultrasonic(uart):
    uart.read()  # flush stale buffer

 

### Code for using the sd card ###



#this is done in the main function
### Note: Use time module to keep track of time and write depth data to sd card every 5 seconds ###

### Code for using depth data to know when to actuate buoyancy engine ###


### Surfacing (end) phase ###
### Code for using Ultrasonic Sensor data to see when it is clear to surface ###
def scan_surface(uart):
    if uart.any():
        return True
    return False

#Just trying to see if it can be written differently
#def scan_surface():
#   data

### Main section ###
def main():
    uart, i2c, spi, cs = setup_pins()
    setup_sd_card(spi, cs)
    
    # Open file for writing once at the start
    with open("/sd/mission_data.txt", "a") as f:
        while True:
            # 1. Get Data
            pressure = read_pressure_sensor(i2c)
            depth = calculate_depth(pressure)
            
            # 2. Write to SD
            f.write(f"Depth: {depth}\n")
            f.flush() # Forces the data onto the card physically
            
            # 3. Decision Logic
            if depth > 10: # Example threshold
                actuate_buoyancy_engine()
            
            time.sleep(5) # Wait 5 seconds


main()