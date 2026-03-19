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
    adc1 = ADC(27)

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
        if "/sd" not in os.listdir("/"):
            print("SD mount failed")
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


# Ultra sonic sensor
def read_ultrasonic(uart):
    uart.read()  # flush stale buffer

    # Wait up to 500ms for 4 bytes
    t_start = time.ticks_ms()
    while uart.any() < 4:
        if time.ticks_diff(time.ticks_ms(), t_start) > 500:
            return None  # timeout - nothing detected

    # Sync to header byte
    byte = uart.read(1)
    if byte is None or byte[0] != 0xFF:
        return None

    # Read remaining 3 bytes
    rest = uart.read(3)
    if rest is None or len(rest) < 3:
        return None

    high, low, checksum = rest[0], rest[1], rest[2]

    # Validate checksum
    if (0xFF + high + low) & 0xFF != checksum:
        print("Ultrasonic: checksum error")
        return None

    distance_cm = ((high << 8) | low) / 10.0

    # Sensor valid range: 5–600cm
    if not (50.0 <= distance_cm <= 600.0):  ###Modify when testing with real sensor###
        return None
    return distance_cm  # obstacle detected
 

### Code for using the sd card ###



#this is done in the main function
### Note: Use time module to keep track of time and write depth data to sd card every 5 seconds ###

### Code for using depth data to know when to actuate buoyancy engine ###


### Surfacing (end) phase ###
### Code for using Ultrasonic Sensor data to see when it is clear to surface ###

### Need to edit this function it isn't done yet
def buoyancy_down_on_ice(uart, ice_threshold_cm=30):
    """
    Detects ice above using the ultrasonic sensor and moves buoyancy engine down.
    """
    distance = read_ultrasonic(uart)
    if distance is not None and distance <= ice_threshold_cm:
        actuate_buoyancy_engine("down")
        return True
    return False
### Need to edit this function it isn't done yet
def determine_buoyancy_direction(depth, ice_detected, max_depth=10):
    """
    Decides whether the buoyancy engine should go up, down, or hold.
    """
    if ice_detected:
        return "down"
    elif depth >= max_depth:
        return "up"
    else:
        return None
    
def scan_surface(uart):
    return 0


"""
def scan_surface(uart, ice_threshold_cm=30):
    for i in range(5):
        raw = read_ultrasonic(uart)
        if raw:
            try:
                distance_cm = int(raw.decode().strip()[1:]) / 10.0
                return distance_cm <= ice_threshold_cm
            except:
                pass
    return True  # Fail-safe: assume ice
"""
def actuate_buoyancy_engine():
    print("Buoyancy engine activated")
### Main section ###
def main():
    uart, i2c, spi, cs, adc = setup_pins()
    setup_sd_card(spi, cs)
    
    # Open file for writing once at the start
    with open("/sd/mission_data.txt", "a") as f:
        while True:
            # 1. Get Data
            pressure = read_pressure_sensor(i2c)
            depth = calculate_depth(pressure)
            temp_raw = adc.read_u16()
            print("ADC:", temp_raw)
            
            # 2. Write to SD
            timestamp = time.time()
            f.write(f"{timestamp}, Depth: {depth}\n")
            f.flush() # Forces the data onto the card physically
            
            # 3. Decision Logic
            if depth > 10: # Example threshold
                actuate_buoyancy_engine()
            
            time.sleep(5) # Wait 5 seconds


main()
