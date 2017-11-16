import numpy as np

sampleData = open('sampleData.txt','r').read()
splitData = sampleData.split('\n')

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



x = 1
TRDates = []
TrueRanges = []

while x < len(date):
    TRDate,TrueRange = TR(date[x],closep[x],highp[x],lowp[x]
                          ,openp[x],closep[x-1])
    TRDates.append(TRDate)
    TrueRanges.append(TrueRange)
    x += 1

def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a =  np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a

ATR = ExpMovingAverage(TrueRanges,14)

print ATR