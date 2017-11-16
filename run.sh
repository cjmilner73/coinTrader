#!/bin/bash

fiveMinsInSecodns=300
fifteenMinsInSeconds=900
fourHoursInSecs=14400

noOfRuns=50
offset=50

runToEndOnDay=1509555600
period=$fifteenMinsInSeconds

python initDB.py

	for ((i=1;i<=noOfRuns;i++));
	do
    		curEndDate=$((runToEndOnDay - (fifteenMinsInSeconds * offset)))
    		offset=$((offset - 1))
    		echo 
    		echo 
    		echo 
    		echo "TEST RUN python coinTrader.py - End Date: $curEndDate with period of $fifteenMinsInSeconds TEST RUN"
    		echo "--------------------------------------------------------"
    		echo " 			TEST RUN NUMBER $i of $noOfRuns" 
    		echo 
    		python coinTrader.py $curEndDate $period
	done
	
	python recordDBProfit.py $period

