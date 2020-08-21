#!/bin/env python
import sys
sys.path.insert(1, '/mnt/persistent/texas/apps/reg_interface')
from rw_reg import *
from time import *
import array
import struct

def main():

    parseXML()

    writeReg(getNode('GEM_AMC.TTC.GENERATOR.ENABLE'), 1)
    writeReg(getNode('GEM_AMC.TTC.GENERATOR.SINGLE_HARD_RESET'), 1)

    readKW('RELEASE')

    writeReg(getNode('GEM_AMC.GEM_SYSTEM.CTRL.LINK_RESET'), 1)
    sleep(1)
    writeReg(getNode('GEM_AMC.TRIGGER.CTRL.CNT_RESET'), 1)
    # verify error counters are 0 or low value, not increment
    readKW('GEM_AMC.TRIGGER.OH0')



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
