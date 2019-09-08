# this is the sending side.  Use I2C to capture the 8x8 IR screen, and send 
# that over to the display side.

import time
import paho.mqtt.client as mqtt
from irCam import IrCam

sensor = IrCam()

broker_address="10.0.0.17"
#broker_address="makerlabpi1"
client = mqtt.Client("IR_Camera")
try:
  client.connect(broker_address)
except:
  print "Unable ot connect to MQTT broker"
  exit(0)

while True:
  pixels = sensor.get_pixels()
  
  # x and y are the top right corner of our rectangle
  x = 0
  y = 0
  for pixel in pixels:
    # saturate each pixel to 255 max
    if pixel > 255:
       pixel = 255

  packed_data = bytearray(pixels)
  client.publish("ir_camera_pixels", packed_data)
  print packed_data
    
  time.sleep(1)
