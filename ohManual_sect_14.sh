#!/bin/sh

./program_prbs_fw.sh

python fpga_phase_scan.py

python eLink_PRBS_loopback_test.py
