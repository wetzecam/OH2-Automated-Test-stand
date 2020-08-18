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

    link_good = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.VFAT15.LINK_GOOD')))
    sync_err_cnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.VFAT15.SYNC_ERR_CNT')))
    daq_event_cnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.VFAT15.DAQ_EVENT_CNT')))
    daq_crc_err_cnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH0.VFAT15.DAQ_CRC_ERROR_CNT')))

    if link_good != 1:
        


if __name__ == '__main__':
    main()
