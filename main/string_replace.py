#!/usr/bin/env python

# This program is to demonstrate string replacement on terminal

import sys
import time
import os

# Define sleep
def sleep():
    time.sleep(.4)
    
# Infinite Loop
try:
  while True:
    sys.stdout.write('\r'+ 'yogesh')
    sleep()
    sys.stdout.flush()
    sys.stdout.write('\r'+ 'jadhav')
    sleep()
    sys.stdout.flush()
except KeyboardInterrupt: # To exit on keyboard interrupt
  print('\n Exiting...')
