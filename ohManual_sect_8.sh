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
cd ~/apps/reg_interface/
OH=0
# Fix This!! These should report a failure with 'FAIL' in log file otw it will be undetected!
python gbt_ge21_map.py $OH 0 config ~/gbt_config/GBTX_GE21_OHv2_GBT_0_minimal_2020-01-17.txt
python gbt_ge21_map.py $OH 1 config ~/gbt_config/GBTX_GE21_OHv2_GBT_1_minimal_2020-01-31.txt
cd ~/oh_testing/
python check_ctp7_comm.py
