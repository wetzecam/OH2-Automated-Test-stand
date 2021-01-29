#!/usr/bin/env python

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
    toleranceCheck(0.99, 1.0, 0.05)
    toleranceCheck(0.75, 1.0, 0.05)
    print(convertVoltage(249))
    print(convertCurrent(70))
    print("TEMPERATURES")
    print(convertTemp(96.1))
    print(convertTemp(105.8))
    print(convertTemp(121.3))
    print(convertTemp(134.7))
    print(convertTemp(144.2))

#   Accounts for 1/4 resistor divider (SCA CH 0-5)
#   Input  : mV
#   Output : mV
def convertVoltage(val):
    return val*4.0

#   Preforms conversion accounting for:
#       - 20 V/V voltage Amplifier
#       - 10 mOhm current sense resistor
#       - 1/4 ADC input voltage divider
#   Input  : mV
#   Output : Amps
def convertCurrent(val):
    return ((val * 4.0) / 10.0) / 20.0

#   Converts Temp dependent resistor calculation
#       Connected to 100uA current source
#       Temp = A + M*(Resistance - Ohms)
#       A = -257.79559      [Intercept]
#       M =  0.25973859     [Slope]
#   Input  : mV
#   Output : Celsius
def convertTemp(val):
    Resistance = (val / 0.1)    # converts mV/mA --> Ohms
    A = -257.79559      # [Intercept]
    M =  0.25973859     # [Slope]
    return (M*Resistance + A)

# Alternate Temperature conversion for SCA internal
#
def convertTemp_SCA(val):
    return


def toleranceCheck(measure, expect, tol):
    if (measure <= (1 + tol)*expect) and (measure >= (1 - tol)*expect):
        print("Pass")
    else:
        print("Fail")
    return

if __name__ == '__main__':
    main()
