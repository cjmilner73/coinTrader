import numpy as np
import psycopg2
from config import config

sampleData = open('sampleData','r').read()
splitData = sampleData.split('\n')

time_period = 14

# read the connection parameters
params = config()

conn = None

conn = psycopg2.connect(**params)

cur = conn.cursor()

lastTime = 0

pair = []
openp = []
date = []
openp = []
highp = []
lowp = []
closep = []
volume = []

def loadData(pairName):
 

    del pair[:]
    del openp[:]
    del date[:]
    del highp[:]
    del lowp[:]
    del closep[:]
    del volume[:]
    lastTime = 0
 
    query = "SELECT * from ohlcv where pair = %s order by timestamp_ut"
    args = (pairName,)
    cur.execute(query,args)
    rows = cur.fetchall()

    for row in rows:
        pair.append(row[0])
        date.append(row[1])
        openp.append(float(row[2]))
        highp.append(float(row[3]))
        lowp.append(float(row[4]))
        closep.append(float(row[5]))
        volume.append(row[6])

    if (len(rows) != 0):
        lastTime = rows[len(rows)-1][1]


    return lastTime
# end of my code

#date,closep,highp,lowp,openp,volume = np.loadtxt(splitData,
#                                                  delimiter=',',
#                                                  unpack=True)


def TR(d,c,h,l,o,yc):
    x = h-l
    y = abs(h-yc)
    z = abs(l-yc)

    if y <= x >= z:
        TR = x
    elif x <= y >= z:
        TR = y
    elif x <= z >= y:
        TR = z
    return d, TR

def DM(d,o,h,l,c,yo,yh,yl,yc):
    moveUp = h-yh
    moveDown = yl-l

    if 0 < moveUp > moveDown:
        PDM = moveUp
    else:
        PDM = 0

    if 0 < moveDown > moveUp:
        NDM = moveDown
    else:
        NDM = 0

    return d,PDM,NDM

def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a

def calcDIs():
    x = 1
    TRDates = []
    TrueRanges = []
    PosDMs = []
    NegDMs = []

    while x < len(date):
        TRDate, TrueRange = TR(date[x],closep[x],highp[x],lowp[x]
                          ,openp[x],closep[x-1])
        TRDates.append(TRDate)
        TrueRanges.append(TrueRange)

        DMDate,PosDM,NegDM = DM(date[x],openp[x],highp[x],lowp[x],closep[x],openp[x-1],highp[x-1],lowp[x-1],closep[x-1])
        PosDMs.append(PosDM)
        NegDMs.append(NegDM)

        x += 1

    #print len(PosDMs)

    expPosDM = ExpMovingAverage(PosDMs,time_period)
    expNegDM = ExpMovingAverage(NegDMs,time_period)
    ATR = ExpMovingAverage(TrueRanges,time_period)

    xx = 0

    PDIs = []
    NDIs = []

    while xx < len(ATR):
        PDI = 100*(expPosDM[xx]/ATR[xx])
        PDIs.append(PDI)

        NDI = 100*(expNegDM[xx]/ATR[xx])
        NDIs.append(NDI)

        xx += 1

    return PDIs,NDIs

def ADX(pairName):

    hasHitHigh = False

    lastTime = loadData(pairName)

    PositiveDI,NegativeDI = calcDIs()

    xxx = 0
    DXs = []

    while xxx < len(date[1:]):
        DX = 100*( (abs(PositiveDI[xxx]-NegativeDI[xxx])))/(PositiveDI[xxx]+NegativeDI[xxx])

        DXs.append(DX)

        xxx += 1

    ADX = ExpMovingAverage(DXs,time_period)

    if (PositiveDI[len(PositiveDI)-1] > NegativeDI[len(NegativeDI)-1]):
        upTrend = True
    else:
        upTrend = False

    print "Processed ADX for: " + pairName + " : " + str(ADX[len(ADX)-1]) + " : " + str(upTrend)

    highestValue = max(closep)
    closeLast = closep[len(closep)-1]
    adxLastDec = ADX[ADX.size-1]
    adxLastStr = str(ADX[ADX.size-1])

    if (closeLast >= highestValue):
        hasHitHigh = True

    if (adxLastDec > 40 and hasHitHigh):
        return (pairName,adxLastStr,upTrend,lastTime, closeLast)


