#!/usr/bin/env python

# This program is to demonstrate string replacement on terminal

import sys
import time
import os

# Define sleep
def sleep():
    time.sleep(.8)
    
thought = 'the discomfort you feel is a sure sign that you are growing as a person... :)'
for word in thought.split():
    word = word + ' ' * 11
    sys.stdout.write('\r' + word)
    sys.stdout.flush()
    sleep()   
print('\n')
