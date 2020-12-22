#!/bin/sh

cd /mnt/persistent/texas/tamu/
./gemloader_configure_v2_full.sh

cd /mnt/persistent/texas/apps/reg_interface/
python ge21_promless_test.py 1 1
