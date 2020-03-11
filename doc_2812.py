#!/usr/bin/python
NumpyImported=False
try:
    import numpy
    from numpy import sin, cos, pi
    NumpyImported=True
    print("NumpyImported")
except ImportError:
    #print("Warning: no numpy found, routines will be slow")
    pass
"""
T0H: 0.35   -> 2p=0.31  3p=0.47
T0L: 0.80   -> 6p=0.94  5p=0.78
T1H: 0.70   -> 4p=0.625 5p=0.78
T1L: 0.60   -> 4p=0.625 3p=0.47
"""

def write2812_numpy8(spi,data):
    d=numpy.array(data).ravel()
    tx=numpy.zeros(len(d)*8, dtype=numpy.uint8)
    for ibit in range(8):
        #print ibit
        #print ((d>>ibit)&1)
        #tx[7-ibit::8]=((d>>ibit)&1)*0x18 + 0xE0   #0->3/5, 1-> 5/3 
        #tx[7-ibit::8]=((d>>ibit)&1)*0x38 + 0xC0   #0->2/6, 1-> 5/3
        tx[7-ibit::8]=((d>>ibit)&1)*0x78 + 0x80    #0->1/7, 1-> 5/3
        #print [hex(v) for v in tx]
    #print [hex(v) for v in tx]
    spi.xfer(tx.tolist(), int(8/1.25e-6))
    #spi.xfer(tx.tolist(), int(8e6))
    
def write2812_numpy4(spi,data):
    #print("here")
    #print spi
    d=numpy.array(data).ravel()
    tx=numpy.zeros(len(d)*4, dtype=numpy.uint8)
    for ibit in range(4):
        #print ibit
        #print ((d>>(2*ibit))&1), ((d>>(2*ibit+1))&1)
        tx[3-ibit::4]=((d>>(2*ibit+1))&1)*0x60 + ((d>>(2*ibit+0))&1)*0x06 +  0x88
        #print [hex(v) for v in tx]
    #print [hex(v) for v in tx]
    spi.xfer(tx.tolist(), int(4/1.25e-6)) #works, on Zero (initially didn't?)
    #spi.xfer(tx.tolist(), int(4/1.20e-6))  #works, no flashes on Zero, Works on Raspberry 3
    #spi.xfer(tx.tolist(), int(4/1.15e-6))  #works, no flashes on Zero
    #spi.xfer(tx.tolist(), int(4/1.05e-6))  #works, no flashes on Zero
    #spi.xfer(tx.tolist(), int(4/.95e-6))  #works, no flashes on Zero
    #spi.xfer(tx.tolist(), int(4/.90e-6))  #works, no flashes on Zero
    #spi.xfer(tx.tolist(), int(4/.85e-6))  #doesn't work (first 4 LEDS work, others have flashing colors)
    #spi.xfer(tx.tolist(), int(4/.65e-6))  #doesn't work on Zero; Works on Raspberry 3
    #spi.xfer(tx.tolist(), int(4/.55e-6))  #doesn't work on Zero; Works on Raspberry 3
    #spi.xfer(tx.tolist(), int(4/.50e-6))  #doesn't work on Zero; Doesn't work on Raspberry 3 (bright colors)
    #spi.xfer(tx.tolist(), int(4/.45e-6))  #doesn't work on Zero; Doesn't work on Raspberry 3
    #spi.xfer(tx.tolist(), int(8e6))

def write2812_pylist8(spi, data):
    tx=[]
    for rgb in data:
        for byte in rgb: 
            for ibit in range(7,-1,-1):
                tx.append(((byte>>ibit)&1)*0x78 + 0x80)
    spi.xfer(tx, int(8/1.25e-6))

def write2812_pylist4(spi, data):
    tx=[0x00]
    for rgb in data:
        for byte in rgb: 
            for ibit in range(3,-1,-1):
                #print ibit, byte, ((byte>>(2*ibit+1))&1), ((byte>>(2*ibit+0))&1), [hex(v) for v in tx]
                tx.append(((byte>>(2*ibit+1))&1)*0x60 +
                          ((byte>>(2*ibit+0))&1)*0x06 +
                          0x88)
    #print [hex(v) for v in tx]
    spi.xfer(tx, int(4/1.05e-6))


if NumpyImported:
    write2812=write2812_numpy4
else:
    write2812=write2812_pylist4    
#write2812=write2812_pylist4

if __name__=="__main__":
    import spidev
    import time
    import getopt
    import sys
    
    LEDs = 32
    matrix = [[0,0,1]]*LEDs
    delay = 0.2
	
    def test_fixed(spi):
        #write fixed pattern for 8 LEDs
        #This will send the following colors:
        #   Red, Green, Blue,
        #   Purple, Cyan, Yellow,
        #   Black(off), White 
        write2812(spi, [[10,0,0], [0,10,0], [0,0,10],
                        [0,10,10], [10,0,10], [10,10,0],
                        [0,0,0], [10,10,10]])
    def test_off(spi, nLED=LEDs):
        #switch all nLED chips OFF.
        write2812(spi, [[0,0,0]]*nLED)
    
    def test1(nLED=LEDs):
        for i in range(0, 254):
            write2812(spi, [[0,0,i]]*nLED)
            time.sleep(0.003)
        time.sleep(1)
        for i in range(254, 0, -1):
            write2812(spi, [[0,0,i]]*nLED)
            time.sleep(0.003)

    def left_to_right():
        for i in range(0, LEDs/2):
            matrix[i]=[0,0,254]
            write2812(spi, matrix)
            time.sleep(delay)
        time.sleep(1)
        for i in range(LEDs/2+1, LEDs):
            matrix[i]=[0,0,254]
            matrix[i-LEDs/2]=[0,0,0]
            write2812(spi, matrix)
            time.sleep(delay)

    def breath():
        min_intensity = 100
        max_intensity = 180
        delay_s = (5.0 / (max_intensity-min_intensity)) 
        for i in range(min_intensity, max_intensity):
            write2812(spi, [[i,i,i]]*nLED)
            time.sleep(delay_s)
        time.sleep(1)
        for i in range(max_intensity, min_intensity,-1):
            write2812(spi, [[i,i,i]]*nLED)
            time.sleep(delay_s)
        time.sleep(1)

    def breath_night():
        min_intensity = 0
        max_intensity = 30
        delay_s = (5.0 / nLED) 
        for i in range(0, nLED-1):
            matrix[i]=[max_intensity,max_intensity,max_intensity]
            write2812(spi, matrix)
            time.sleep(delay_s)
        time.sleep(1)
        for i in range(0, nLED-1):
            matrix[i]=[min_intensity,min_intensity,min_intensity]
            write2812(spi, matrix)
            time.sleep(delay_s)
        time.sleep(1)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn:c:t", ["help", "color=", "test"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    color=None
    nLED=32

    spi = spidev.SpiDev()
    spi.open(1,0)

    print ("Press CTRL+C to exit")
    try:
        while True:
            breath_night()
            # breath()
            # left_to_right()
            # test1()

    # breath()
    # breath()

    except KeyboardInterrupt:
        print ("Goodbye.")

    #test_off(spi,32)
    #time.sleep(1)

	
    #test2()
    #time.sleep(2)
    #test_fixed(spi)
    #test_off(spi)
	
    #write2812(spi, eval(color)*nLED)
    #else:
    #    usage()


