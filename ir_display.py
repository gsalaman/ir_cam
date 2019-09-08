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

#options.hardware_mapping = 'adafruit-hat-pwm' 
#options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'
options.hardware_mapping = 'regular'  

options.gpio_slowdown = 2

matrix = RGBMatrix(options = options)

##############################
def map_color(pixel_val):
  
  pixel_low_bound = 75 
  pixel_high_bound = 130 

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

  # for right now, I'm just going to use that number as the hsv value.
  return "hsl({},100%,50%)".format(mapped_color)

#############################
def show_pixels(payload):
  global matrix

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

  # better scaling math goes here...
  display_side = 64

  full_image = image_8x8.resize((display_side,display_side), Image.BICUBIC)
  matrix.SetImage(full_image,0,0)

##############################

def on_message(client, userdata, message):

  print "Callback!"

  if message.topic == "ir_camera_pixels":
    show_pixels(message.payload)
  else:
    print("Unknown topic received:  "+message.topic)

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

while True:
  print "Click!"
  time.sleep(1)

