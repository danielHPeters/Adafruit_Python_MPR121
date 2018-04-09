# Adafruit Raspberry Pi MPR121 Keyboard Example
# Author: Tony DiCola
#
# Allows you to turn touches detected by the MPR121 into key presses on a
# Raspberry Pi.
#
# NOTE: This only works with a Raspberry Pi right now because it depends on some
# specific event detection logic in the RPi.GPIO library.
#
# Dependencies
# ============
#
# Make sure you have the required dependencies by executing the following commands:
#   sudo apt-get update
#   sudo apt-get install build-essential python-dev python-pip libudev-dev
#   sudo pip install python-uinput
#
# Also make sure you have installed the Adafruit Python MPR121 library by running
# its setup.py (in the parent directory):
#   sudo python setup.py install
#
# Usage
# =====
#
# To use this program you first need to connect the MPR121 board to the Raspberry
# Pi (either connect the HAT directly to the Pi, or wire the I2C pins SCL, SDA to
# the Pi SCL, SDA, VIN to Pi 3.3V, GND to Pi GND).  If you aren't using the HAT
# version of the board you must connect the IRQ pin to a free digital input on the
# Pi (the default is 26).
#
# Next define the mapping of capacitive touch input presses to keyboard
# button presses.  Scroll down to the KEY_MAPPING dictionary definition below
# and adjust the configuration as described in its comments.
#
# If you're using a differnet pin for the IRQ line change the IRQ_PIN variable
# below to the pin number you're using.  Don't change this if you're using the
# HAT version of the board as it's built to use pin 26 as the IRQ input.
#
# Finally run the script as root:
#   sudo python keyboard.py
#
# Try pressing buttons and you should see key presses made on the Pi!
#
# Press Ctrl-C to quit at any time.
#
# Copyright (c) 2014 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import atexit
import logging
import subprocess
import sys
import time

import Adafruit_MPR121.MPR121 as MPR121
import RPi.GPIO as GPIO
import uinput
import pyautogui


# Define mapping of capacitive touch pin presses to keyboard button presses.
#KEY_MAPPING = {
 #               0: uinput.KEY_A,    # Each line here should define a dict entry
  #              1: uinput.KEY_S,     # that maps the capacitive touch input number
   #             2: uinput.KEY_D,     # to an appropriate key press.
    #            3: uinput.KEY_F,     #
    #           4: uinput.KEY_G,     # For reference the list of possible uinput.KEY_*
    #            5: uinput.KEY_H,     # values you can specify is defined in linux/input.h:
 #               6: uinput.KEY_J,     # http://www.cs.fsu.edu/~baker/devices/lxr/http/source/linux/include/linux/input.h?v=2.6.11.8
 #               7: uinput.KEY_K,
  #              8: uinput.KEY_Q,
   #             9: uinput.KEY_W
    #          }                      # Make sure a cap touch input is defined only
                                     # once or else the program will fail to run!

KEY_MAPPING = {
    0: 'a',
    1: 's',
    2: 'd',
    3: 'f',
    4: 'g',
    5: 'h',
    6: 'j',
    7: 'k',
    8: 'q',
    9: 'w'
}

# Input pin connected to the capacitive touch sensor's IRQ output.
# For the capacitive touch HAT this should be pin 26!
IRQ_PIN = 26

# Don't change the below values unless you know what you're doing.  These help
# adjust the load on the CPU vs. responsiveness of the key detection.
MAX_EVENT_WAIT_SECONDS = 0.5
EVENT_WAIT_SLEEP_SECONDS = 0.1


# Uncomment to enable debug message logging (might slow down key detection).
# logging.basicConfig(level=logging.DEBUG)

# Make sure uinput kernel module is loaded.
subprocess.check_call(['modprobe', 'uinput'])

# Configure virtual keyboard.
# device = uinput.Device(KEY_MAPPING.values())

# Setup the MPR121 device.
cap = MPR121.MPR121()
# if not cap.begin():
#    print('Failed to initialize MPR121, check your wiring!')
#    sys.exit(1)
cap.begin(address=0x5C)
# Configure GPIO library to listen on IRQ pin for changes.
# Be sure to configure pin with a pull-up because it is open collector when not
# enabled.
GPIO.setmode(GPIO.BCM)
GPIO.setup(IRQ_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(IRQ_PIN, GPIO.FALLING)
atexit.register(GPIO.cleanup)

# Clear any pending interrupts by reading touch state.
cap.touched()
pressed = dict()
for pin, key in KEY_MAPPING.iteritems():
    dict[key] = False

# Event loop to wait for IRQ pin changes and respond to them.
print('Press Ctrl-C to quit.')
while True:
    # Wait for the IRQ pin to drop or too much time elapses (to help prevent
    # missing an IRQ event and waiting forever).
    start = time.time()
    while (time.time() - start) < MAX_EVENT_WAIT_SECONDS and not GPIO.event_detected(IRQ_PIN):
        time.sleep(EVENT_WAIT_SLEEP_SECONDS)
    # Read touch state.
    touched = cap.touched()
    # Emit key presses for any touched keys.
    for pin, key in KEY_MAPPING.iteritems():
        # Check if pin is touched.
        pin_bit = 1 << pin
        if touched & pin_bit:
            # Emit key event when touched.
            logging.debug('Input {0} touched.'.format(pin))
            if pressed.get(key) is False:
                pressed[key] = True
            # device.emit_click(key)
                pyautogui.keyDown(key)
        else:
            pyautogui.keyUp(key)
            pressed[key] = False
