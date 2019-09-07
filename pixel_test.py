import smbus
import time

PI_I2C_CHANNEL = 1

IR_I2C_ADDR = 0x69

PIXEL_START_ADDR = 0x80

bus = smbus.SMBus(PI_I2C_CHANNEL)

while True:
  val = bus.read_word_data(IR_I2C_ADDR,0x80)
  print(val)

  time.sleep(1) 
