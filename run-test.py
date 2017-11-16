fifteenMinsInSeconds = 900
startDays = 100
startDay = 1507291200

for i in range(100):
    curEndDate = startDay - (fifteenMinsInSeconds * startDays)
    startDays = startDays - 1
    python cP-test.py startDays
