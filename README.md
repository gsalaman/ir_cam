# ir_cam
Adafruit libraries use circuitPython...loads of install overhead.  Since I'm not scared of I2C, I'm going to 
grab the registers myself.

Default I2C address = 0x69
Pixel data lives as words from 0x80 to 0xFF

Cam doesn't appear to support a "block read" functionality, so I'm gonna write one.  :)

## Docs
I2C description: https://www.digikey.com/eewiki/display/Motley/Panasonic+Grid+Eye+Memory+Registers
