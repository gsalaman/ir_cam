# this is the sending side.  Use I2C to capture the 8x8 IR screen, and send 
# that over to the display side.

import time
import paho.mqtt.client as mqtt
from irCam import IrCam
from broker import read_broker

_shutdown = False

def on_message(client, userdata, message):
  global _shutdown

  if (message.topic == "ir_cam/shutdown"):
    print("Shutdown Received")
    _shutdown = True

sensor = IrCam()

broker_address = read_broker()
client = mqtt.Client("IR_Camera")
client.on_message = on_message
try:
  client.connect(broker_address)
except:
  print("Unable to connect to MQTT broker")
  exit(0)

client.loop_start()
client.subscribe("ir_cam/shutdown")

print("Camera running.  Hit ctl-c to exit")
while (_shutdown == False):
  pixels = sensor.get_pixels()
  
  # x and y are the top right corner of our rectangle
  x = 0
  y = 0
  for pixel in pixels:
    # saturate each pixel to 255 max
    if pixel > 255:
       pixel = 255
    if pixel < 0:
       pixel = 0

  packed_data = bytearray(pixels)
  client.publish("ir_camera_pixels", packed_data)
    
  time.sleep(.1)
