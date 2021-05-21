#!/bin/sh

./program_full_fw.sh

OH=0

python vfat_interact.py
# Phase Scan GBT1
python ./reg_interface/gbt_ge21_map.py $OH 0 ge21-phase-scan ./gbt_config/GBTX_GE21_OHv2_GBT_0_minimal_2020-01-17.txt

# Phase Scan GBT2
python ./reg_interface/gbt_ge21_map.py $OH 1 ge21-phase-scan ./gbt_config/GBTX_GE21_OHv2_GBT_1_minimal_2020-01-31.txt

# Program "Best" Phases GBT1
python ./reg_interface/gbt_ge21_map.py 0 0 ge21-program-phases ./gbt_config/GBTX_GE21_OHv2_GBT_0_minimal_2020-01-17.txt 8 7 7 7 6 9

# Program "Best" Phases GBT2
python ./reg_interface/gbt_ge21_map.py 0 1 ge21-program-phases ./gbt_config/GBTX_GE21_OHv2_GBT_1_minimal_2020-01-31.txt 8 7 7 7 6 9

OH_NUMBER=0
VFAT_MIN=1
VFAT_MAX=11

python ./reg_interface/sbit_timing_scan_oh_sbit_hitmap.py $OH_NUMBER $VFAT_MIN $VFAT_MAX
