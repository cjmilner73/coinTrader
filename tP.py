import datetime
import time
import calendar
import psycopg2
import myConnection
import dbMod
import broker


currHour = time.strftime("%Y/%m/%d %H")
currMin = time.strftime("%M")
nowTimeEpoch = calendar.timegm(time.gmtime())

#btcTickPairs = []
polCon = myConnection.getPolConn()
polBal = polCon.returnBalances()

BTCTOSPEND = 0.2
LIMIT_WEIGHT = float(0.05)
STOP_WEIGHT = float(0.05)
ACTIVE_TYPE = 'ADX_TRADE'

def getPrices():

    print "DEF: getPrices"
    global polTicker
    global tickPairKeys
    bal = broker.getBTCBalance()
    polTicker = polCon.returnTicker()
    tickPairKeys = polTicker.keys()

def checkStopLimit():
    
    actives = dbMod.getActives()

    for pairActive, activeType, utBought, direction, price, amount, stopPrice, limitPrice in actives:
        for key, value in polTicker.iteritems():
	    pairLatest = key 
	    lastPrice = value['last']
            lastPriceFloat = float(lastPrice)

            priceLimitFloat = float(limitPrice)
            priceStopFloat = float(stopPrice)

            if pairLatest == pairActive:
		if (direction == 'BUY'):
		    if lastPriceFloat >= priceLimitFloat:
			print "We've hit our BUY LIMIT of " + str(lastPriceFloat) + " as it's above our limit of " + str(priceLimitFloat) + " - cashing out"
                        profit = (lastPriceFloat - float(price)) * float(amount)
                        broker.sellPair(pairActive, lastPriceFloat, amount)                 
		        dbMod.insertHistory(pairActive, activeType, utBought, nowTimeEpoch, direction, price, lastPrice, amount, profit) 
		    if lastPriceFloat <= priceStopFloat:
			print "We've hit our BUY STOP of " + str(lastPriceFloat) + " as it's below our stop of " + str(priceLimitFloat) + " - exiting out"
                        profit = (lastPriceFloat - float(price)) * float(amount)
                        broker.sellPair(pairActive, lastPriceFloat, amount)                 
		        dbMod.insertHistory(pairActive, activeType, utBought, nowTimeEpoch, direction, price, lastPrice, amount, profit) 

		if (direction == 'SELL'):
		    if lastPriceFloat <= priceLimitFloat:
			print "We've hit our SELL LIMIT of " + str(lastPriceFloat) + " as it's below our limit of " + str(priceLimitFloat) + " - cashing out"
                        profit = (float(price) - lastPriceFloat) * float(amount)
                        broker.sellPair(pairActive, lastPriceFloat, amount)                 
		        dbMod.insertHistory(pairActive, activeType, utBought, nowTimeEpoch, direction, price, lastPrice, amount, profit) 
		    if lastPriceFloat >= priceStopFloat:
			print "We've hit our SELL STOP of " + str(lastPriceFloat) + " as it's above our stop of " + str(priceLimitFloat) + " - exiting out"
                        profit = (float(price) - lastPriceFloat) * float(amount)
                        broker.sellPair(pairActive, lastPriceFloat, amount)                 
		        dbMod.insertHistory(pairActive, activeType, utBought, nowTimeEpoch, direction, price, lastPrice, amount, profit) 
                
 
def checkSellTriggers():

    DIRECTION = 'SELL'

    triggers = dbMod.getSellTriggers()

    triggerFloor = 0

    for pairTrigger, priceTrigger, direction, lowPrice, highPrice in triggers:
	for key, value in polTicker.iteritems():
	    pairLatest = key 
	    lastPrice = value['last']
            lastPriceFloat = float(lastPrice)
            priceTriggerFloat = float(priceTrigger)
            if pairLatest == pairTrigger:
		if lastPriceFloat <= priceTriggerFloat and lastPriceFloat > triggerFloor:
      		    btcToSpend = BTCTOSPEND
    	            totalBTC = getBTCBalance()
                    myTickPrices = polCon.returnTicker()
                    coinPriceTick = myTickPrices[pairLatest]
                    coinPrice = coinPriceTick['last']
                    priceFloat = float(coinPrice)
                    noOfCoinsToSell = round(btcToSpend / priceFloat)

                    priceTriggerFloat = float(priceTrigger)
                    lowPriceFloat = float(lowPrice)
                    highPriceFloat = float(highPrice)
	            limit = lowPriceFloat - (LIMIT_WEIGHT * priceTriggerFloat)
		    stop = highPriceFloat + (STOP_WEIGHT * priceTriggerFloat)

    		    if ( noOfCoinsToSell * priceFloat < totalBTC ):
                        print "Sell %d of %s at %s" % (noOfCoinsToSell, pairLatest, priceFloat)
                        broker.sellPair(pairTrigger, priceTrigger, noOfCoinsToSell)
		        dbMod.insertActive(pairTrigger, ACTIVE_TYPE, nowTimeEpoch, DIRECTION, lastPrice, noOfCoinsToSell, stop, limit)
    		    else:
         		print "Not enough BTC, need " + str(noOfCoinsToSell*priceFloat) + " only have " + str(totalBTC)


def checkBuyTriggers():

    print "DEF: checkBuyTrigger"
    DIRECTION = 'BUY';
    triggers = dbMod.getBuyTriggers()
    print triggers
    triggerCeiling = 100

    for pairTrigger, priceTrigger, direction, lowPrice, highPrice in triggers:
        print "Trigger price from db: " + str(priceTrigger)
	for key, value in polTicker.iteritems():
            print "Iter through Ticker list"
	    pairLatest = key 
	    lastPrice = value['last']
            lastPriceFloat = float(lastPrice)
            priceTriggerFloat = float(priceTrigger)
            if pairLatest == pairTrigger:
                print "Checking trigger..."
		if lastPriceFloat >= priceTriggerFloat and lastPriceFloat < triggerCeiling:
      		    btcToSpend = BTCTOSPEND
    	            totalBTC = getBTCBalance()
                    myTickPrices = polCon.returnTicker()
                    coinPriceTick = myTickPrices[pairLatest]
                    coinPrice = coinPriceTick['last']
                    priceFloat = float(coinPrice)
                    noOfCoinsToBuy = round(btcToSpend / priceFloat)
                    priceTriggerFloat = float(priceTrigger)
                    lowPriceFloat = float(lowPrice)
                    highPriceFloat = float(highPrice)

		    stop = lowPriceFloat - (STOP_WEIGHT * priceTriggerFloat)
		    limit = highPriceFloat + (LIMIT_WEIGHT * priceTriggerFloat)

    		    if ( noOfCoinsToBuy * priceFloat < totalBTC ):
                        print "Buy %d of %s at %s" % (noOfCoinsToBuy, pairLatest, priceFloat)
                        broker.buyPair(pairTrigger, priceTrigger, noOfCoinsToBuy)
		        dbMod.insertActive(pairTrigger, ACTIVE_TYPE, nowTimeEpoch, DIRECTION, lastPrice, noOfCoinsToBuy, stop, limit)
    		    else:
         		print "Not enough BTC, need " + str(noOfCoinsToBuy*priceFloat) + " only have " + str(totalBTC)

def getBTCBalance():
    myBalance = {}
    for balTicker, balValue in polBal.iteritems():
        if balTicker == 'BTC':
            btcBalance = balValue
    return btcBalance

getPrices()
checkBuyTriggers()
checkSellTriggers()
checkStopLimit()

