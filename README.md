# ir_cam
Adafruit libraries use circuitPython...loads of install overhead.  Since I'm not scared of I2C, I'm going to 
grab the registers myself.

Default I2C address = 0x69
Pixel data lives as words from 0x80 to 0xFF

Cam doesn't appear to support a "block read" functionality, so I'm gonna write one.  :)

## Docs
I2C description: https://www.digikey.com/eewiki/display/Motley/Panasonic+Grid+Eye+Memory+Registers  
Enabling I2C on your pi:  https://github.com/gsalaman/pi_i2c_touch/README.md

# MQTT based transaction thoughts
## camera side
ir_camera.py will be the camera side.  It'll send 64 pixels of RAW data over to the display side as bytes...looks like the pixel data never (rarely?) saturates.

topic = ir_camera_pixels, message is a stream of 64 bytes.
## display side
ir_display.py will be the display side.  We'll subscribe to the 64 pixels, and use that to make an 8x8 color image.  Then, using PIL, we'll upscale that image to our display size (keeping it a square).

### a word on color
The display side picks what color to use for a given pixel based on the low and high temperature bounds; specifically:
* Pixels at or below the cold bound are mapped to blue
* Pixels at or above the hot bound are mapped to red
* Anything in between is interpolated, going through the yellow/green scale (rather than purple)

The display has picked some default values, but here are some notes on adjusting the cold and hot bounds.
* Raising the cold bound raises the temperature at which pixels are considered to be blue.  Think of this as making your background "more blue"
* Lowering the cold bound lowers the temperature at which pixels are considered to be blue.  Think of this as making your background "more green"
* Raising the high bound raises the temperature at which pixels are considered red.  Think of this as making your subject "more green"
* Lowering the high bound lowers the temperature at which pixels are considered red.  Think of this as making your subject "more red"
* Your color "dynamic range" is the space between the cold bound and the hot bound.  A bigger space here shows more pixel variation, while a smaller space shows less.

# Public API
| Message Topic | Payload | Description |
|---|---|---|
| ir_cam_display/set/low_temp | "+" or "-" | Either increments or decrements the low temperature display bound |
| ir_cam_display/set/high_temp | "+" or "-" | Either increments or decrements the high temperature display bound |
| ir_cam_display/query/low_temp | None | Causes the display to publish the low temp bound via an ir_cam_display/value/low_temp message |
| ir_cam_display/query/high_temp | None | Causes the display to publish the high temp bound via an ir_cam_display/value/high_temp message |
| ir_cam_display/value/low_temp | Low Temp bound | Payload contains the display's current low temperature bound. |
| ir_cam_display/value/high_temp | High Temp bound | Payload contains the display's current high temperature bound. |

## Application notes
In order to just set the low and high bounds, an app simply needs to send the ir_cam_display/set/# commands.

If you want to see what the current bounds are, you need to subscribe to ir_cam_display/value/#.  You can query the current value at any time via ir_cam_display/query/...; thus a common flow is to set, then query.

Note that the display will autonomously send both values on startup in order to prevent "out of sync" conditions.  Any app should also query the values on startup for the same reason.
