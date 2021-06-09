#!/usr/bin/env python
import sys
sys.path.insert(1, '/mnt/persistent/texas/apps/reg_interface')
from rw_reg import *
from time import *
import array
import struct
import signal
import sys

DEBUG=False

class Colors:
    WHITE   = '\033[97m'
    CYAN    = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE    = '\033[94m'
    YELLOW  = '\033[93m'
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    ENDC    = '\033[0m'

ADDR_IC_ADDR = None
ADDR_IC_WRITE_DATA = None
ADDR_IC_EXEC_WRITE = None
ADDR_IC_EXEC_READ = None

ADDR_LINK_RESET = None

ADDRESS_TABLE_SLOW_CTRL_ONLY = '/mnt/persistent/texas/gem_amc_top_SLOW_CTRL_ONLY.xml'

V3B_GBT0_ELINK_TO_VFAT = {0: 15, 1: 14, 2: 13, 3: 12, 6: 7, 8: 23}
V3B_GBT1_ELINK_TO_VFAT = {1: 4, 2: 2, 3: 3, 4: 8, 5: 0, 6: 6, 7: 16, 8: 5, 9: 1}
V3B_GBT2_ELINK_TO_VFAT = {1: 9, 2: 20, 3: 21, 4: 11, 5: 10, 6: 18, 7: 19, 8: 17, 9: 22}
V3B_GBT_ELINK_TO_VFAT = [V3B_GBT0_ELINK_TO_VFAT, V3B_GBT1_ELINK_TO_VFAT, V3B_GBT2_ELINK_TO_VFAT]

GE21_GBT0_ELINK_TO_VFAT = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
GE21_GBT1_ELINK_TO_VFAT = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11}
GE21_GBT_ELINK_TO_VFAT = [GE21_GBT0_ELINK_TO_VFAT, GE21_GBT1_ELINK_TO_VFAT]

GE21_GBT0_ELINK_TO_FPGA = [6, 7, 8, 9]
GE21_GBT1_ELINK_TO_FPGA = [6, 7, 8, 9, 10, 11, 12, 13]
GE21_GBT_ELINK_TO_FPGA = [GE21_GBT0_ELINK_TO_FPGA, GE21_GBT1_ELINK_TO_FPGA]

GBT_ELINK_SAMPLE_PHASE_REGS = [[69, 73, 77], [67, 71, 75], [93, 97, 101], [91, 95, 99], [117, 121, 125], [115, 119, 123], [141, 145, 149], [139, 143, 147], [165, 169, 173], [163, 167, 171], [189, 193, 197], [187, 191, 195], [213, 217, 221], [211, 215, 219]]

PHASE_SCAN_NUM_SLOW_CONTROL_READS = 10000

GBT0_Config_File = "gbt_config/GBTX_GE21_OHv2_GBT_0_minimal_2020-01-17.txt"
GBT1_Config_File = "gbt_config/GBTX_GE21_OHv2_GBT_1_minimal_2020-01-31.txt"

def main():
    ohSelect = 0
    gbtSelect = 0
    filename = "gbt_config/GBTX_GE21_OHv2_GBT_0_minimal_2020-01-17.txt"

    parseXML()

    initGbtRegAddrs()

    scan_vfats(0,0,GBT0_Config_File)
    scan_vfats(0,1,GBT1_Config_File)
    ## ADD VFAT phase Picking / Programming HERE!!!!


def scan_fpga(ohSelect,gbtSelect,configFile):
    # prep
    writeReg(getNode('GEM_AMC.GEM_TESTS.OH_LOOPBACK.CTRL.OH_SELECT'), ohSelect)

    # print the result table header
    tableColWidth = 13
    header = "Phase".ljust(tableColWidth)
    for elink in GE21_GBT_ELINK_TO_FPGA[gbtSelect]:
        header += ("e-link %d" % elink).ljust(tableColWidth)
    print("")
    print(header)

    # start the scan
    for phase in range(0, 15):
        writeReg(getNode('GEM_AMC.GEM_SYSTEM.TESTS.GBT_LOOPBACK_EN'), 0)

        # set phase on all elinks
        for elink in GE21_GBT_ELINK_TO_FPGA[gbtSelect]:
            for subReg in range(0, 3):
                addr = GBT_ELINK_SAMPLE_PHASE_REGS[elink][subReg]
                value = (regs[addr] & 0xf0) + phase
                wReg(ADDR_IC_ADDR, addr)
                wReg(ADDR_IC_WRITE_DATA, value)
                wReg(ADDR_IC_EXEC_WRITE, 1)
                sleep(0.000001) # writing is too fast for CVP13 :)

        # reset the PRBS tester, and give some time to accumulate statistics
        sleep(0.001)
        writeReg(getNode('GEM_AMC.GEM_TESTS.OH_LOOPBACK.CTRL.RESET'), 1)
        writeReg(getNode('GEM_AMC.GEM_SYSTEM.TESTS.GBT_LOOPBACK_EN'), 1)
        sleep(5)

        # check all elinks for errors
        result = ("%d" % phase).ljust(tableColWidth)
        for elink in GE21_GBT_ELINK_TO_FPGA[gbtSelect]:
            prbsLocked = parseInt(readReg(getNode('GEM_AMC.GEM_TESTS.OH_LOOPBACK.GBT_%d.ELINK_%d.PRBS_LOCKED' % (gbtSelect, elink))))
            megaWordCnt = parseInt(readReg(getNode('GEM_AMC.GEM_TESTS.OH_LOOPBACK.GBT_%d.ELINK_%d.MEGA_WORD_CNT' % (gbtSelect, elink))))
            errorCnt = parseInt(readReg(getNode('GEM_AMC.GEM_TESTS.OH_LOOPBACK.GBT_%d.ELINK_%d.ERROR_CNT' % (gbtSelect, elink))))

            color = Colors.GREEN if errorCnt == 0 else Colors.RED
            res = ('%d' % errorCnt).ljust(tableColWidth)
            if (prbsLocked == 0) or (megaWordCnt < 80):
                color = Colors.RED
                res = "NO LOCK".ljust(tableColWidth)

            result += color + res + Colors.ENDC

            if DEBUG:
                print color + 'Phase = %d, ELINK %d: PRBS_LOCKED=%d, MEGA_WORD_CNT=%d, ERROR_CNT=%d' % (phase, elink, prbsLocked, megaWordCnt, errorCnt) + Colors.ENDC

        print(result)

    writeReg(getNode('GEM_AMC.GEM_SYSTEM.TESTS.GBT_LOOPBACK_EN'), 0)

def scan_vfats(ohSelect, gbtSelect, configFile):
    heading("Hello, I'm you GBT controller :)")

    if(checkGbtReady(ohSelect,gbtSelect) == 1):
        selectGbt(ohSelect,gbtSelect)
    else:
        printRed("Sorry, OH%d GBT%d link is not ready.. check the following your OH is on, the fibers are plugged in correctly, the CTP7 TX polarity is correct, and muy importante, check that your GBTX is fused with at least the minimal config.." % (ohSelect, gbtSelect))
        return

    subheading('Configuring OH%d GBT%d' % (ohSelect, gbtSelect))

    if configFile[-3:] != "txt":
        printRed("Seems like the file is not a txt file, please provide a txt file generated with the GBT programmer software")
        return
    if not os.path.isfile(configFile):
        printRed("Can't find the file %s" % configFile)
        return

    timeStart = clock()

    regs = downloadConfig(ohSelect, gbtSelect, configFile)

    totalTime = clock() - timeStart
    print('time took = ' + str(totalTime) + 's')

    # Phase Scanning:
    initVfatRegAddrs()
    for elink, vfat in GE21_GBT_ELINK_TO_VFAT[gbtSelect].items():
        subheading('Scanning elink %d phase, corresponding to VFAT%d' % (elink, vfat))
        for phase in range(0, 15):
            # set phase
            for subReg in range(0, 3):
                addr = GBT_ELINK_SAMPLE_PHASE_REGS[elink][subReg]
                value = (regs[addr] & 0xf0) + phase
                wReg(ADDR_IC_ADDR, addr)
                wReg(ADDR_IC_WRITE_DATA, value)
                wReg(ADDR_IC_EXEC_WRITE, 1)
            # reset the link, give some time to lock and accumulate any sync errors and then check VFAT comms
            sleep(0.1)
            writeReg(getNode('GEM_AMC.GEM_SYSTEM.CTRL.LINK_RESET'), 1)
            sleep(0.001)
            cfgRunGood = 1
            cfgAddr = getNode('GEM_AMC.OH.OH%d.GEB.VFAT%d.CFG_RUN' % (ohSelect, vfat)).real_address
            for i in range(PHASE_SCAN_NUM_SLOW_CONTROL_READS):
                #ret = readReg(getNode('GEM_AMC.OH.OH%d.GEB.VFAT%d.CFG_RUN' % (ohSelect, vfat)))
                ret = rReg(cfgAddr)
                #if (ret != '0x00000000' and ret != '0x00000001'):
                if (ret != 0 and ret != 1):
                    cfgRunGood = 0
                    break
            #sleep(0.3)
            #sleep(0.5)
            linkGood = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH%d.VFAT%d.LINK_GOOD' % (ohSelect, vfat))))
            syncErrCnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH%d.VFAT%d.SYNC_ERR_CNT' % (ohSelect, vfat))))
            color = Colors.GREEN
            prefix = 'GOOD: '
            if (linkGood == 0) or (syncErrCnt > 0) or (cfgRunGood == 0):
                color = Colors.RED
                prefix = '>>>>>>>> BAD <<<<<<<< '
            print color, prefix, 'Phase = %d, VFAT%d LINK_GOOD=%d, SYNC_ERR_CNT=%d, CFG_RUN_GOOD=%d' % (phase, vfat, linkGood, syncErrCnt, cfgRunGood), Colors.ENDC

    # End of Phase Scanning

def downloadConfig(ohIdx, gbtIdx, filename):
    f = open(filename, 'r')

    #for now we'll operate with 8 bit words only
    writeReg(getNode("GEM_AMC.SLOW_CONTROL.IC.READ_WRITE_LENGTH"), 1)

    ret = []

    lines = 0
    addr = 0
    for line in f:
        value = int(line, 16)
        wReg(ADDR_IC_ADDR, addr)
        wReg(ADDR_IC_WRITE_DATA, value)
        wReg(ADDR_IC_EXEC_WRITE, 1)
        addr += 1
        lines += 1
        ret.append(value)

    print("Wrote %d registers to OH%d GBT%d" % (lines, ohIdx, gbtIdx))
    if lines < 366:
        printRed("looks like you gave me an incomplete file, since I found only %d registers, while a complete config should contain 366 registers")

    f.close()

    return ret

def destroyConfig():
    for i in range(0, 369):
        wReg(ADDR_IC_ADDR, i)
        wReg(ADDR_IC_WRITE_DATA, 0)
        wReg(ADDR_IC_EXEC_WRITE, 1)

def initGbtRegAddrs():
    global ADDR_IC_ADDR
    global ADDR_IC_WRITE_DATA
    global ADDR_IC_EXEC_WRITE
    global ADDR_IC_EXEC_READ
    ADDR_IC_ADDR = getNode('GEM_AMC.SLOW_CONTROL.IC.ADDRESS').real_address
    ADDR_IC_WRITE_DATA = getNode('GEM_AMC.SLOW_CONTROL.IC.WRITE_DATA').real_address
    ADDR_IC_EXEC_WRITE = getNode('GEM_AMC.SLOW_CONTROL.IC.EXECUTE_WRITE').real_address
    ADDR_IC_EXEC_READ = getNode('GEM_AMC.SLOW_CONTROL.IC.EXECUTE_READ').real_address

def initVfatRegAddrs():
    global ADDR_LINK_RESET
    ADDR_LINK_RESET = getNode('GEM_AMC.GEM_SYSTEM.CTRL.LINK_RESET').real_address

def selectGbt(ohIdx, gbtIdx):
    linkIdx = ohIdx * 2 + gbtIdx

    writeReg(getNode('GEM_AMC.SLOW_CONTROL.IC.GBTX_LINK_SELECT'), linkIdx)

    return 0

def checkGbtReady(ohIdx, gbtIdx):
    return parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH%d.GBT%d_READY' % (ohIdx, gbtIdx))))

def signal_handler(sig, frame):
    print("Exiting..")
    writeReg(getNode('GEM_AMC.GEM_SYSTEM.TESTS.GBT_LOOPBACK_EN'), 0)
    sys.exit(0)

def check_bit(byteval,idx):
    return ((byteval&(1<<idx))!=0);

def debug(string):
    if DEBUG:
        print('DEBUG: ' + string)

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
