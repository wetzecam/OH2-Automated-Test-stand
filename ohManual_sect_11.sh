#!/bin/sh

cd /mnt/persistent/texas/tamu/
./gemloader_configure_v2_full.sh

cd ~/oh_testing/
python check_vttx_optical_link.py
