#!/bin/env python
import sys
sys.path.insert(1, '/mnt/persistent/texas/apps/reg_interface')
from rw_reg import *
from time import *
import array
import struct


def main():

    parseXML()

    # Do Link Reset
    writeReg(getNode('GEM_AMC.GEM_SYSTEM.CTRL.LINK_RESET'), 1)

    link_good = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.VFAT0.LINK_GOOD')))
    sync_err_cnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.VFAT0.SYNC_ERR_CNT')))
    daq_event_cnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.VFAT0.DAQ_EVENT_CNT')))
    daq_crc_err_cnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.VFAT0.DAQ_CRC_ERROR_CNT')))

    if link_good != 1:
        print('FAIL: VFAT0 Link is NOT GOOD')
        print('GEM_AMC.OH_LINKS.OH0.VFAT0.LINK_GOOD = %d' % link_good)
    if sync_err_cnt != 0:
        print('FAIL: VFAT0 has Non-zero Sync Error Count')
        print('GEM_AMC.OH_LINKS.OH0.VFAT0.SYNC_ERR_CNT = %d' % sync_err_cnt)
    if daq_event_cnt != 0:
        print('FAIL: VFAT0 has Non-zero DAQ Event Count')
        print('GEM_AMC.OH_LINKS.OH0.VFAT0.DAQ_EVENT_CNT = %d' % daq_event_cnt)
    if daq_crc_err_cnt != 0:
        print('FAIL: VFAT0 has Non-zero DAQ Critical Error Count')
        print('GEM_AMC.OH_LINKS.OH0.VFAT0.DAQ_CRC_ERROR_CNT = %d' % daq_crc_err_cnt)



if __name__ == '__main__':
    main()
