import datetime
import time
import calendar
import psycopg2
from myConnection import getConn
import dbMod
from adx import ADX
import spikeCheck
import sys
endTimeEpoch = 1507291200

currHour = time.strftime("%Y/%m/%d %H")
currMin = time.strftime("%M")
nowTimeEpoch = calendar.timegm(time.gmtime())

weekInSeconds = 604800
monthInSeconds = 2592000
twoMonthsInSeconds = 2592000*2
threeMonthsInSeconds = 2592000*3
fourHoursInSeconds = 14400
oneDayInSeconds = 86400
fiveMinsInSeconds = 300
fifteenMinsInSeconds = 900

tickPeriod = fifteenMinsInSeconds
#tickPeriod = fiveMinsInSeconds
#tickPeriod = fourHoursInSeconds
#tickPeriod = oneDayInSeconds
startEpoch = oneDayInSeconds * 2
#startEpoch = weekInSeconds
#startEpoch = weekInSeconds*4

btcTickPairs = []

# Modify the these for testing
#endTimeEpoch = 1507291200
#endTimeEpoch = 1507708800
#endTimeEpoch = nowTimeEpoch
#endTimeEpoch = endTimeEpoch + (fourHoursInSeconds * 7)

startTimeEpoch = endTimeEpoch - startEpoch

def downloadPrices():
    global btcTickPairs

    polCon = getConn()
    #startEpoch = weekInSeconds*2
    #startEpoch = oneDayInSeconds
    #tickPeriod = oneDayInSeconds
    #tickPeriod = fiveMinsInSeconds


    print "endTimeEpoch: " + str(endTimeEpoch)
    print "From Date: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTimeEpoch))
    print "To Date: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endTimeEpoch))
    print

    polTicker = polCon.returnTicker()

    tickPairKeys = polTicker.keys()

    for tickPair in tickPairKeys:
        if tickPair.startswith("BTC"):
            btcTickPairs.append(tickPair)

    #btcTickPairs = ['BTC_VTC']
    print "Start Time: " + str(datetime.datetime.now())
    print

    dbMod.deleteOHLCV()

    epochUT = 0
    for keyPair in btcTickPairs:
        polChart = polCon.returnChartData(keyPair, tickPeriod, startTimeEpoch, endTimeEpoch)
        #print polChart
        if 'candleStick' in polChart:
            for tickSticks in polChart['candleStick']:
                epochUT = tickSticks['date']
                openP = tickSticks['open']
                highP = tickSticks['high']
                lowP = tickSticks['low']
                closeP = tickSticks['close']
                volumeP = tickSticks['volume']
                #f = open('sampleData2', 'a')
                #myLine = keyPair + "," + str(volumeP) + ", " + str(epochUT) + "," + str(closeP) + "," + str(lowP) + "," + str(highP) + "," + str(openP)
                myLine = keyPair + ":" + str(epochUT) + "," + str(closeP) + "," + str(highP) + "," + str(lowP) + "," + str(openP) + "," + str(volumeP)
                #f.write(myLine + "\n")
                myRow = [keyPair,epochUT,openP,highP,lowP,closeP,volumeP]
                dbMod.insertOHLCV(myRow)
	else:
	    print polChart

        lastDateUT = epochUT


def calcADX():
    print "DEF: identPotentials"

    for keyPair in btcTickPairs:
        myTuple = ADX(keyPair)
        if myTuple is not None:
            pair = myTuple[0]
            adx = myTuple[1]
            upTrend = myTuple[2]
            lastTime = myTuple[3]
            startPrice = myTuple[4]
            print pair + " ADX: " + str(adx) + " upTrend: " + str(upTrend) + " lastTime: " + str(lastTime) + " startPrice: " + str(startPrice)
            print
            dbMod.insertPotential(myTuple)

def removeExpiredPotentials():
    print "DEF: removeExpiredPotentials"

    potentials = dbMod.getPotentials()

    for pot in potentials:
        thisPotPair = pot[0]
        thisStartDate = pot[3]
   	thisHot = pot[7]
        periodsActive = (endTimeEpoch - thisStartDate) / tickPeriod
        print "Periods active: " + str(periodsActive)

        if (thisHot == True):
             activeLimit = 11
             print "ACtivelimit set to: " + str(activeLimit)
        else:
             activeLimit = 7
        print thisHot
        print periodsActive
        print activeLimit
        if (periodsActive >= activeLimit):
            print thisPotPair + " has been active " + str(periodsActive) + " periods."
            print "Deleting potential..."
            dbMod.deletePotential(thisPotPair)
                
def checkPotentials():
    print "DEF: checkPotentials"
    # Check for 3 dips in 5 periods
    # If yes, set trigger, stop and limit (trigger should be in correct range limits)
        # Get all close prices for potential period
    # Need table for ACTIVE, pair, ut_bought, price_bought, amount_btc, stop, limit

    potentials = dbMod.getPotentials()

    for pot in potentials:
        thisHot = pot[7]
        if thisHot == False: 
            thisPotPair = pot[0]
            thisStartDate =  pot[3]
            ohlcvRows = dbMod.getOHLCV(thisPotPair, thisStartDate)
            if pot[4] == 'True':
	        checkForDip(ohlcvRows)
	    else:
 		checkForRise(ohlcvRows)

def checkForRise(ohlcvRows):

	counter = 0
	streak = 0
        print "Len of ohlcvRows is " + str(len(ohlcvRows))
        print ohlcvRows
	if len(ohlcvRows) >= 3:
                lowPeriodClosePrice = ohlcvRows[0][5]
		numberOfPeriods = len(ohlcvRows)
                print "numberOfPeriods = " + str(numberOfPeriods)
		#currentLow = ohlcvRows[0][5]
		currentHigh = 0
		print "currentHigh = " + str(currentHigh)

		for row in ohlcvRows:
			pairName = row[0]
			if counter < numberOfPeriods-1:
				periodClose = ohlcvRows[counter][5]
				followingPeriod = ohlcvRows[counter+1][5]	
                                print "Close: " + str(periodClose)
				print "Next Close: " + str(followingPeriod)
				# Adding check for new highs before a dip

                                #if followingPeriod < highPeriodClosePrice:
                                if followingPeriod < periodClose:
				    lowPeriodClosePrice = followingPeriod
				    if currentHigh == 0:
					currentHigh = lowPeriodClosePrice

				if followingPeriod > currentHigh:
                                        currentHigh = followingPeriod
					streak += 1
 					print "Rise! + " + str(streak)
					if streak == 3:
						print "We've 3 in a rise"
						dipStartTime = ohlcvRows[0][1]
						#highPeriodClosePrice = ohlcvRows[0][5]
						#lowPeriodClosePrice = ohlcvRows[counter+1][5]
						highPeriodClosePrice = ohlcvRows[counter+1][5]
						print "Rise Start Time: " + str(dipStartTime)
						print "Low price: " + str(lowPeriodClosePrice)
						print "High price:" + str(highPeriodClosePrice)
						trigger = highPeriodClosePrice - (highPeriodClosePrice - lowPeriodClosePrice)/2
						print "Trigger: " + str(trigger)
						hot = True
						dbMod.setHotsetTrigger(pairName, hot, trigger, lowPeriodClosePrice, highPeriodClosePrice)
				counter += 1

def checkForDip(ohlcvRows):
	counter = 0
	streak = 0
        print "Len of ohlcvRows is " + str(len(ohlcvRows))
        print ohlcvRows
	if len(ohlcvRows) >= 3:
                highPeriodClosePrice = ohlcvRows[0][5]
		numberOfPeriods = len(ohlcvRows)
                print "numberOfPeriods = " + str(numberOfPeriods)
		#currentLow = ohlcvRows[0][5]
		currentLow = 99999
		print "currentLow = " + str(currentLow)

		for row in ohlcvRows:
			pairName = row[0]
			if counter < numberOfPeriods-1:
				periodClose = ohlcvRows[counter][5]
				followingPeriod = ohlcvRows[counter+1][5]	
                                print "Close: " + str(periodClose)
				print "Next Close: " + str(followingPeriod)
				# Adding check for new highs before a dip

                                if followingPeriod > highPeriodClosePrice:
				    highPeriodClosePrice = followingPeriod
				    if currentLow == 99999:
					currentLow = highPeriodClosePrice

				if followingPeriod < currentLow:
                                        currentLow = followingPeriod
					streak += 1
 					print "Dip! + " + str(streak)
					if streak == 3:
						print "We've 3 in a dip"
						dipStartTime = ohlcvRows[0][1]
						#highPeriodClosePrice = ohlcvRows[0][5]
						#lowPeriodClosePrice = ohlcvRows[counter+1][5]
						lowPeriodClosePrice = ohlcvRows[counter+1][5]
						print "Dip Start Time: " + str(dipStartTime)
						print "High price: " + str(highPeriodClosePrice)
						print "Low price:" + str(lowPeriodClosePrice)
						trigger = lowPeriodClosePrice + (highPeriodClosePrice - lowPeriodClosePrice)/2
						print "Trigger: " + str(trigger)
						hot = True
						dbMod.setHotsetTrigger(pairName, hot, trigger, lowPeriodClosePrice, highPeriodClosePrice)
				counter += 1



def spikeChk():
    spikeCheck.checkEachTick()

downloadPrices()
removeExpiredPotentials()
calcADX()
checkPotentials()
spikeChk()

print
print "End Time: " + str(datetime.datetime.now())
