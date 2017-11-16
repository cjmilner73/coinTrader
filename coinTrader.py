import datetime
import time
import calendar
import psycopg2
import myConnection
import dbMod
from adx import ADX
import spikeCheck
import broker
import sys
import time
import balances

#endTimeVar=sys.argv[1]
#endTimeEpoch=int(endTimeVar)
#tickPeriodVar=sys.argv[2]
#tickPeriod=int(tickPeriodVar)

BTCTOSPEND = .5
LIMIT_WEIGHT = float(0.05)
STOP_WEIGHT = float(0.05)
ACTIVE_TYPE = 'ADX_TRADE'

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

#tickPeriod = fifteenMinsInSeconds
tickPeriod = fiveMinsInSeconds
#tickPeriod = fourHoursInSeconds
#tickPeriod = oneDayInSeconds
if tickPeriod == fiveMinsInSeconds:
    secondsToSubtract = oneDayInSeconds / 6
elif tickPeriod == fifteenMinsInSeconds:
    secondsToSubtract = oneDayInSeconds / 2
elif tickPeriod == fourHoursInSeconds:
    secondsToSubstract = oneDayInSeconds * 3

print "secondsToSubtract: (periods) " + str(secondsToSubtract)
print
print "Num of periods to download is: " + str(secondsToSubtract/tickPeriod)
print

#startEpoch = weekInSeconds
#startEpoch = weekInSeconds*4

btcTickPairs = []

# Modify the these for testing
#endTimeEpoch = 1508853020
#endTimeEpoch = 1509254100
endTimeEpoch = nowTimeEpoch
#endTimeEpoch = endTimeEpoch + (fourHoursInSeconds * 7)

startTimeEpoch = int(endTimeEpoch) - secondsToSubtract


def downloadPrices():
    logTime = datetime.datetime.now()
    print "DEF: downloadPrices: " + str(logTime)
    print
    print "From Date: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTimeEpoch))
    print "To Date: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(endTimeEpoch))
    print
    print "Tick Period: " + str(tickPeriod)
    print
    global btcTickPairs
    global polTicker


    polTicker = polCon.returnTicker()

    tickPairKeys = polTicker.keys()

    for tickPair in tickPairKeys:
        if tickPair.startswith("BTC"):
            btcTickPairs.append(tickPair)

    #btcTickPairs = ['BTC_VTC']

    dbMod.deleteOHLCV()

    logTime = datetime.datetime.now()
    print "DEF: downloadPrices - 1: " + str(logTime)
    print

    epochUT = 0
    for keyPair in btcTickPairs:
        polChart = polCon.returnChartData(keyPair, tickPeriod, startTimeEpoch, endTimeEpoch)
        if 'candleStick' in polChart:
            statements=[]
            start = time.time()
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
                statements.append(myRow) 
                #dbMod.insertOHLCV(myRow)
            dbMod.insertStatementsOHLCV(statements)
            end = time.time()
            #print "Downloaded prices for: " + keyPair + " in " + str(end-start)
	else:
	    print polChart
        lastDateUT = epochUT


    logTime = datetime.datetime.now()
    print "END: downloadPrices - 1: " + str(logTime)
    print


def calcADX():
    logTime = datetime.datetime.now()
    print "DEF: calcADX: " + str(logTime)
    print

    for keyPair in btcTickPairs:
        myTuple = ADX(keyPair)
        if myTuple is not None:
            pair = myTuple[0]
            adx = myTuple[1]
            direction = myTuple[2]
            lastTime = myTuple[3]
            startPrice = myTuple[4]
            #print
            #print pair + "...Found Potential, ADX: " + str(adx) + " direction: " + str(direction) + " lastTime: " + str(lastTime) + " startPrice: " + str(startPrice)
            existingPotOrAct = dbMod.getExisting()
            rows = [x[0] for x in existingPotOrAct]
            if keyPair not in rows:
                dbMod.insertPotential(myTuple)

def removeExpiredPotentials():
    logTime = datetime.datetime.now()
    print "DEF: removeExpiredPotentialss: " + str(logTime)
    print

    potentials = dbMod.getPotentials()

    for pot in potentials:
        thisPotPair = pot[0]
        thisStartDate = pot[3]
   	thisHot = pot[7]
        periodsActive = (endTimeEpoch - thisStartDate) / tickPeriod
        #print "Periods active: " + str(periodsActive)

        if (thisHot == True):
             activeLimit = 11
             #print "ACtivelimit set to: " + str(activeLimit)
        else:
             activeLimit = 7
        #print periodsActive
        #print activeLimit
        if (periodsActive >= activeLimit):
            print
            print thisPotPair + " has been active " + str(periodsActive) + " periods...DELETING"
            print
            #print "Deleting potential..."
            dbMod.deletePotential(thisPotPair)
                
def checkPotentials():
    logTime = datetime.datetime.now()
    print "DEF: checkPotentials: " + str(logTime)
    print
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
            direction = pot[4]
            ohlcvRows = dbMod.getOHLCV(thisPotPair, thisStartDate)
            if direction == 'BUY':
	        checkForDip(ohlcvRows)
	    else:
 		checkForRise(ohlcvRows)

def checkForRise(ohlcvRows):

        module = "checkForRise"
	counter = 0
	streak = 0
        #print "Len of ohlcvRows is " + str(len(ohlcvRows))
        #print ohlcvRows
	if len(ohlcvRows) >= 3:
                lowPeriodClosePrice = ohlcvRows[0][5]
                #print ohlcvRows[0][0] + " lowPeridClosePeriod initial value: " + str(lowPeriodClosePrice)
		numberOfPeriods = len(ohlcvRows)
                #print "numberOfPeriods = " + str(numberOfPeriods)
		#currentLow = ohlcvRows[0][5]
		currentHigh = 0
		#print "currentHigh = " + str(currentHigh)
		for row in ohlcvRows:
			pairName = row[0]
			if counter < numberOfPeriods-1:
				periodClose = ohlcvRows[counter][5]
				followingPeriod = ohlcvRows[counter+1][5]	
                                periodTimestamp = ohlcvRows[counter+1][1]
                                #print "Close: " + str(periodClose)
				#print "Next Close: " + str(followingPeriod)

                                #if followingPeriod < highPeriodClosePrice:
                                if followingPeriod < periodClose and followingPeriod < lowPeriodClosePrice:
				    lowPeriodClosePrice = followingPeriod
                                    #print "Setting new lowPeriodClosePeriod: " + str(lowPeriodClosePrice)
				    if currentHigh == 0:
					currentHigh = lowPeriodClosePrice

				if followingPeriod > currentHigh:
                                        currentHigh = followingPeriod
					streak += 1
 					#print "Dip! + " + str(streak) + " at followingPeriod price " + str(followingPeriod)
                                        #print
                                        #dips.append(followingPeriod)
					if streak == 3:
                                                print module + ": We've 3 in a rise for " + pairName
						riseStartTime = ohlcvRows[0][1]
						#highPeriodClosePrice = ohlcvRows[0][5]
						#lowPeriodClosePrice = ohlcvRows[counter+1][5]
						highPeriodClosePrice = ohlcvRows[counter+1][5]
						print module + ": Rise Start Time: " + str(riseStartTime)
						print module + ": Low price: " + str(lowPeriodClosePrice)
						print module + ": High price:" + str(highPeriodClosePrice)
						trigger = highPeriodClosePrice - (highPeriodClosePrice - lowPeriodClosePrice)/2
						#print "Trigger: " + str(trigger)
						hot = True
						dbMod.setHotsetTrigger(pairName, hot, trigger, lowPeriodClosePrice, highPeriodClosePrice)
                                                #print
                                                print module + "Set trigger for " + pairName + " at value " + str(trigger) + " at time " + str(periodTimestamp)
				counter += 1

def checkForDip(ohlcvRows):
        logTime = datetime.datetime.now()
        print "DEF: CheckForDip: " + str(logTime)
        print
	counter = 0
	streak = 0
        #print "Len of ohlcvRows is " + str(len(ohlcvRows))
        #print ohlcvRows
	if len(ohlcvRows) >= 3:
                highPeriodClosePrice = ohlcvRows[0][5]
		numberOfPeriods = len(ohlcvRows)
                #print "numberOfPeriods = " + str(numberOfPeriods)
		#currentLow = ohlcvRows[0][5]
		currentLow = 99999
		#print "currentLow = " + str(currentLow)
                dips = []
		for row in ohlcvRows:
			pairName = row[0]
			if counter < numberOfPeriods-1:
				periodClose = ohlcvRows[counter][5]
				followingPeriod = ohlcvRows[counter+1][5]	
                                periodTimestamp = ohlcvRows[counter+1][1]
                                #print "Close: " + str(periodClose)
				#print "Next Close: " + str(followingPeriod)
				# Adding check for new highs before a dip

                                if followingPeriod > highPeriodClosePrice and followingPeriod > highPeriodClosePrice:
				    highPeriodClosePrice = followingPeriod
				    if currentLow == 99999:
					currentLow = highPeriodClosePrice
                                        #print "Readjusting currentLow: " + str(currentLow) + " for " + pairName

				if followingPeriod < currentLow:
                                        currentLow = followingPeriod
					streak += 1
 					#print "Dip! + " + str(streak) + " at followingPeriod price " + str(followingPeriod)
                                        #print
                                        dips.append(followingPeriod)
					if streak == 3:
						#print "We've 3 in a dip"
						dipStartTime = ohlcvRows[0][1]
                                                #print dips
                                                #print
						#highPeriodClosePrice = ohlcvRows[0][5]
						#lowPeriodClosePrice = ohlcvRows[counter+1][5]
						lowPeriodClosePrice = ohlcvRows[counter+1][5]
						#print "Dip Start Time: " + str(dipStartTime)
						#print "High price: " + str(highPeriodClosePrice)
						#print "Low price:" + str(lowPeriodClosePrice)
						trigger = lowPeriodClosePrice + (highPeriodClosePrice - lowPeriodClosePrice)/2
						#print "Trigger: " + str(trigger)
						hot = True
						dbMod.setHotsetTrigger(pairName, hot, trigger, lowPeriodClosePrice, highPeriodClosePrice)
                                                #print
                                                #print "Set trigger for " + pairName + " at value " + str(trigger) + " at time " + str(periodTimestamp)
				counter += 1



def spikeChk():
    logTime = datetime.datetime.now()
    print "DEF: spikeChk: " + str(logTime)
    print
    spikeCheck.checkEachTick()


def getPrices():
    logTime = datetime.datetime.now()
    print "DEF: getPrices: " + str(logTime)
    print
    #global polTicker
    #global tickPairKeys
    bal = broker.getBTCbalance()
    #polTicker = polCon.returnTicker()

def checkStopLimit():
    
    print "DEF: checkStopLimit"
    print
    module = "checkForStopLimit"

    logTime = datetime.datetime.now()
    print
    actives = dbMod.getActives()

    for pairActive, activeType, utBought, direction, startPrice, amount, stopPrice, limitPrice in actives:
        for key, value in polTicker.iteritems():
	    pairLatest = key 
	    lastPrice = value['last']
            lastPriceFloat = float(lastPrice)
            priceLimitFloat = float(limitPrice)
            priceStopFloat = float(stopPrice)

            if pairLatest == pairActive:
                #print pairActive + " is a " + direction + " , startPrice= " + str(startPrice) + ", lastPrice= " + str(lastPriceFloat) + ", priceLimitFloat= " + str(priceLimitFloat) + ", priceLimitStop= " + str(priceStopFloat)
		if (direction == 'BUY'):
		    if lastPriceFloat >= priceLimitFloat:
                        profit = (lastPriceFloat - float(startPrice)) * float(amount)
			print pairActive + "...We've hit our BUY LIMIT of " + str(lastPriceFloat) + " as it's above our limit of " + str(priceLimitFloat) + " - cashing out, profit = " + str(profit) + ", startPrice= " + str(startPrice)
                        broker.sellPair(pairActive, lastPriceFloat, amount)                 
		        dbMod.insertHistory(pairActive, activeType, utBought, nowTimeEpoch, direction, startPrice, lastPrice, amount, profit) 
		    if lastPriceFloat <= priceStopFloat:
                        profit = (lastPriceFloat - float(startPrice)) * float(amount)
			print pairActive + "...We've hit our BUY STOP of " + str(lastPriceFloat) + " as it's below our stop of " + str(priceLimitFloat) + " - exiting out, profit = " + str(profit) + ", startPrice= " + str(startPrice)
                        broker.sellPair(pairActive, lastPriceFloat, amount)                 
		        dbMod.insertHistory(pairActive, activeType, utBought, nowTimeEpoch, direction, startPrice, lastPrice, amount, profit) 

		if (direction == 'SELL'):
		    if lastPriceFloat <= priceLimitFloat:
                        profit = (float(startPrice) - lastPriceFloat) * float(amount)
                        #print utBought
			print module + ": " + pairActive + "...We've hit our SELL LIMIT of " + str(lastPriceFloat) + " as it's below our limit of " + str(priceLimitFloat) + " - cashing out, profit = " + str(profit) + ", startPrice= " + str(startPrice)
                        broker.sellPair(pairActive, lastPriceFloat, amount)                 
		        dbMod.insertHistory(pairActive, activeType, utBought, nowTimeEpoch, direction, startPrice, lastPrice, amount, profit) 
		    if lastPriceFloat >= priceStopFloat:
                        profit = (float(startPrice) - lastPriceFloat) * float(amount)
			print module + ": " + pairActive + "...We've hit our SELL STOP of " + str(lastPriceFloat) + " as it's above our stop of " + str(priceLimitFloat) + " - exiting out, profit = " + str(profit) + ", startPrice= " + str(startPrice)
                        broker.sellPair(pairActive, lastPriceFloat, amount)                 
		        dbMod.insertHistory(pairActive, activeType, utBought, nowTimeEpoch, direction, startPrice, lastPrice, amount, profit) 
                
 
def checkSellTriggers():
    module = "checkSellTriggers"
    logTime = datetime.datetime.now()
    print "DEF: checkSellTriggers: " + str(logTime)
    print
    DIRECTION = 'SELL'

    triggers = dbMod.getSellTriggers()
    startTime = nowTimeEpoch;

    triggerFloor = 0

    for pairTrigger, priceTrigger, direction, lowPrice, highPrice in triggers:
	for key, value in polTicker.iteritems():
	    pairLatest = key 
	    lastPrice = value['last']
            lastPriceFloat = float(lastPrice)
            priceTriggerFloat = float(priceTrigger)
            if pairLatest == pairTrigger:
                priceTriggerFloat = float(priceTrigger)
                startTimeInt = int(startTime)
                lowPriceFloat = float(lowPrice)
                highPriceFloat = float(highPrice)
	        limit = lowPriceFloat - (LIMIT_WEIGHT * lastPriceFloat)
		stop = highPriceFloat + (STOP_WEIGHT * lastPriceFloat)
      		btcToSpend = BTCTOSPEND
                coin = pairLatest.split("BTC_",1)[1] 
    	        totalCoin = getCoinBalance(coin)
                noOfCoinsToSell = round(btcToSpend / lastPriceFloat)
                if lastPriceFloat < limit:
                    limit = lastPriceFloat - (LIMIT_WEIGHT * lastPriceFloat)
                    print "Setting new sell limit for " + pairTrigger + " at price " + str(limit)
		if lastPriceFloat <= priceTriggerFloat and lastPriceFloat > triggerFloor:
		#if lastPriceFloat <= priceTriggerFloat and lastPriceFloat > limit:
    		    if ( noOfCoinsToSell * lastPriceFloat <= totalCoin ):
    		    #if ( True ):
                        print module + ": Sell %d of %s at %s" % (noOfCoinsToSell, pairLatest, lastPriceFloat)
                        print module + "SELL PRICE OF : " + str(lastPriceFloat) + " should not be LIMIT: " + str(limit)
                        broker.sellPair(pairTrigger, priceTrigger, noOfCoinsToSell)
		        #dbMod.insertActive(pairTrigger, ACTIVE_TYPE, nowTimeEpoch, DIRECTION, priceTrigger, noOfCoinsToSell, stop, limit)
		        dbMod.insertActive(pairTrigger, ACTIVE_TYPE, startTimeInt, DIRECTION, lastPrice, noOfCoinsToSell, stop, limit)
    		    else:
         		print module + ": Not enough BTC, need " + str(noOfCoinsToSell*lastPriceFloat) + " only have " + str(totalCoin)


def checkBuyTriggers():

    logTime = datetime.datetime.now()
    print "DEF: checkBuyTrigger: " + str(logTime)
    print
    DIRECTION = 'BUY';
    triggers = dbMod.getBuyTriggers()
    startTime = nowTimeEpoch;

    triggerCeiling = 999999

    for pairTrigger, priceTrigger, direction, lowPrice, highPrice in triggers:
        #print "Trigger price from db: " + str(priceTrigger)
	for key, value in polTicker.iteritems():
	    pairLatest = key 
	    lastPrice = value['last']
            lastPriceFloat = float(lastPrice)
            startTimeInt = int(startTime)
            priceTriggerFloat = float(priceTrigger)
            if pairLatest == pairTrigger:
                #print "Checking trigger...lastPrice: " + str(lastPriceFloat) + " and trigger: " + str(priceTriggerFloat)
		#if lastPriceFloat >= priceTriggerFloat and lastPriceFloat < triggerCeiling:
                priceTriggerFloat = float(priceTrigger)
                lowPriceFloat = float(lowPrice)
                highPriceFloat = float(highPrice)
		stop = lowPriceFloat - (STOP_WEIGHT * lastPriceFloat)
		limit = highPriceFloat + (LIMIT_WEIGHT * lastPriceFloat)
      		btcToSpend = BTCTOSPEND
                coin = 'BTC'
    	        totalCoin = getCoinBalance(coin)
                noOfCoinsToBuy = round(btcToSpend / lastPriceFloat)
                if lastPriceFloat > limit:
                    limit = lastPriceFloat + (LIMIT_WEIGHT * lastPriceFloat)
                    print "Setting new buy limit for " + pairTrigger + " at price " + str(limit)
		#if lastPriceFloat >= priceTriggerFloat and lastPriceFloat < triggerCeiling:
		if lastPriceFloat >= priceTriggerFloat and lastPriceFloat < limit:

    		    if ( noOfCoinsToBuy * lastPriceFloat <= totalCoin ):
    		    #if ( True ):
                        #print "Buy %d of %s at %s" % (noOfCoinsToBuy, pairLatest, priceFloat)
                        print "Buy %d of %s at %s" % (noOfCoinsToBuy, pairLatest, lastPriceFloat)
                        broker.buyPair(pairTrigger, lastPriceFloat, noOfCoinsToBuy)
		        dbMod.insertActive(pairTrigger, ACTIVE_TYPE, startTimeInt, DIRECTION, lastPriceFloat, noOfCoinsToBuy, stop, limit)
    		    else:
         		print "Not enough BTC, need " + str(noOfCoinsToBuy*priceFloat) + " only have " + str(totalCoin)

def getCoinBalance(coin):
    coinBalance = dbMod.getCoinBalance(coin)
    coinBalanceFloat = coinBalance[0][0]
    print "Returning coinBalance: " + str(coin) + " as " + str(coinBalanceFloat)
    return coinBalanceFloat

def loadBalances():
    a = balances.loadPolBalances()

print "==============================================================="
print "Starting new run of coinTrader: " + str(datetime.datetime.now())
print "==============================================================="
print
polCon = myConnection.getPolConn()
polBal = polCon.returnBalances()

loadBalances()
downloadPrices()
removeExpiredPotentials()
calcADX()
checkPotentials()
spikeChk()
checkBuyTriggers()
#checkSellTriggers()
checkStopLimit()
print "========================="
print "End Time: " + str(datetime.datetime.now())
print "========================="
print 
