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

# Unofficial ST7789 Display Driver Perf Optimization
The ST7789 library is using the [obsolete `xfer` method to write the display via SPI](https://github.com/pimoroni/st7789-python/blob/v1.0.1/st7789/__init__.py#L184-L187)

Double the framerate with the [more optimized `writedata2` method](https://pypi.org/project/spidev/) and remove the send by chunk logic
