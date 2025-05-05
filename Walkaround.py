#Speaker is configured via /boot/firmware/config
#Camera requires 'sudo apt install -y python3-picamera2' on lite os

from time import sleep
from gpiozero import LED, Button, RGBLED, TonalBuzzer, Buzzer
import rv3028
import datetime
import time
from lsm6ds3 import LSM6DS3
from smbus2 import SMBus
from bme280 import BME280
from picamera2 import Picamera2
from pygame import mixer

mixer.init()

GreenLed = LED(19) #21
#AltGreenLed = LED(25) #Yup, not working
RedLed = LED(24)
YellowLed = LED(5)

BigButton = Button(4)
LittleButton = Button(23)
ColourLed = RGBLED(red = 17, green = 18, blue = 27) #Also not working

buzzer = TonalBuzzer(12) #Works, but need to spend some time finding good tones

#Might only have to run the rtc set-up once per system?
# rtc = rv3028.RV3028()
# rtc.set_battery_switchover('level_switching_mode')
# current_system_time = datetime.datetime.now()
# rtc.set_time_and_date(current_system_time)

lsm = LSM6DS3()
bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

#Camera
cam = Picamera2()
capture_config = cam.create_still_configuration()
cam.configure(capture_config)

testAudio = mixer.Sound("Resources/TestAudio.wav")


def printMsg():
    print("A button was pressed!")

BigButton.when_activated = printMsg
BigButton.when_deactivated = printMsg
LittleButton.when_activated = printMsg
LittleButton.when_activated = printMsg

while True:
    currentTime = time.gmtime()
    print("The time is: {:02d}:{:02d}:{:02d} on :{:02d}/{:02d}/{:02d}".format(currentTime.tm_hour, currentTime.tm_min, currentTime.tm_sec, currentTime.tm_mday, currentTime.tm_mon, currentTime.tm_year))     
    #buzzer.play(60)
    GreenLed.on()
    sleep(2)
    #buzzer.stop()
    GreenLed.off()
    YellowLed.on()
    sleep(2)
    YellowLed.off()
    RedLed.on()
    sleep(2)
    RedLed.off()
    ax, ay, az, gx, gy, gz = lsm.get_readings()
    print("Accelerometer\nX:{}, Y:{}, Z:{}\nGyro\nX:{}, Y:{}, Z{}\n\n ".format(ax, ay, az, gx, gy, gz))
    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    print(f"{temperature:05.2f}°C {pressure:05.2f}hPa {humidity:05.2f}%")
    cam.start()
    cam.capture_file("Walkaround_test.jpg")
    testAudio.play()
    print("----- End of test -----")
