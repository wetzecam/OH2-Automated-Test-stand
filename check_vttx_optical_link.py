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

    #reset Trigger Module
    writeReg(getNode('GEM_AMC.TRIGGER.CTRL.MODULE_RESET'), 1)

    PASS = check_vttx_link()

    word = ''
    if PASS:
        word = 'PASSED'
    else :
        word = 'FAILED'

    print('Test VTTX Optical Links with CTP7: %s' % word)


    #Example of writing a register
    #writeReg(getNode('GEM_AMC.GEM_SYSTEM.CTRL.LINK_RESET'), 1)

    #Example of reading a register
    #result = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.GBT0_READY')))
    #print("OH0 GBT0 ready = %d" % result)

def check_vttx_link():
    #returns true if test passes
    passFail = True

    link0_missed = parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK0_MISSED_COMMA_CNT')))
    link1_missed = parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK1_MISSED_COMMA_CNT')))
    link0_overflow = parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK0_OVERFLOW_CNT')))
    link1_overflow = parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK1_OVERFLOW_CNT')))
    link0_underflow = parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK0_UNDERFLOW_CNT')))
    link1_underflow = parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK1_UNDERFLOW_CNT')))

    # wait a few seconds to ensure no increment
    sleep(3)

    cntChange = link0_missed - parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK0_MISSED_COMMA_CNT')))
    if cntChange != 0:
        print('FAIL: GEM_AMC.TRIGGER.OH0.LINK0_MISSED_COMMA_CNT incremented by, %d' % cntChange)
        passFail = False

    cntChange = link1_missed - parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK1_MISSED_COMMA_CNT')))
    if cntChange != 0:
        print('FAIL: GEM_AMC.TRIGGER.OH0.LINK1_MISSED_COMMA_CNT incremented by, %d' % cntChange)
        passFail = False

    cntChange = link0_overflow - parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK0_OVERFLOW_CNT')))
    if cntChange != 0:
        print('FAIL: GEM_AMC.TRIGGER.OH0.LINK0_OVERFLOW_CNT incremented by, %d' % cntChange)
        passFail = False

    cntChange =  link1_overflow - parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK1_OVERFLOW_CNT')))
    if cntChange != 0:
        print('FAIL: GEM_AMC.TRIGGER.OH0.LINK1_OVERFLOW_CNT incremented by, %d' % cntChange)
        passFail = False

    cntChange = link0_underflow - parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK0_UNDERFLOW_CNT')))
    if cntChange != 0:
        print('FAIL: GEM_AMC.TRIGGER.OH0.LINK0_UNDERFLOW_CNT incremented by, %d' % cntChange)
        passFail = False

    cntChange = link1_underflow - parseInt(readReg(getNode('GEM_AMC.TRIGGER.OH0.LINK1_UNDERFLOW_CNT')))
    if cntChange != 0:
        print('FAIL: GEM_AMC.TRIGGER.OH0.LINK1_UNDERFLOW_CNT incremented by, %d' % cntChange)
        passFail = False


    print('readKW GEM_AMC.TRIGGER.OH0')
    readKW('GEM_AMC.TRIGGER.OH0') # prints status for log file

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
