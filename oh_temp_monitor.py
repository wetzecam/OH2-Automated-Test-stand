#!/usr/bin/env python

from rw_reg import *
from mcs import *
from time import *
import array
import struct

DEBUG=False

def main():

    out_file_name = ""
    out_file = None
    ohMask = 0
    ohList = []

    if len(sys.argv) < 2:
        print('Usage: temperature_monitor.py <oh_mask> [out_file]')
        return
    else:
        ohMask = parseInt(sys.argv[1])
        for i in range(0,12):
            if check_bit(ohMask, i):
                ohList.append(i)
        if len(sys.argv) > 2:
            out_file_name = sys.argv[2]
            out_file = open(out_file_name, "w")

    parseXML()

    iter = 0
    while(True):
        temps = "%d\t" % iter
        for oh in range(12):
            if oh in ohList:
                tempRaw = parseInt(readReg(getNode('GEM_AMC.OH.OH%d.FPGA.ADC.CTRL.DATA_OUT' % oh)))
                temp = ((tempRaw >> 4) * 503.975 / 4096) - 273.15
                temps += "%f\t" % temp
            else:
                temps += "0.0\t"
        print(temps)
        if out_file != None:
            out_file.write("%s\n" % temps)
            out_file.flush()
        sleep(1.0)
        iter += 1
        
        

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
