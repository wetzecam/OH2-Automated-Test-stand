#!/bin/sh

RED='\033[0;31m'
NC='\033[0m'
args=("$@")
argnum=("$#")
OH_TEST_LOGFILE="OHtestResults_"
OH_ID=''

export

if [ "$argnum" -lt 1 ]
then
	echo "ERROR: Enter an OH ID"
else
	OH_ID=$1
	OH_TEST_LOGFILE="${OH_TEST_LOGFILE}${OH_ID}.log"
	if test -f "${OH_TEST_LOGFILE}"
	then
		echo -e "${RED}ERROR:${NC} Log file ${OH_TEST_LOGFILE} Already Exists"
				
		while true
		do
			echo "Do you wish to continue? (y/n):"
			read userIn
			if [ "$userIn" == "y" ] || [ "$userIn" == "Y" ]
			then 
				echo "Yes selected"
				
			elif [ $userIn == "n" ] || [ $userIn == "N" ]
			then
				echo "No selected"
				break
			fi
		done

	else
		touch ${OH_TEST_LOGFILE}
		echo "Log file is created: ${OH_TEST_LOGFILE}"
	fi
fi
