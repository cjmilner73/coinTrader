import calendar
import time
from pymongo import MongoClient
from myConnection import getConn

polCon =  getConn()

currTime = time.strftime("%Y/%m/%d %H:%M:%S")

db = client.ticker_db

# Remove when happy
db.balances.remove({})

polBal = polCon.returnBalances()

print type(polBal)
print polBal

polTickers = polCon.returnTicker()
tickPairKeys = polTickers.keys()

btcBalUSD = polTickers['USDT_BTC']['last']

db.balances.remove()

def loadTotalAltInBTC():
    total = 0

    for balTicker, balValue  in polBal.iteritems():
        for tickerPair, price in polTickers.iteritems():
            btcKey = 'BTC_' + balTicker
            if tickerPair == btcKey:
                print balTicker
                print balValue
                print price['last']
                total = float(balValue) * float(price['last'])

                myBalance = {'tick': balTicker, 'balance': total}
                print myBalance
                db.balances.insert(myBalance)

def getTotalBTC():
    myBalance = {}
    for balTicker, balValue in polBal.iteritems():
        if balTicker == 'BTC':
            btcBalance = balValue
    return btcBalance

def getInvested():
    nowTimeEpoch = calendar.timegm(time.gmtime())
    polOrderHistory = polCon.returnTradeHistory('BTC_XRP',0,nowTimeEpoch)
    sellTotal = 0.0
    buyTotal = 0.0
    for i in polOrderHistory:
	print polOrderHistory
        if i['type'] == 'sell':
            sellTotal += float(i['total'])
        if i['type'] == 'buy':
            buyTotal += float(i['total'])
    print "Sold: %f" % sellTotal
    print "Bought: %f" % buyTotal



loadTotalAltInBTC()
getInvested()

