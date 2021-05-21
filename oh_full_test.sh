#!/bin/sh

RED='\033[0;31m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'
args=("$@")
argnum=("$#")
OH_TEST_LOGFILE="OHtestResults_"
OH_ID=''


function queryContinue()
{
FAIL_COUNT=$(grep -c FAIL ${OH_TEST_LOGFILE})
if [ "$FAIL_COUNT" -gt 0 ]
then
	echo -e "${RED}ERROR:${NC} ${PURPLE}${FAIL_COUNT}${NC} Failures have been observed"
	grep -i -n FAIL ${OH_TEST_LOGFILE}
	while true
	do
		echo "Do you wish to proceed with further Tets? (y/n):"
		read userIn
		if [ "$userIn" == "y" ] || [ "$userIn" == "Y" ]
		then
			echo "Yes selected"
			break
		elif [ $userIn == "n" ] || [ $userIn == "N" ]
		then
			echo "No selected Ending OH Testing"
			exit
		fi
	done
fi
}


if [ "$argnum" -lt 1 ]
then
	echo -e "${RED}ERROR:${NC} Enter an OH ID"
	exit
else
	OH_ID=$1
	OH_TEST_LOGFILE="${OH_TEST_LOGFILE}${OH_ID}.log"
	if test -f "${OH_TEST_LOGFILE}"
	then
		echo -e "${RED}ERROR:${NC} Log File ${CYAN}${OH_TEST_LOGFILE}${NC} Already Exists, please enter unique ID and Try again"
		exit
	else
		touch ${OH_TEST_LOGFILE}
		echo -e "Log file is created: ${CYAN}${OH_TEST_LOGFILE}${NC}"
	fi
fi

echo "Begin RiceOH2_testManual Section 8: Checking communication with CTP7"

./ohManual_sect_8.sh >> ${OH_TEST_LOGFILE}
queryContinue

echo "Begin RiceOH2_testManual Section 12: Testing of Load FPGA from GBT1"
./ohManual_sect_12.sh >> ${OH_TEST_LOGFILE}
queryContinue

echo "Begin RiceOH2_testManual Section 11.3: Testing of VTTX optical links with CTP7"                    
./ohManual_sect_11.sh >> ${OH_TEST_LOGFILE}                                                              
queryContinue 

echo "Begin RiceOH2_testManual Section 15: Integrated Test of VFAT Interface"        
./ohManual_sect_15.sh | tee -a ${OH_TEST_LOGFILE}                                    
queryContinue

echo "Begin RiceOH2_testManual Section 14: Integrated Test of Internal Links"
./ohManual_sect_14.sh >> ${OH_TEST_LOGFILE}
queryContinue
