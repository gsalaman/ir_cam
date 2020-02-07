import smbus

#########################################################
#  IrCam Class
#########################################################
class IrCam():

  ###############################
  # Init method
  ###############################
  def __init__(self):
    self.I2C_CHANNEL = 1
    self.I2C_ADDR = 0x69
    self.I2C_PIXEL_BASE_ADDR = 0x80
    self.num_pixels = 64

    self.bus = smbus.SMBus(self.I2C_CHANNEL)

  ###############################
  # Read Pixel method
  #
  #    Pass in an index (0 through 63), and this function will return the 
  #    sensor value of that pixel. 
  ###############################
  def read_pixel(self, index):

    # check input parameters
    if (index < 0) or (index >= self.num_pixels):
      print("Pixel index out of range: "+str(index))
      exit(1) 
    
    address = self.I2C_PIXEL_BASE_ADDR + (index * 2) 
    return self.bus.read_word_data(self.I2C_ADDR, address)


  ###############################
  # get pixels method
  # 
  #    This method returns all 64 pixels of data in a list.
  ###############################
  def get_pixels(self):
  
    pixel_data = []

    for pixel in range (0,self.num_pixels):
      pixel_data.append(self.read_pixel(pixel))
     
    return pixel_data
