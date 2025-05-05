import json
import datetime
import time
import os
from gpiozero import LED, Button, Buzzer
import rv3028 # type: ignore
from lsm6ds3 import LSM6DS3 # type: ignore
from smbus2 import SMBus
from bme280 import BME280 # type: ignore
from picamera2 import Picamera2
from pygame import mixer
import libcamera
from pathlib import Path
from signal import pause
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

#region Setup folders
currentTime = time.gmtime()
homeDir = str(Path.home())
todaysDate = "{:02d}-{:02d}".format(currentTime.tm_mday, currentTime.tm_mon)

try:
    capturesPath = Path(homeDir + '/' + todaysDate)
    capturesPath.mkdir()
except FileExistsError:
    print(f"Directory '{capturesPath}' already exists.")
except PermissionError:
    print(f"Permission denied: Unable to create '{capturesPath}'.")
except Exception as e:
    print(f"An error occurred: {e}")
#endregion

#region Init IO

with open("config/IO.json") as io_data:
    IO: dict = json.load(io_data)

GreenLed: LED = LED(IO["GreenLed"])
YellowLed: LED = LED(IO["YellowLed"])
RedLed: LED = LED(IO["RedLed"])

ActionButton: Button = Button(IO["ActionButton"])
ModeButton: Button = Button(IO["ChangeModeButton"])

BoardBuzzer: Buzzer = Buzzer(IO["Buzzer"])
#endregion

#region Init i2c devices
bus = SMBus(1)

lsm = LSM6DS3()
bme280 = BME280(i2c_dev=bus)

#RTC only has to run once per system
try:
    rtc = rv3028.RV3028()
    rtc.set_battery_switchover('level_switching_mode')
    current_system_time = datetime.datetime.now()
    rtc.set_time_and_date(current_system_time)
except:
    print("No rtc run!")
#endregion

#region Init Camera
pictureMode: bool = True
with open("config/CameraConfig.json") as cam_data:
    camSettings: dict = json.load(cam_data)

cam: Picamera2 = Picamera2()
capture_config: dict = cam.create_still_configuration()
flipHorizontal: bool = bool(camSettings["CamFlipHorizontal"])
flipVertical: bool = bool(camSettings["CamFlipVertical"])

#capture_config["transform"] = libcamera.Transform(hflip=flipHorizontal, vFlip=flipVertical)
cam.configure(capture_config)
#endregion

#region Setup audio
mixer.init()
startUpSound = mixer.Sound("Resources/Startup.mp3")
takeImageSound = mixer.Sound("Resources/CaptureImage.mp3")
#endregion

#region Setup Actions
def Capture():
    if pictureMode:
        RedLed.on()
        currentTime = time.gmtime()
        captureTime: str = "{:02d}:{:02d}:{:02d}".format(currentTime.tm_hour, currentTime.tm_min, currentTime.tm_sec)
        cam.start()
        cam.capture_file(str(capturesPath) + '/' + captureTime + ".jpg")
        takeImageSound.play()
        print("Image captured")
        #Logger.logMessage
        cam.stop()
        RedLed.off()
    else: 
        RedLed.on()
        currentTime = time.gmtime()
        captureTime: str = "{:02d}:{:02d}:{:02d}".format(currentTime.tm_hour, currentTime.tm_min, currentTime.tm_sec)
        encoder = H264Encoder(10000000)
        output = FfmpegOutput(str(capturesPath) + '/' + captureTime  + '.mp4')
        cam.start_recording(encoder, output)
        time.sleep(30)
        cam.stop_recording()
        print("Video recorded")
        RedLed.off()

def SwapMode():
    print("Mode Changed!")
    global pictureMode 
    pictureMode = ~pictureMode
    if pictureMode:
        YellowLed.off()
    else:
        YellowLed.on()



ActionButton.when_activated = Capture
ModeButton.when_held = SwapMode
#endregion

#region Final checks
GreenLed.on()
startUpSound.play()

pause()