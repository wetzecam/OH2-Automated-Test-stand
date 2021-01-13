#!/bin/sh

cd /mnt/persistent/texas/oh_testing/
./program_prbs_fw.sh

python eLink_PRBS_loopback_test.py
