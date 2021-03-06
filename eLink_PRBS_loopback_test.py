#!/bin/env python
import sys
sys.path.insert(1, '/mnt/persistent/texas/apps/reg_interface')
from rw_reg import *
from time import *
import array
import struct

eLink_addrs = ('GBT_0.ELINK_6',
          'GBT_0.ELINK_7',
          'GBT_0.ELINK_8',
          'GBT_0.ELINK_9',
          'GBT_1.ELINK_6',
          'GBT_1.ELINK_7',
          'GBT_1.ELINK_8',
          'GBT_1.ELINK_9',
          'GBT_1.ELINK_10',
          'GBT_1.ELINK_11',
          'GBT_1.ELINK_12',
          'GBT_1.ELINK_13')

# 10^12 = 8*10^6[MegaWord] * 0.125*10^6
acceptCriteria = 12500

def main():

    parseXML()

    # select the OH to be used
    writeReg(getNode('GEM_AMC.GEM_TESTS.OH_LOOPBACK.CTRL.OH_SELECT'), 0)

    # Make sure Loopback is Disabled
    writeReg(getNode('GEM_AMC.GEM_SYSTEM.TESTS.GBT_LOOPBACK_EN'), 0)

    # reset loopback counters
    writeReg(getNode('GEM_AMC.GEM_TESTS.OH_LOOPBACK.CTRL.RESET'), 1)

    # Put CTP7 into loopback testing mode
    writeReg(getNode('GEM_AMC.GEM_SYSTEM.TESTS.GBT_LOOPBACK_EN'), 1)

    # reset loopback counters
    # writeReg(getNode('GEM_AMC.GEM_TESTS.OH_LOOPBACK.CTRL.RESET'), 1)

    noFailCount = 0
    while noFailCount < acceptCriteria and noFailCount >= 0:
        noFailCount = check_loopback_regs()
        if noFailCount == -1:
            print('FAIL: an E-LINK is not locked')
            print('Integrated test of Internal Links : FAILED')
            return
        elif noFailCount == -2:
            print('FAIL: There is a non-zero error counter')
            print('Integrated test of Internal Links : FAILED')
            return

    if noFailCount >= acceptCriteria and noFailCount >0:
        print('Integrated test of Internal Links : PASSED')
    else:
        print('Integrated test of Internal Links : FAILED')




    # take CTP7 out of loopback testing mode
    writeReg(getNode('GEM_AMC.GEM_SYSTEM.TESTS.GBT_LOOPBACK_EN'), 0)
    return


def check_loopback_regs():
    #outputs lowest number of mega_word_count for all e-links under test
    # outputs: -1 if an e-link is not locked & prints status to command line
    # outputs: -2 if an error count is non-zero

    # take CTP7 out of loopback testing mode
    #writeReg(getNode('GEM_AMC.GEM_SYSTEM.TESTS.GBT_LOOPBACK_EN'), 0)

    head = 'GEM_AMC.GEM_TESTS.OH_LOOPBACK.'
    megaCount = parseInt(readReg(getNode(head+eLink_addrs[0]+'.MEGA_WORD_CNT')))
    for eLink in eLink_addrs:
        # check elink is PRBS LOCKED
        if parseInt(readReg(getNode(head+eLink+'.PRBS_LOCKED'))) != 1:
            print('FAIL: '+eLink+' PRBS Not Locked!')
            megaCount = -1
        # check elink Error Count
        if parseInt(readReg(getNode(head+eLink+'.ERROR_CNT'))) > 0:
            print('FAIL: '+eLink+' Has non-zero error count = %d' % parseInt(readReg(getNode(head+eLink+'.ERROR_CNT'))))
            megaCount = -2
        #if parseInt(readReg(getNode(head+eLink+'.MEGA_WORD_CNT'))) != megaCount:
        #    print('FAIL: '+eLink+' mega Word Count incosistent')

    return megaCount



if __name__ == '__main__':
    main()
