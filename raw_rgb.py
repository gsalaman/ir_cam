import time
from irCam import IrCam
from rgb_matrix import Screen

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



##############################
sensor = IrCam()

matrix_rows = 64
matrix_columns = 64
num_hor = 1
num_vert = 1
 
# we've got a 64x64 matrix, but we only have 8x8 data.  This means every
# block is 8 pixels to a side
pixel_size = 8

display = Screen(matrix_rows, matrix_columns, num_hor, num_vert)

while True:
  pixels = sensor.get_pixels()
  
  # x and y are the top right corner of our rectangle
  x = 0
  y = 0
  for pixel in pixels:
    color = map_color(pixel)
    display.draw.rectangle((x,y,x+pixel_size-1,y+pixel_size-1),fill=color)
    x +=pixel_size
    if (x >= 63):
      x = 0
      y += pixel_size 
  
  display.show()

  time.sleep(.1)
