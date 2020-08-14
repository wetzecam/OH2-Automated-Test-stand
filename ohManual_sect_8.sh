#!/bin/sh

# starting from working directory /home/texas/oh_testing/ on CTP7
# this script will perform the contents of section 8 of Rice OH testing manual
# and dumps all outputs to command line

cd ~/tamu
# Load the CTP7 firmware
./cold_boot_invert_rx.sh
# Load OH firmware to CTP7 RAM
./gemloader_configure_v2.sh
# Configure the GBTs (0 and 1)

cd ~/oh_testing/
python configure_gbts.py
python check_ctp7_comm.py
