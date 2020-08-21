#!/bin/sh

cd /mnt/persistent/texas/tamu/
./gemloader_configure_v2.sh

cd /mnt/persistent/texas/oh_testing/
python program_full_fw.py
