#!/bin/sh

cd /mnt/persistent/texas/oh_testing/
./program_full_fw.sh
python check_vttx_optical_link.py
