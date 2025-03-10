# PiZeroAiCam
A simple demo of using Coral TPU and Pimoroni Display HAT mini to create an object detection camera

# Instructions
[Link to Instructables](https://www.instructables.com/RPi-Compact-AI-Camera-Feat-Coral-USB-Accelerator/)

# Install
```
git clone https://github.com/Alitzlan/PiZeroAiCam.git
cd PiZeroAiCam
bash install.sh
```
Then reboot the device

# Optimization
With the following optimization, the framerate can hit 20 FPS

## Unofficial ST7789 Display Driver Perf Optimization
The ST7789 library is using the [obsolete `xfer` method to write the display via SPI](https://github.com/pimoroni/st7789-python/blob/v1.0.1/st7789/__init__.py#L184-L187)

Double the framerate with the [more optimized `writebytes2` method](https://pypi.org/project/spidev/) and remove the send by chunk logic

## Unofficial Display HAT Mini Perf Optimization
The Display HAT Mini library [sets a 180-degree rotation](https://github.com/pimoroni/displayhatmini-python/blob/main/library/displayhatmini/__init__.py#L72) and then in this project [a transpose is applied](https://github.com/Alitzlan/PiZeroAiCam/blob/main/src/aicam.py#L119). However, this buffer copy can be removed by setting the rotation directly at the Display HAT Mini (by setting it to rotation=0)

Moreover, [the `spi_speed_hz` parameter can be adjusted to a higher value](https://github.com/pimoroni/displayhatmini-python/blob/main/library/displayhatmini/__init__.py#L73). Based on my experiments, setting it to 90 MHz brings framerate boost without image distortion
