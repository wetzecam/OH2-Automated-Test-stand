#!/bin/env python
import sys
sys.path.insert(1, '/mnt/persistent/texas/apps/reg_interface')
import ge21_promless_test_modified
from rw_reg import *
from time import *
import array
import struct

def main():

    PASS = True

    parseXML()

    # check That SCA is ready
    scaReady = parseInt(readReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.STATUS.READY')))

    if scaReady == 1:
        PASS = check_fpga_load_paths()
    else :
        print("FAIL: SCA not Ready, GBT1 -> FPGA loading path not tested!!!")
        PASS = False

    word = ''
    if PASS:
        word = 'PASSED'
    else :
        word = 'FAILED'

    print('Test of Load FPGA from GBT1: %s' % word)


def check_fpga_load_paths():
    #returns true if test passes
    passFail = True
    failCount = ge21_promless_test_modified.main()
    if failCount > 0:
        print("FAIL: fpga loading encountered %d errors" % failCount)
        passFail = False

    return passFail


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
