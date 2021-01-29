#!/usr/bin/env python
import sys
sys.path.insert(1, '/mnt/persistent/texas/apps/reg_interface')
from rw_reg import *
from mcs import *
from time import *
import array
import struct

SLEEP_BETWEEN_COMMANDS=0.1
DEBUG=False
CTP7HOSTNAME = "eagle36"

class Colors:
    WHITE   = '\033[97m'
    CYAN    = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE    = '\033[94m'
    YELLOW  = '\033[93m'
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    ENDC    = '\033[0m'

class Virtex6Instructions:
    FPGA_ID     = 0x3C9
    USER_CODE   = 0x3C8
    SYSMON      = 0x3F7
    BYPASS      = 0x3FF
    CFG_IN      = 0x3C5
    CFG_OUT     = 0x3C4
    SHUTDN      = 0x3CD
    JPROG       = 0x3CB
    JSTART      = 0x3CC
    ISC_NOOP    = 0x3D4
    ISC_ENABLE  = 0x3D0
    ISC_PROGRAM = 0x3D1
    ISC_DISABLE = 0x3D6


ARTIX7_75T_FIRMWARE_SIZE = 3825768
ARTIX7_75T_FPGA_ID = 0x49c0
VIRTEX6_FIRMWARE_SIZE = 5464972
VIRTEX6_FPGA_ID = 0x6424a093

FIRMWARE_SIZE = ARTIX7_75T_FIRMWARE_SIZE
FPGA_ID = ARTIX7_75T_FPGA_ID

ADDR_JTAG_LENGTH = None
ADDR_JTAG_TMS = None
ADDR_JTAG_TDO = None
ADDR_JTAG_TDI = None

def main():
    instructions = ""
    ohMask = 1
    ohList = []

    for i in range(0,12):
        if check_bit(ohMask, i):
            ohList.append(i)

    parseXML()
    initJtagRegAddrs()

    heading("Hola, I'm SCA controller tester :)")

    writeReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.MANUAL_CONTROL.LINK_ENABLE_MASK'), ohMask)

    sleep(0.1)

    # enable the current source on channels 13-17 (GE2/1 OHv2 PT1000)
    #sendScaCommand(ohList, 0x14, 0x60, 0x4, 0x00a00300, False)
    sendScaCommand(ohList, 0x14, 0x60, 0x4, 0x00e00300, False)

    # Channels 18 - 32 are unused
    for ch in range(17):
#            if ch == 6 or ch == 7:
#                continue

        sendScaCommand(ohList, 0x14, 0x50, 0x4, ch << 24, False)
        results = sendScaCommand(ohList, 0x14, 0x02,    0x4, 1 << 24, True)
        for oh in range(len(results)):
            res = (results[oh] >> 24) + ((results[oh] >> 8) & 0xff00)
            if (res > 0xfff):
                printRed("ERROR: ADC returned a reading above 0xfff!!")
            res_mv = ((1.0 / 0xfff) * float(res)) * 1000
            print "Channel %d OH %d: %d counts (%s) = %fmV" % (ch, oh, res, hex(res), res_mv)
            #NEW Stuff : CAMERON Jan 2021
            if ch < 6:
                print "True Reading = %fmV" % (voltageConversion(res_mv))
            elif (ch <= 12 and ch >= 8) :
                print "Current Reading = %fA" % (currentConversion(res_mv))

        sleep(0.001)





def sendScaCommand(ohList, sca_channel, sca_command, data_length, data, doRead):
    #print('fake send: channel ' + hex(sca_channel) + ', command ' + hex(sca_command) + ', length ' + hex(data_length) + ', data ' + hex(data) + ', doRead ' + str(doRead))
    #return

    d = data

    writeReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.MANUAL_CONTROL.SCA_CMD.SCA_CMD_CHANNEL'), sca_channel)
    writeReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.MANUAL_CONTROL.SCA_CMD.SCA_CMD_COMMAND'), sca_command)
    writeReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.MANUAL_CONTROL.SCA_CMD.SCA_CMD_LENGTH'), data_length)
    writeReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.MANUAL_CONTROL.SCA_CMD.SCA_CMD_DATA'), d)
    writeReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.MANUAL_CONTROL.SCA_CMD.SCA_CMD_EXECUTE'), 0x1)
    reply = []
    if doRead:
        for i in ohList:
            reply.append(parseInt(readReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.MANUAL_CONTROL.SCA_REPLY_OH%d.SCA_RPY_DATA' % i))))
    return reply

def check_bit(byteval,idx):
    return ((byteval&(1<<idx))!=0);

def checkStatus(ohList):
    rxReady       = parseInt(readReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.STATUS.READY')))
    criticalError = parseInt(readReg(getNode('GEM_AMC.SLOW_CONTROL.SCA.STATUS.CRITICAL_ERROR')))

    statusGood = True
    for i in ohList:
        if not check_bit(rxReady, i):
            printRed("OH #%d is not ready: RX ready = %d, critical error = %d" % (i, (rxReady >> i) & 0x1, (criticalError >> i) & 0x1))
            statusGood = False

    return statusGood

def debug(string):
    if DEBUG:
        print('DEBUG: ' + string)


def printRed(string):
    print Colors.RED
    print string, Colors.ENDC


def initJtagRegAddrs():
    global ADDR_JTAG_LENGTH
    global ADDR_JTAG_TMS
    global ADDR_JTAG_TDO
    global ADDR_JTAG_TDI
    ADDR_JTAG_LENGTH = getNode('GEM_AMC.SLOW_CONTROL.SCA.JTAG.NUM_BITS').real_address
    ADDR_JTAG_TMS = getNode('GEM_AMC.SLOW_CONTROL.SCA.JTAG.TMS').real_address
    ADDR_JTAG_TDO = getNode('GEM_AMC.SLOW_CONTROL.SCA.JTAG.TDO').real_address
    #ADDR_JTAG_TDI = getNode('GEM_AMC.SLOW_CONTROL.SCA.JTAG.TDI').real_address

def heading(string):
    print Colors.BLUE
    print '\n>>>>>>> '+str(string).upper()+' <<<<<<<'
    print Colors.ENDC

def subheading(string):
    print Colors.YELLOW
    print '---- '+str(string)+' ----',Colors.ENDC

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

# Voltage Readings Conversions: Channels [0:5]
#   ADC reading through 1/4 Voltage divider
#   Output in mV
def voltageConversion(raw_value):
    return raw_value*4.0

# Current readings Channels [8:12]
# output in Amps
#
def currentConversion(raw_value):
    return raw_value*0.02

if __name__ == '__main__':
    main()
