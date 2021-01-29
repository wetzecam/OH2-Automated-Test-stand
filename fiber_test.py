#!/usr/bin/env python

from rw_reg import *
from time import *
import array
import struct
import subprocess

class Colors:
    WHITE   = '\033[97m'
    CYAN    = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE    = '\033[94m'
    YELLOW  = '\033[93m'
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    ENDC    = '\033[0m'


def main():
    heading("Fiber test")

    subprocess.call(["rawi2c", "/dev/i2c-2", "w", "0x54", "127", "1", ">", "/dev/null"])
    subprocess.call(["rawi2c", "/dev/i2c-3", "w", "0x54", "127", "1", ">", "/dev/null"])
    subprocess.call(["rawi2c", "/dev/i2c-4", "w", "0x54", "127", "1", ">", "/dev/null"])

    #subprocess.call(["rawi2c", "/dev/i2c-4", "r", "0x54", "206", "24"])
    p = subprocess.Popen(["rawi2c", "/dev/i2c-4", "r", "0x54", "206", "24"], stdout=subprocess.PIPE)
    out = p.communicate()
    parseRxPower(out[0])

    print "zzzzzzzzzzzzz"
    print readOhRxPower(9)

def parseRxPower(rawi2c_output):
    res = rawi2c_output.split(" ")
    for ch in range(0, 12):
        ch_msb_idx=5+(11-ch)*2
        ch_lsb_idx=6+(11-ch)*2
        ch_msb=str(res[ch_msb_idx])
        ch_lsb=str(res[ch_lsb_idx])
        ch_pwr="0x" + ch_msb + ch_lsb
        print "Ch %02d :  %3d uW" % (ch,int(ch_pwr,0)/10)

# this function reads the RX power of channels corresponding to GBT0, GBT1, GBT2, trig1 and trig2 of the specified OH and returns an array of these values in that order (units are uW)
def readOhRxPower(oh):

    power = [-1, -1, -1, -1, -1]

    #read the GBT power
    cxp = oh / 4
    p = subprocess.Popen(["rawi2c", "/dev/i2c-%d" % (cxp+2), "r", "0x54", "206", "24"], stdout=subprocess.PIPE)
    out = p.communicate()
    res = out[0].split(" ")
    first_ch = oh * 3 - cxp * 12
    for ch in range(first_ch, first_ch + 3):
        ch_msb_idx=5+(11-ch)*2
        ch_lsb_idx=6+(11-ch)*2
        ch_msb=str(res[ch_msb_idx])
        ch_lsb=str(res[ch_lsb_idx])
        ch_pwr="0x" + ch_msb + ch_lsb
        power[ch - first_ch] = int(ch_pwr,0)/10

#	    printf "\n---   MP0   ---\n"
#	    ./parse_i2c_opto_power.py `ssh $CTP7_DUT "rawi2c /dev/i2c-1 r 0x30 64 24"`

#	    printf "\n---   MP1   ---\n"
#	    ./parse_i2c_opto_power.py `ssh $CTP7_DUT "rawi2c /dev/i2c-1 r 0x31 64 24"`

#	    printf "\n---   MP2   ---\n"
#	    ./parse_i2c_opto_power.py `ssh $CTP7_DUT "rawi2c /dev/i2c-1 r 0x32 64 24"`

    mp_ch = 4 + oh * 2
    if oh > 9:
        mp_ch += 8

    return power

def debugCyan(string):
    if DEBUG:
        printCyan('DEBUG: ' + string)

def heading(string):
    print Colors.BLUE
    print '\n>>>>>>> '+str(string).upper()+' <<<<<<<'
    print Colors.ENDC

def subheading(string):
    print Colors.YELLOW
    print '---- '+str(string)+' ----',Colors.ENDC

def printCyan(string):
    print Colors.CYAN
    print string, Colors.ENDC

def printRed(string):
    print Colors.RED
    print string, Colors.ENDC

def hex(number):
    if number is None:
        return 'None'
    else:
        return "{0:#0x}".format(number)

def binary(number, length):
    if number is None:
        return 'None'
    else:
        return "{0:#0{1}b}".format(number, length + 2)

if __name__ == '__main__':
    main()
