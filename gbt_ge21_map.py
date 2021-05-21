#!/usr/bin/env python

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

def main():

    command = ""
    ohSelect = 0
    gbtSelect = 0

    if len(sys.argv) < 4:
        print('Usage: gbt.py <oh_num> <gbt_num> <command>')
        print('available commands:')
        print('  config <config_filename_txt>:   Configures the GBT with the given config file (must use the txt version of the config file, can be generated with the GBT programmer software)')
        print('  v3b-phase-scan <base_config_filename_txt>:   Configures the GBT with the given config file, and performs an elink phase scan while checking the VFAT communication for each phase')
        print('  ge21-phase-scan <base_config_filename_txt>:   Configures the GBT with the given config file, and performs an elink phase scan while checking the VFAT communication for each phase')
        print('  ge21-fpga-phase-scan <base_config_filename_txt>:   Configures the GBT with the given config file, and performs a phase scan on elinks connected to the FPGA while checking the PRBS error count for each phase. NOTE: This requires the FPGA to be loaded with a loopback firmware (future OH fw versions will probably have the PRBS sender built in)')
        print('  ge21-program-phases <elink_0_phase> <elink_1_phase> <elink_2_phase> <elink_3_phase> etc... :   Programs the provided GBTX sampling phases to as many elinks as the numbers provided (can also include wide-bus elinks)')
        return
    else:
        ohSelect = int(sys.argv[1])
        gbtSelect = int(sys.argv[2])
        command = sys.argv[3]

    if ohSelect > 11:
        printRed("The given OH index (%d) is out of range (must be 0-11)" % ohSelect)
        return
    if gbtSelect > 2:
        printRed("The given GBT index (%d) is out of range (must be 0-2)" % gbtSelect)
        return

    if os.path.isfile(ADDRESS_TABLE_SLOW_CTRL_ONLY) and (command != 'v3b-phase-scan'):
        parseXML('/mnt/persistent/texas/gem_amc_top_SLOW_CTRL_ONLY.xml')
    else:
        parseXML()

    initGbtRegAddrs()

    signal.signal(signal.SIGINT, signal_handler)

    heading("Hello, I'm your GBT controller :)")

    if (checkGbtReady(ohSelect, gbtSelect) == 1):
        selectGbt(ohSelect, gbtSelect)
    else:
        printRed("Sorry, OH%d GBT%d link is not ready.. check the following: your OH is on, the fibers are plugged in correctly, the CTP7 TX polarity is correct, and muy importante, check that your GBTX is fused with at least the minimal config.." % (ohSelect, gbtSelect))
        return

    if (command == 'config') or (command == 'v3b-phase-scan') or (command == 'ge21-phase-scan') or (command == 'ge21-program-phases') or (command == 'ge21-phase-scan-new') or (command == 'ge21-fpga-phase-scan'):
        if len(sys.argv) < 5:
            print("For this command, you also need to provide a config file")
            return

        subheading('Configuring OH%d GBT%d' % (ohSelect, gbtSelect))
        filename = sys.argv[4]
        if filename[-3:] != "txt":
            printRed("Seems like the file is not a txt file, please provide a txt file generated with the GBT programmer software")
            return
        if not os.path.isfile(filename):
            printRed("Can't find the file %s" % filename)
            return

        timeStart = clock()

        regs = downloadConfig(ohSelect, gbtSelect, filename)

        totalTime = clock() - timeStart
        print('time took = ' + str(totalTime) + 's')

        if (command == 'v3b-phase-scan'):
            initVfatRegAddrs()
            for elink, vfat in V3B_GBT_ELINK_TO_VFAT[gbtSelect].items():
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
                    # wReg(ADDR_LINK_RESET, 1)
                    sleep(0.3)
                    linkGood = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH%d.VFAT%d.LINK_GOOD' % (ohSelect, vfat))))
                    syncErrCnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH%d.VFAT%d.SYNC_ERR_CNT' % (ohSelect, vfat))))
                    cfgRun = readReg(getNode('GEM_AMC.OH.OH%d.GEB.VFAT%d.CFG_RUN' % (ohSelect, vfat)))
                    color = Colors.GREEN
                    prefix = 'GOOD: '
                    if (linkGood == 0) or (syncErrCnt > 0) or (cfgRun != '0x00000000' and cfgRun != '0x00000001'):
                        color = Colors.RED
                        prefix = '>>>>>>>> BAD <<<<<<<< '
                    print color, prefix, 'Phase = %d, VFAT%d LINK_GOOD=%d, SYNC_ERR_CNT=%d, CFG_RUN=%s' % (phase, vfat, linkGood, syncErrCnt, cfgRun), Colors.ENDC

        elif (command == 'ge21-phase-scan'):
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

        elif (command == 'ge21-fpga-phase-scan'):
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

        elif (command == 'ge21-phase-scan-new'):
            initVfatRegAddrs()
            resultStr = "Phase"
            for elink, vfat in GE21_GBT_ELINK_TO_VFAT[gbtSelect].items():
                resultStr += "\t\tVFAT%d" % vfat
            print(resultStr)

            for phase in range(0, 15):
                for elink, vfat in GE21_GBT_ELINK_TO_VFAT[gbtSelect].items():
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

                # check slow control for every vfat
                cfgRunErrCntArr = []
                for elink, vfat in GE21_GBT_ELINK_TO_VFAT[gbtSelect].items():
                    cfgRunErrCnt = 0
                    cfgRunAddr = getNode('GEM_AMC.OH.OH%d.GEB.VFAT%d.CFG_RUN' % (ohSelect, vfat)).real_address
                    cfgHwIdAddr = getNode('GEM_AMC.OH.OH%d.GEB.VFAT%d.HW_ID' % (ohSelect, vfat)).real_address
                    cfgHwIdVerAddr = getNode('GEM_AMC.OH.OH%d.GEB.VFAT%d.CFG_RUN' % (ohSelect, vfat)).real_address
                    for i in range(PHASE_SCAN_NUM_SLOW_CONTROL_READS):
                        retRun = rReg(cfgRunAddr)
                        retHwId = rReg(cfgHwIdAddr)
                        retHwIdVer = rReg(cfgHwIdVerAddr)
                        if (retRun != 0 and retRun != 1) or (retHwId != 0x56464154) or (retHwIdVer > 100):
                            cfgRunErrCnt += 1
                            if cfgRunErrCnt >= 10:
                                break # failing reads take much longer than good ones
                    cfgRunErrCntArr.append(cfgRunErrCnt)

                # check sync errors
                syncErrCntArr = []
                for elink, vfat in GE21_GBT_ELINK_TO_VFAT[gbtSelect].items():
                    syncErrCnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH%d.VFAT%d.SYNC_ERR_CNT' % (ohSelect, vfat))))
                    syncErrCntArr.append(syncErrCnt)

                resultStr = "%d" % phase
                for i in range(len(GE21_GBT_ELINK_TO_VFAT[gbtSelect])):
                    good = (cfgRunErrCntArr[i] == 0 and syncErrCntArr[i] == 0)
                    goodBadStr = "GOOD" if good else "BAD"
                    color = Colors.GREEN if good else Colors.RED
                    resultStr += "\t\t%s%s%s" % (color, goodBadStr, Colors.ENDC)
                print(resultStr)

        elif (command == 'ge21-program-phases'):
            initVfatRegAddrs()

            numPhases = len(sys.argv) - 5
            for elink in range(numPhases):
                phase = int(sys.argv[5+elink])
                subheading('Setting phase = %d for elink %d' % (phase, elink))
                for subReg in range(0, 3):
                    addr = GBT_ELINK_SAMPLE_PHASE_REGS[elink][subReg]
                    value = (regs[addr] & 0xf0) + phase
                    wReg(ADDR_IC_ADDR, addr)
                    wReg(ADDR_IC_WRITE_DATA, value)
                    wReg(ADDR_IC_EXEC_WRITE, 1)

                if elink in GE21_GBT_ELINK_TO_VFAT[gbtSelect]:
                    vfat = GE21_GBT_ELINK_TO_VFAT[gbtSelect][elink]
                    # reset the link, give some time to lock and accumulate any sync errors and then check VFAT comms
                    sleep(0.1)
                    writeReg(getNode('GEM_AMC.GEM_SYSTEM.CTRL.LINK_RESET'), 1)
                    sleep(0.001)
                    cfgRunGood = 1
                    cfgAddr = getNode('GEM_AMC.OH.OH%d.GEB.VFAT%d.CFG_RUN' % (ohSelect, vfat)).real_address
                    for i in range(10000):
                        #ret = readReg(getNode('GEM_AMC.OH.OH%d.GEB.VFAT%d.CFG_RUN' % (ohSelect, vfat)))
                        ret = rReg(cfgAddr)
                        #if (ret != '0x00000000' and ret != '0x00000001'):
                        if (ret != 0 and ret != 1):
                            print("bad read of CFG_RUN on elink %d VFAT%d, iteration #%d: %s" % (elink, vfat, i, hex(ret)))
                            cfgRunGood = 0
                            break
                    #sleep(0.3)
                    #sleep(0.5)
                    linkGood = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH%d.VFAT%d.LINK_GOOD' % (ohSelect, vfat))))
                    syncErrCnt = parseInt(readReg(getNode('GEM_AMC.OH_LINKS.OH%d.VFAT%d.SYNC_ERR_CNT' % (ohSelect, vfat))))
                    color = Colors.GREEN
                    prefix = 'COMMUNICATION GOOD on elink %d VFAT%d: ' % (elink, vfat)
                    if (linkGood == 0) or (syncErrCnt > 0) or (cfgRunGood == 0):
                        color = Colors.RED
                        prefix = 'COMMUNICATION BAD on elink %d VFAT%d: ' % (elink, vfat)
                    print color, prefix, 'Phase = %d, LINK_GOOD=%d, SYNC_ERR_CNT=%d, CFG_RUN_GOOD=%d' % (phase, linkGood, syncErrCnt, cfgRunGood), Colors.ENDC


    elif command == 'destroy':
        subheading('Destroying configuration of OH%d GBT%d' % (ohSelect, gbtSelect))
        destroyConfig()

    else:
        printRed("Unrecognized command '%s'" % command)
        return

    print("")
    print("bye now..")

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
