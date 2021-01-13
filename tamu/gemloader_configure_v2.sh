#!/bin/sh

#LOAD_BIT_FILE=/mnt/persistent/texas/oh_fw/evka_ohv3a_test0.bit
#LOAD_BIT_FILE=/mnt/persistent/texas/oh_fw/OH-20180306-3.1.0.B.bit
#LOAD_BIT_FILE=/mnt/persistent/texas/oh_fw/OH-20180223-3.0.10.A.bit
#LOAD_BIT_FILE=/mnt/persistent/texas/oh_fw/oh_ge21_mike.bit

#LOAD_BIT_FILE=/mnt/persistent/texas/oh_fw/optohybrid_top_20190130_fixed_pinout_ge21_ohv1.bit
#LOAD_BIT_FILE=/mnt/persistent/texas/oh_fw/OH_3.2.2.2A.bit
#LOAD_BIT_FILE=/mnt/persistent/texas/oh_fw/oh_200t.bit
#LOAD_BIT_FILE=/mnt/persistent/texas/oh_fw/oh_200t_vivado.bit
#LOAD_BIT_FILE=/mnt/persistent/texas/oh_fw/oh_200t_comp.bit
LOAD_BIT_FILE=/mnt/persistent/texas/oh_testing/oh_fw/oh_ge21v2_loopback_120.bit

echo "Loading $LOAD_BIT_FILE"
gemloader load $LOAD_BIT_FILE
#/mnt/persistent/texas/tamu/gemloader/gemloader_clear_header.sh

mpoke 0x6a000000 1       #enable the loader fw core
#mpoke 0x6a000004 7694183 #number of bytes to load -- OTMB mez (v6 190T)
#mpoke 0x6a000004 5465074 #number of bytes to load -- OHv3a (v6 130T)
#mpoke 0x6a000004 5465091 #number of bytes to load -- OHv3b (v6 130T)
#mpoke 0x6a000004 3825898 #3825889 #number of bytes to load -- GE2/1 OHv1 (A7 75T)
#mpoke 0x6a000004 9730753 #number of bytes to load -- GE2/1 OHv2 (A7 200T)
#mpoke 0x6a000004 1243286 #number of bytes to load -- GE2/1 OHv2 compressed (A7 200T)
#mpoke 0x6a000004  939734 #number of bytes to load -- GE2/1 OHv2 compressed (A7 200T)
#mpoke 0x6a000004  5465074 #number of bytes to load -- GE2/1 OHv2 compressed (A7 200T)
mpoke 0x6a000004  939733 #number of bytes to load -- GE2/1 OHv2 compressed (A7 200T)
