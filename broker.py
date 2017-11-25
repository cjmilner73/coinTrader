import datetime
import time
import calendar
import psycopg2
import myConnection
import dbMod
import sendSMS

BTCTOSPEND = 0.2
polCon = myConnection.getPolConn()
polBal = polCon.returnBalances()

currHour = time.strftime("%Y/%m/%d %H")
currMin = time.strftime("%M")
nowTimeEpoch = calendar.timegm(time.gmtime())

def getBTCBalance():
    myBalance = {}
    btcBalance = -1
    for balTicker, balValue in polBal.iteritems():
        if balTicker == 'BTC':
            btcBalance = balValue
    return btcBalance

def buyPair(pair, price, amount):
    print "DEF: buyPair"
    print
    print "Buying " + str(amount) + " of " + pair + " at " + str(price)
    #sendSMS.sendMessage("Buying " + str(amount) + " of " + pair + " at " + str(price))
    orderNo = polCon.buy(pair,price,amount)
    print orderNo
    openOrders = polCon.returnOpenOrders(pair)
    print "Order placed..."
    print openOrders

def buyPairSpike(pair):
    btcToSpend = BTCTOSPEND
    totalBTC = getBTCBalance()
    print "Total BTC: " + str(totalBTC)
    myTickPrices = polCon.returnTicker()
    coinPriceTick = myTickPrices[pair]
    coinPrice = coinPriceTick['last']
    priceFloat = float(coinPrice)
    print "coinPrice: " + str(priceFloat)
    noOfCoinsToBuy = round(btcToSpend / priceFloat)
    print "noOfCoindsToBuy: " + str(noOfCoinsToBuy)
    print "Cost in BTC to buy is : " + str(noOfCoinsToBuy*priceFloat)
    if ( (noOfCoinsToBuy * priceFloat) < totalBTC ):
    #if ( True ):
        print "Buy %d of %s at %s" % (noOfCoinsToBuy, pair, priceFloat)
        #polCon.buy(pair, priceFloat, noOfCoinsToBuy)
        sendSMS.sendMessage("Buying " + str(noOfCoinsToBuy) + " of " + pair + " at " + str(priceFloat))
        stop = priceFloat * 0.7
        limit = priceFloat * 1.3
        dbMod.insertActive(pair, 'SPIKE', nowTimeEpoch, 'BUY', priceFloat, noOfCoinsToBuy, stop, limit)
    else:
        print "Not enough BTC, need " + str(noOfCoinsToBuy*priceFloat) + " only have " + str(totalBTC)

def sellPair(pair, price, amount):
    print "DEF: sellPair"
    print
    print "Selling " + str(amount) + " of " + pair + " at " + str(price)
    #sendSMS.sendMessage("Selling " + str(amount) + " of " + pair + " at " + str(price))
    orderNo = polCon.sell(pair,price,amount)
    print orderNo
    openOrders = polCon.returnOpenOrders(pair)
    print "Order placed..."
    print openOrders
