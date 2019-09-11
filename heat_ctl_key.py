###############################
#  Imports for reading keyboard
##############################
import sys, os
import termios, fcntl

# used to slow down our main loop
import time

import paho.mqtt.client as mqtt

##################################
# Non-blocking character read function.
#################################
def getch_noblock():
  try:
    return sys.stdin.read()
  except (IOError, TypeError) as e:
    return None

################################
#  Initialize keyboard reading. 
#  Save the old terminal configuration, and
#  tweak the terminal so that it doesn't echo, and doesn't block.
################################
fd = sys.stdin.fileno()
newattr = termios.tcgetattr(fd)

oldterm = termios.tcgetattr(fd)
oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)

newattr[3] = newattr[3] & ~termios.ICANON
newattr[3] = newattr[3] & ~termios.ECHO

fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

termios.tcsetattr(fd, termios.TCSANOW, newattr)


###################
def print_cmds():
  print "Controls:"
  print "d to lower cold bound"
  print "f to raise cold bound"
  print "j to lower hot bound"
  print "k to rarise hot bound"
  print "q to quit"
 
###
# main code here...
###
broker_address = "10.0.0.17"
#broker_address = "makerlabPi1"
client = mqtt.Client("ir_ctl_key")
try:
  client.connect(broker_address)
except:
  print "Unable to connect to MQTT broker"
  exit(0)


print_cmds()

while True:
  key = getch_noblock()

  if key == 'd':
    client.publish("ir_cam_display/set/low_temp", "-")
    print "Lowered cold bound"
  elif key == 'f':
    client.publish("ir_cam_display/set/low_temp", "+")
    print "Raised cold bound"
  elif key == 'j':
    print "Lowered hot bound"
    client.publish("ir_cam_display/set/high_temp", "-")
  elif key == 'k':
    client.publish("ir_cam_display/set/high_temp", "+")
    print "Raised hot bound"
  elif key == 'q':
    break;
  elif key == None:
    continue;
  else:  
    print "unknown key: "+key
    print_cmds()

###################################
# Reset the terminal on exit
###################################
termios.tcsetattr(fd, termios.TCSANOW, oldterm)

fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
