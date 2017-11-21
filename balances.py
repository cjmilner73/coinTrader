import myConnection
from decimal import Decimal
import dbMod
import datetime
import time

bittConn = myConnection.getBittConn()
polConn = myConnection.getPolConn()
bitfConnTrade = myConnection.getBitfConnTrade()
bitfConnClient = myConnection.getBitfConnClient()

nowTime = time.time()    

wallets = {'BTC':63,'ETH':1100,'DASH':35,'ZEC':256,'XRP':68000,'NEO':4000,'ADL':8000,'BCH':84,'BCC':0}

def loadPolBalances():
    
    polBalances = polConn.returnBalances()
    for coin, value in polBalances.iteritems():
        balance = float(value)
        dbMod.insertBalances('POLONIEX',coin,balance)
        dbMod.updateBalances('POLONIEX',coin,balance)
    return True

def loadBittBalances():
    
    bittBalances = bittConn.get_balances()
    #print bittBalances
    for key, value in bittBalances.iteritems():
        if key == 'result':
            for coinBals in value:
                coin = coinBals["Currency"]
                balance = float(coinBals["Balance"])
                dbMod.insertBalances('BITTREX',coin,balance)
                dbMod.updateBalances('BITTREX',coin,balance)

def loadBitfBalances():
    
    bitfBalances = bitfConnTrade.balances()
    print bitfBalances
    for coinBals in bitfBalances:
        coin = coinBals["currency"]
        balance = float(coinBals["amount"])
        if balance != 0:
            dbMod.insertBalances('BITFINEX',coin.upper(),balance)
            dbMod.updateBalances('BITFINEX',coin.upper(),balance)

def loadPolPrices():

    polPrices = polConn.returnTicker()
    for key, value in polPrices.iteritems():
        coinPair = key
        price = value['last']
        dbMod.insertPrices('POLONIEX',coinPair,price)
        dbMod.updatePrices('POLONIEX',coinPair,price)

def loadBittPrices():
    
    bittPrices = bittConn.get_markets()
    price = 0
    for key, value in bittPrices.iteritems():
        if key == 'result':
            for coinMarkets in value:
                coinPair = coinMarkets["MarketName"]
                priceDict = bittConn.get_ticker(coinPair)
                thisPriceDict = priceDict['result']
                if thisPriceDict is not None:
                    thisLast = thisPriceDict['Last'] 
                    dbMod.insertPrices('BITTREX',coinPair,thisLast)
                    dbMod.updatePrices('BITTREX',coinPair,thisLast)

def loadBitfPrices():
    
    bitfPrices = bitfConnClient.ticker(0)
    price = 0
    print bitfPrices
    for key, value in bitfPrices.iteritems():
        if key == 'result':
            for coinMarkets in value:
                coinPair = coinMarkets["MarketName"]
                priceDict = bitfConn.get_ticker(coinPair)
                thisPriceDict = priceDict['result']
                if thisPriceDict is not None:
                    thisLast = thisPriceDict['Last'] 
                    dbMod.insertPrices('BITFINEX',coinPair,thisLast)
                    dbMod.updatePrices('BITFINEX',coinPair,thisLast)

def loadTotalBalHistory():
    
    activeExchanges = ['POLONIEX','BITTREX']


    currBTCPrice = dbMod.getBTCPrice()

    for exchange in activeExchanges:
        totalBTCList = dbMod.getTotalBTCExch(exchange)
        totalBTC = totalBTCList[0][0]
        if totalBTC is not None:
            usdValue = totalBTC * currBTCPrice[0][0]
            dbMod.insertTotBalHist(nowTime, exchange, 'BTC', totalBTC, usdValue)
        
    
def checkWallets():
    currBTCPrice = dbMod.getBTCPrice()
    if len(currBTCPrice) > 0:
        for coin, amt in wallets.iteritems():
            coinPrice = dbMod.getCoinPrice(coin)
            if len(coinPrice) != 0:
                thisCoinPrice = coinPrice[0][0]
                btcValue = thisCoinPrice * amt
                usdValue = btcValue * currBTCPrice[0][0]
                #print type(btcValue)
                #print nowTime 
                #print type(usdValue)
                dbMod.insertTotBalHist(nowTime, 'WALLET', coin, btcValue, usdValue)
    
    totalBTC = dbMod.getTotalBTC()
    decimalTotalBTC = totalBTC[0][0]
    #print type(decimalTotalBTC)
    if len(totalBTC) != 0:
        currBTCPrice = dbMod.getBTCPrice()
        #print currBTCPrice
        usdValue = decimalTotalBTC * currBTCPrice[0][0]
        print "============================================"
        print "You're total BTC holdings: " + str(decimalTotalBTC)
        print
        print "USD equivalent: " + str(usdValue)
        print "BTC/USD: " + str(currBTCPrice[0][0])
        print "============================================"
        dbMod.insertTotBalHist(nowTime, 'TOTAL', 'BTC', decimalTotalBTC, usdValue)
    else:
        print "Cannot load BTC price from DB."


loadPolBalances()
loadBittBalances()
#loadBitfBalances()
loadPolPrices()
loadBittPrices()
#loadBitfPrices()
loadTotalBalHistory()
checkWallets()
