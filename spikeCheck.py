import time
import calendar
import psycopg2
import myConnection
import dbMod
import sendSMS
import broker

polCon = myConnection.getPolConn()

currHour = time.strftime("%Y/%m/%d %H")
currMin = time.strftime("%M")

# Check if 2 periods spike 30 percent over price average

weekInSeconds = 604800
monthInSeconds = 2592000
twoMonthsInSeconds = 2592000*2
threeMonthsInSeconds = 2592000*3
fourHoursInSeconds = 14400
oneDayInSeconds = 86400
fiveMinutesInSeconds = 500

tickPeriod = fiveMinutesInSeconds

nowTimeEpoch = calendar.timegm(time.gmtime())
# endTimeEpoch = calendar.timegm(time.gmtime()) - (5 * tickPeriod)
endTimeEpoch = nowTimeEpoch
startTimeEpoch = endTimeEpoch  - (3 * tickPeriod)

btcTickPairs = []

percentInc = 1.1
percentDec = 0.9

def checkEachTick():
    
    try: 
        polTicker = polCon.returnTicker()
        tickPairKeys = polTicker.keys()
    except:
	print "Connection error"
	exit()


    for tickPair in tickPairKeys:
        if tickPair.startswith("BTC"):
            btcTickPairs.append(tickPair)
    
    for pairName in btcTickPairs:
        lastFourTicks = dbMod.getLastThreePeriods(pairName)
        if len(lastFourTicks) > 3:
            close3 = lastFourTicks[0][1]
            close2 = lastFourTicks[1][1]
            close1 = lastFourTicks[2][1]
            close0 = lastFourTicks[3][1]
            thisPercent = close3/close0
	    #print "Percent change for " + pairName + ": " + str(thisPercent)
#      	    if close3/close2 > percentInc and close2/close1 > percentInc and close1/close0 > percentInc:
#                print "%s STREAKING" % (pairName)
#                message = pairName + " is going to the MOON!"
#                sendSMS.sendMessage(message)
#                broker.buyPairSpike(pairName)
#    	    if close3/close2 < percentDec and close2/close1  < percentDec and close1/close0 < percentDec:
#                print "%s DUMPING" % (pairName)
#                message = pairName + " is DUMPING!"
#                sendSMS.sendMessage(message)
#                broker.buyPairSpike(pairName)
      	    if thisPercent > percentInc:
                print pairName + " STREAKING - up " + str(thisPercent)
                message = pairName + " is going to the MOON!"
                sendSMS.sendMessage(message)
                broker.buyPairSpike(pairName)
    	    if thisPercent < percentDec:
                print pairName + " DUMPIN - down " + str(thisPercent)
                message = pairName + " is DUMPING!"
                sendSMS.sendMessage(message)
                broker.buyPairSpike(pairName)


