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

    PASS = check_GBTx_transmission_CTP7()

    word = ''
    if PASS:
        word = 'PASSED'
    else :
        word = 'FAILED'

    print('Check GBTx transmission to CTP7: %s' % word)

    PASS = check_SCA_ASIC()

    if PASS:
        word = 'PASSED'
    else :
        word = 'FAILED'

    print('Check SCA ASIC: %s' % word)


def check_GBTx_transmission_CTP7():
    #returns true if test passes
    passFAIL = True

    #perform link-reset
    writeReg(getNode('GEM_AMC.GEM_SYSTEM.CTRL.LINK_RESET'), 1)

    #check GBT0
    if parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.GBT0_READY'))) == 0:
        passFAIL =  False
    if parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.GBT0_WAS_NOT_READY'))) == 1:
        passFAIL =  False
    if parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.GBT0_RX_HAD_OVERFLOW'))) == 1:
        passFAIL =  False
    if parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.GBT0_RX_HAD_UNDERFLOW'))) == 1:
        passFAIL =  False
    #check GBT1
    if parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.GBT1_READY'))) == 0:
        passFAIL =  False
    if parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.GBT1_WAS_NOT_READY'))) == 1:
        passFAIL =  False
    if parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.GBT1_RX_HAD_OVERFLOW'))) == 1:
        passFAIL =  False
    if parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.GBT1_RX_HAD_UNDERFLOW'))) == 1:
        passFAIL =  False

    print('readKW OH_LINKS.OH0.GBT')
    readKW('OH_LINKS.OH0.GBT') # prints status for log file

    return passFAIL


def check_SCA_ASIC():
    #returns true if test passes
    passFAIL = True

    # clear error counters + reset SCA
    writeReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.CTRL.MODULE_RESET'), 1)

    if parseInt(readReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.STATUS.READY'))) != 1:
        print("FAIL: SCA ASIC not READY!")
        passFAIL =  False
    if parseInt(readReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.STATUS.CRITICAL_ERROR'))) != 0:
        print("FAIL: SCA ASIC nonzero critical error count!")
        passFAIL =  False

    errorCount = parseInt(readReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.STATUS.NOT_READY_CNT_OH0')))
    if errorCount > 2:
        print("WARN: more errors that usual\n GEM_AMC.SLOW_CONTROL.SCA.STATUS.NOT_READY_CNT_OH0 = %d" % errorCount)
    #wait a few seconds between reads to ensure no increment
    sleep(3)
    errorCount -= parseInt(readReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.STATUS.NOT_READY_CNT_OH0')))
    if errorCount != 0:
        print("FAIL: SCA ASIC error counter increasing!")
        passFAIL =  False

    readKW('GEM_AMC.SLOW_CONTROL.SCA.STATUS.READY')
    readKW('GEM_AMC.SLOW_CONTROL.SCA.STATUS.CRITICAL_ERROR')
    readKW('GEM_AMC.SLOW_CONTROL.SCA.STATUS.NOT_READY_CNT_OH0')
    return passFAIL


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
