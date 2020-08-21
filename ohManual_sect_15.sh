#!/bin/sh

OH=0

python vfat_interact.py

python gbt_ge21_map.py $OH 0 ge21-phase-scan ~/gbt_config/GBTX_GE21_OHv2_GBT_0_minimal_2020-01-17.txt

python gbt_ge21_map.py 0 0 ge21-program-phases ~/gbt_config/GBTX_GE21_OHv2_GBT_0_minimal_2020-01-17.txt 9 0 0 0 0 0

OH_NUMBER=0
VFAT_MIN=0
VFAT_MAX=11
cd /mnt/persistent/texas/apps/reg_interface/
python sbit_timing_scan_oh_sbit_hitmap.py $OH_NUMBER $VFAT_MIN $VFAT_MAX
