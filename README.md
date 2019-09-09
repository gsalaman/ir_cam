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

## Display control Messages
I'm going to implement a "query/set" mechanism...that way a client can either set a raw pixel temperature for high 
or low bound, or do an increment/decrement (query, add or subtract, then set)

Proposed messages:  
Subscribed by display:
`ir_cam_display/query/low_temp` will cause `ir_cam_display/value/low_temp` to be published.  
`ir_cam_display/query/high_temp` causes `ir_cam_display/value/high_temp` to be published.  
`ir_cam_display/set/low_temp` will set the low temp.  
`ir_cam_display/set/high_temp` sets the high temp.  

Which means the app needs to subscribe to `ir_cam_display/value/#`
