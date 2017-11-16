import time
import calendar
import adx
from poloniex import Poloniex
from pymongo import MongoClient
from myConnection import getConn

polCon =  getConn()

client = MongoClient('mongodb://localhost:27017')

currHour = time.strftime("%Y/%m/%d %H")
currMin = time.strftime("%M")

weekInSeconds = 604800
monthInSeconds = 2592000
twoMonthsInSeconds = 2592000*2
threeMonthsInSeconds = 2592000*3
fourHoursInSeconds = 14400
oneDayInSeconds = 86400
fiveMinsInSeconds = 900

startEpoch = oneDayInSeconds
tickPeriod = fiveMinsInSeconds

nowTimeEpoch = calendar.timegm(time.gmtime())
# endTimeEpoch = calendar.timegm(time.gmtime()) - (5 * tickPeriod)
endTimeEpoch = nowTimeEpoch
startTimeEpoch = endTimeEpoch  - startEpoch

db = client.ticker_db

orderHist = polCon.returnTradeHistory("BTC_STR")

for i in orderHist:
    print i