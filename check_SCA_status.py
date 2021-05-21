#!/bin/env python
import sys
sys.path.insert(1, '/mnt/persistent/texas/apps/reg_interface')
from rw_reg import *
from time import *
import array
import struct

def main():

    PASS = True

    parseXML()

    PASS = check_SCA_ASIC()

    if PASS:
        word = 'PASSED'
    else :
        reset_SCA_ASIC()
        if check_SCA_ASIC():
            word = 'PASSED'
        else :
            word = 'FAIL'

    print('Check SCA ASIC: %s' % word)


def check_SCA_ASIC():
    #returns true if test passes
    passFAIL = True

    if parseInt(readReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.STATUS.READY'))) != 1:
        print("SCA ASIC not READY!")
        passFAIL =  False
    else :
        print("SCA ASIC GOOD!")

    return passFAIL

def reset_SCA_ASIC():
    # reset SCA
    writeReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.CTRL.MODULE_RESET'), 1)


def readKW(args):
    """Read all registers containing KeyWord. USAGE: readKW <KeyWord>"""
    if getNodesContaining(args) is not None and args!='':
        for reg in getNodesContaining(args):
            address = reg.real_address
            if 'r' in str(reg.permission):
                print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7),readReg(reg)
            elif reg.isModule: print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7) #,'Module!'
            else: print hex(address).rstrip('L'),reg.permission,'\t',tabPad(reg.name,7) #,'No read permission!'
    else: print args,'not found!'

if __name__ == '__main__':
    main()
