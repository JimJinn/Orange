#!/usr/bin/env python
"""Read pir.

Make gpio input and enable pull-up resistor.
"""

import os
import sys

if not os.getegid() == 0:
    sys.exit('Script must be run as root')

from pyA20.gpio import gpio
from pyA20.gpio import connector
from pyA20.gpio import port

pir = port.PA10

"""Init gpio module"""
gpio.init()

"""Set directions"""
gpio.setcfg(led, gpio.OUTPUT)
gpio.setcfg(pir, gpio.INPUT)

"""Enable pullup resistor"""
gpio.pullup(pir, gpio.PULLUP)
#gpio.pullup(pir, gpio.PULLDOWN)     # Optionally you can use pull-down resistor

try:
    print ("Press CTRL+C to exit")
    old = 0
    while True:
        state = gpio.input(pir)      # Read pir state
        if (old != state):
            print(state)
            old = state

        """Since we use pull-up the logic will be inverted"""
        #gpio.output(led, not state)

except KeyboardInterrupt:
    print ("Goodbye.")
