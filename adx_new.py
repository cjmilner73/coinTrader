import numpy as np

sampleData = open('sampleData.txt','r').read()
splitData = sampleData.split('\n')

# my code to replace sampelData with database data

time_period = 14



# end of my code

date,closep,highp,lowp,openp,volume = np.loadtxt(splitData,
                                                  delimiter=',',
                                                  unpack=True)


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
        #print "Sending these: " + str(date[x]) + ", close: " + str(closep[x])
        TRDates.append(TRDate)
        TrueRanges.append(TrueRange)

        DMDate,PosDM,NegDM = DM(date[x],openp[x],highp[x],lowp[x],closep[x],openp[x-1],highp[x-1],lowp[x-1],closep[x-1])
        PosDMs.append(PosDM)
        NegDMs.append(NegDM)

        x += 1

    print len(PosDMs)

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

def ADX():
    PositiveDI,NegativeDI = calcDIs()

    xxx = 0
    DXs = []

    while xxx < len(date[1:]):
        DX = 100*( (abs(PositiveDI[xxx]-NegativeDI[xxx])))/(PositiveDI[xxx]+NegativeDI[xxx])

        DXs.append(DX)
        xxx += 1

    ADX = ExpMovingAverage(DXs,time_period)

    print ADX
    posDI = PositiveDI[len(PositiveDI)-1]
    negDI = NegativeDI[len(NegativeDI)-1]
    print posDI
    print negDI

ADX()







