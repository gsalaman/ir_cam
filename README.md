# ir_cam
Adafruit libraries use circuitPython...loads of install overhead.  Since I'm not scared of I2C, I'm going to 
grab the registers myself.

Default I2C address = 0x69
Pixel data lives as words from 0x80 to 0xFF

Cam doesn't appear to support a "block read" functionality, so I'm gonna write one.  :)

## Docs
I2C description: https://www.digikey.com/eewiki/display/Motley/Panasonic+Grid+Eye+Memory+Registers

# MQTT based transaction thoughts
## camera side
ir_camera.py will be the camera side.  It'll send 64 pixels of RAW data over to the display side as bytes...looks like the pixel data never (rarely?) saturates.

topic = ir_camera_pixels, message is a stream of 64 bytes.
## display side
ir_display.py will be the display side.  We'll subscribe to the 64 pixels, and use that to make an 8x8 color image.  Then, using PIL, we'll upscale that image to our display size (keeping it a square).

## future messages
Setting low and high pixel bound for color


