import time
import paho.mqtt.client as mqtt

###################################
# Graphics imports, constants and structures
###################################
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw

# this is the size of ONE of our matrixes. 
matrix_rows = 64 
matrix_columns = 64 

# how many matrixes stacked horizontally and vertically 
matrix_horizontal = 1 
matrix_vertical = 1

total_rows = matrix_rows * matrix_vertical
total_columns = matrix_columns * matrix_horizontal

options = RGBMatrixOptions()
options.rows = matrix_rows 
options.cols = matrix_columns 
options.chain_length = matrix_horizontal
options.parallel = matrix_vertical 
options.hardware_mapping = 'regular'  
#options.gpio_slowdown = 2

matrix = RGBMatrix(options = options)

# Since we're doing a "preditor" style view, we're going to map our raw pixel
# temperature to a color (from blue to red).
# The low bound will tell which pixel temp maps to blue, and the high bound
# tells what maps to red.
pixel_low_bound = 75 
pixel_high_bound = 130 

##############################
# map_color
#
# This function takes a raw pixel value (temperature) and maps it to a color 
# value
############################## 
def map_color(pixel_val):
  
  global pixel_low_bound  
  global pixel_high_bound 

  # We're going to use HSV for the color...240 is blue, 0 is red.
  # We'll map 240 to our low_bound, 0 to our high_bound, and interpolate 
  # the rest. 
  cool_color = 240
  hot_color = 0

  # start by saturating our pixel_val to be within the allowed bounds
  if pixel_val < pixel_low_bound:
    pixel_val = pixel_low_bound
  if pixel_val > pixel_high_bound:
    pixel_val = pixel_high_bound

  # calulate what % our pixel is (beteeen low and high). 
  # 0% = low, 100% = high
  pixel_range = pixel_high_bound - pixel_low_bound
  pixel_pct = 100 * (pixel_val - pixel_low_bound) / pixel_range

  # take that %, and use it to calculate where we are in color.
  color_range = hot_color - cool_color
  color_delta = color_range * pixel_pct / 100 
  mapped_color = cool_color + color_delta 

  return "hsl({},100%,50%)".format(mapped_color)

#############################
# show_pixels
#
# This function takes a packed pixel payload, unpacks it, and maps those
# pixels displays on our RGB matrix "preditor vision" style, doing
# a bicubic interpolation to increase our 8x8 pixel data to fit a square on 
# the screen.
#############################
def show_pixels(payload):
  global matrix
  global total_rows
  global total_columns

  # Step 1:  read the pixel data out of the message
  pixel_data = []
  for item in payload:
     pixel_data.append(ord(item))

  # now that we've got pixel values, we're going to want an 8x8 image
  # where we map those pixels to color values.  
  image_8x8 = Image.new("RGB", (8,8))
  draw_8x8 = ImageDraw.Draw(image_8x8)
  x = 0
  y = 0
  for pixel in pixel_data:
    color = map_color(pixel)
    draw_8x8.rectangle((x,y,x,y),fill=color)
    x += 1
    if (x >= 8):
      x = 0
      y += 1
  
  # Okay, we've built the 8x8.  Now want to rescale it up to our display size
  # Since we're doing a square, make it the smaller of our width and height.
  if (total_rows < total_columns):
    display_side = total_rows
  else:
    display_side = total_columns

  full_image = image_8x8.resize((display_side,display_side), Image.BICUBIC)
  matrix.SetImage(full_image,0,0)

###################################################
# low_temp_ctl
#
#  This function modifies the low temperature bound based on the
#  received payload.  Specificially:
#    * If it's a "+", we'll increase it
#    * If it's a "-", we'll decrease it
#  All other payloads are ignored.
###################################################
def low_temp_ctl(payload):
  global pixel_low_bound
  
  if payload == "+":
    if pixel_low_bound < 255:
      pixel_low_bound += 1
    print "New low temp: "+str(pixel_low_bound)
      
  elif payload == "-":
    if pixel_low_bound > 0: 
      pixel_low_bound -= 1
    print "New low temp: "+str(pixel_low_bound)
 
  else:
    print "Unknown payload for setting lower temp"
  
###################################################
# high_temp_ctl
#
#  This function modifies the high temperature bound based on the
#  received payload.  Specificially:
#    * If it's a "+", we'll increase it
#    * If it's a "-", we'll decrease it
#  All other payloads are ignored.
###################################################
def high_temp_ctl(payload):
  global pixel_high_bound
  
  if payload == "+":
    if pixel_high_bound < 255:
      pixel_high_bound += 1
    print "New high temp: "+str(pixel_high_bound)
      
  elif payload == "-":
    if pixel_high_bound > 0: 
      pixel_high_bound -= 1
    print "New high temp: "+str(pixel_high_bound)
 
  else:
    print "Unknown payload for setting upper temp"

####################################################
# send_low_temp
#
#  Publishes the low temperature bound
####################################################
def send_low_temp():
  global pixel_low_bound
  global client

  client.publish("ir_cam_display/value/low_temp", str(pixel_low_bound))
  print "Sent low temp: "+str(pixel_low_bound)

####################################################
# send_high_temp
#
#  Publishes the high temperature bound
####################################################
def send_high_temp():
  global pixel_high_bound
  global client

  client.publish("ir_cam_display/value/high_temp", str(pixel_high_bound))
  print "Sent high temp: "+str(pixel_high_bound)

  
##############################
# on_message
#
#  MQTT callback for when we recieve a message.
##############################
def on_message(client, userdata, message):

  if message.topic == "ir_camera_pixels":
    show_pixels(message.payload)
  elif message.topic == "ir_cam_display/set/low_temp":
    low_temp_ctl(message.payload)
  elif message.topic == "ir_cam_display/set/high_temp":
    high_temp_ctl(message.payload)
  elif message.topic == "ir_cam_display/query/low_temp":
    send_low_temp()
  elif message.topic == "ir_cam_display/query/high_temp":
    send_high_temp()
  else:
    print("Unknown topic received:  "+message.topic)

###############################
# And, the main code.
###############################
broker_address = "10.0.0.17"
#broker_address = "makerlabPi1"
client = mqtt.Client("IR_Display")
client.on_message=on_message
try:
  client.connect(broker_address)
except:
  print "Unable to connect to MQTT broker"
  exit(0)

client.loop_start()
client.subscribe("ir_camera_pixels")
client.subscribe("ir_cam_display/set/#")
client.subscribe("ir_cam_display/query/#")

send_high_temp()
send_low_temp()

print "Display running.  Hit ctl-c to exit"
while True:
  time.sleep(1)

