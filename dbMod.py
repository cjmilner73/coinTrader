import psycopg2
from config import config

conn = None

# read the connection parameters
params = config()

def updateBalances(exchange, coin, amount):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    try:
        command= "UPDATE BALANCES SET amount = " + str(amount) + " WHERE exchange = '" + exchange + "' AND coin = '" + coin + "'"
        #command= "INSERT INTO balances (exchange, coin, amount) VALUES ('" + exchange + "', '" + coin + "', " + str(amount) + ")" + " ON CONFLICT ON CONSTRAINT balances_pkey DO UPDATE SET amount  = " + str(amount)
        cur.execute(command)
	conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print "End of error detection"
    finally:
        if conn is not None:
            conn.close()

def insertBalances(exchange, coin, amount):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    try:
        command= "INSERT INTO balances (exchange, coin, amount) VALUES ('" + exchange + "', '" + coin + "', " + str(amount) + ")"
        #command= "INSERT INTO balances (exchange, coin, amount) VALUES ('" + exchange + "', '" + pair + "', " + str(amount) + ")" + " ON CONFLICT ON CONSTRAINT balances_pkey DO UPDATE SET amount  = " + str(amount)
        cur.execute(command)
	conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        a = 0
    finally:
        if conn is not None:
            conn.close()

def updatePrices(exchange, pair, price):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    try:
        command= "UPDATE PRICES SET price = " + str(price) + " WHERE exchange = '" + exchange + "' AND pair = '" + pair + "'"
        cur.execute(command)
	conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        #print(error)
        print "End of error detection"
    finally:
        if conn is not None:
            conn.close()

def insertTotBalHist(nowTime, exchange, coin, totalBTC, usdValue):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    try:
        command= "INSERT INTO total_balance_history (balance_date, exchange, coin, btc_value, usd_Value) VALUES (" + str(nowTime) + ",'" + exchange + "', '" + coin + "', " + str(totalBTC) + ", " + str(usdValue) + ")"
        cur.execute(command)
	conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        #print(error)
        #print "End of error detection"
        a = 0
    finally:
        if conn is not None:
            conn.close()

def insertPrices(exchange, pair, price):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    try:
        command= "INSERT INTO prices (exchange, pair, price) VALUES ('" + exchange + "', '" + pair + "', " + str(price) + ")"
        cur.execute(command)
	conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        #print(error)
        #print "End of error detection"
        a = 0
    finally:
        if conn is not None:
            conn.close()


def insertStatementsOHLCV(statements):

    sql = """INSERT INTO ohlcv(pair, timestamp_ut, open, high, low, close, volume) VALUES (%s,%s,%s,%s,%s,%s,%s);"""

    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        for s in statements:
            pair = s[0]
            timestamp_ut = s[1]
            openP = s[2]
            highP = s[3]
            lowP = s[4]
            closeP = s[5]
            volume = s[6]
            cur.execute(sql, (pair, timestamp_ut, openP, highP, lowP, closeP, volume))

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
          conn.close()

def insertOHLCV(ohlcv):
    pair = ohlcv[0]
    timestamp_ut = ohlcv[1]
    openP = ohlcv[2]
    highP = ohlcv[3]
    lowP =ohlcv[4]
    closeP = ohlcv[5]
    volume = ohlcv[6]

    sql = """INSERT INTO ohlcv(pair, timestamp_ut, open, high, low, close, volume) VALUES (%s,%s,%s,%s,%s,%s,%s);"""

    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql, (pair, timestamp_ut, openP, highP, lowP, closeP, volume))
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
          conn.close()

def deleteOHLCV():

    #command = "INSERT INTO ohlcv(pair, timestamp_ut, open, high, low, close, volume) VALUES (" + pair + ", " + timestamp_ut + ", " + open + ", " + high + ", " + low + ", " + close + ", " + volume
    sql = """delete from ohlcv;"""

    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        cur.execute(sql)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
          conn.close()

def insertPotential(myPotential):

    pair = myPotential[0]
    adx = int(float(myPotential[1]))
    upTrend = myPotential[2]
    startTime = myPotential[3]
    startPrice = myPotential[4]

    #command = "INSERT INTO ohlcv(pair, timestamp_ut, open, high, low, close, volume) VALUES (" + pair + ", " + timestamp_ut + ", " + open + ", " + high + ", " + low + ", " + close + ", " + volume
    sql = """INSERT INTO potentials(pair, adx, adx_start_ut, direction, start_price) VALUES (%s,%s,%s,%s,%s);"""

    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql, (pair, adx, startTime, upTrend, startPrice))
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print "Error at insertPotential"
        print(error)
    finally:
        if conn is not None:
          conn.close()

def insertHistory(pairName, activeType, entryTime, exitTime, direction, startPrice, lastPrice, amount, profit):

    sql = """INSERT INTO HISTORY (pair, active_type, ut_entered, ut_exited, direction, price, exit_price, amount, profit) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql, (pairName, activeType, entryTime, exitTime, direction, startPrice, lastPrice, amount, profit))
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print "Error at insertHistory"
        print(error)
    finally:
        if conn is not None:
          conn.close()

    deleteActive(pairName)

def insertActive(pairName, active_type, timestamp, direction, lastPrice, noOfCoinsToBuy, stop, limit):

    sql = """INSERT INTO ACTIVES (pair, active_type, ut_bought, direction, price, amount, stop_price, limit_price) VALUES (%s, %s,%s,%s,%s,%s,%s,%s);"""
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(sql, (pairName, active_type, timestamp, direction, lastPrice, noOfCoinsToBuy, stop, limit))
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print "Error at insertActive"
        print(error)
    finally:
        if conn is not None:
          conn.close()

    deletePotential(pairName)

def getCoinPrice(coin):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    
    pair = "BTC_" + coin


    query = "select price from prices where pair = '" + pair + "' and exchange = 'POLONIEX'"

    cur.execute(query)
    rows = cur.fetchall()

    conn.close()

    if coin == 'BTC':
        rows = [(1,)]

    return rows

def getBTCPrice():

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "select price from prices where pair = 'USDT_BTC' and exchange = 'POLONIEX'"

    cur.execute(query)
    rows = cur.fetchall()

    conn.close()

    return rows

def getTotalBTC():

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "select sum(btc_value) from total_balance_history where balance_date = (select max(balance_date) from total_balance_history) and exchange != 'TOTAL'"

    cur.execute(query)
    rows = cur.fetchall()

    conn.close()

    return rows

def getTotalBTCExch(exchange):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "select sum(amount*price) from balances, prices where substr(pair,5,length(pair)) = coin and (pair like 'BTC\_%' or pair like 'BTC-%') and balances.exchange = prices.exchange and balances.exchange = '" + exchange + "'"

    cur.execute(query)
    rows = cur.fetchall()

    conn.close()

    return rows

def getExisting():

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "SELECT pair from potentials UNION select pair from actives"
    cur.execute(query)
    rows = cur.fetchall()

    conn.close()

    return rows

def getPotentials():

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "SELECT * from potentials"
    cur.execute(query)
    rows = cur.fetchall()

    conn.close()

    return rows

def deleteActive(pairName):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "DELETE FROM actives WHERE pair = %s"
    cur.execute(query, (pairName,))
    conn.commit()

    conn.close()

def deletePotential(pairName):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "DELETE FROM potentials WHERE pair = %s"
    cur.execute(query, (pairName,))
    conn.commit()

    conn.close()

def setHotsetTrigger(pairName, hot, trigger, lowPrice, highPrice):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "UPDATE potentials SET HOT = %s, TRIGGER = %s, LOW_PRICE = %s, HIGH_PRICE = %s WHERE pair = %s"
    cur.execute(query, (hot,trigger,lowPrice,highPrice,pairName))
    conn.commit()

    conn.close()

def getLastThreePeriods(pairName):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    #query = "SELECT pair, close from ohlcv where pair = %s and timestamp_ut > %s order by timestamp_ut"
    query = "SELECT pair, close from ohlcv where pair = %s order by timestamp_ut desc limit 4"
    #query = "SELECT distinct close, max(timestamp_ut) from ohlcv where pair = %s group by close order by max(timestamp_ut) desc limit 4"
    cur.execute(query, (pairName,))
    rows = cur.fetchall()

    conn.close()

    return rows

def getOHLCV(pairName, startDate):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "SELECT * from ohlcv where pair = %s and timestamp_ut >= %s order by timestamp_ut"
    cur.execute(query, (pairName, startDate))
    rows = cur.fetchall()

    conn.close()

    return rows

def getActives():

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "SELECT pair, active_type, ut_bought, direction, price, amount, stop_price, limit_price from actives"
    cur.execute(query,)
    rows = cur.fetchall()

    conn.close()

    return rows

def getSellTriggers():

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "SELECT pair, trigger, direction, low_price, high_price from potentials where hot = 'TRUE' and direction = 'SELL'"
    cur.execute(query,)
    rows = cur.fetchall()

    conn.close()

    return rows

def getBuyTriggers():

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "SELECT pair, trigger, direction, low_price, high_price from potentials where hot = 'TRUE' and direction = 'BUY'"
    cur.execute(query,)
    rows = cur.fetchall()

    conn.close()

    return rows

def getCoinBalance(coin):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "SELECT amount from balances where coin = '" + coin + "' and exchange = 'POLONIEX'"
    cur.execute(query,)
    rows = cur.fetchall()

    conn.close()
    return rows
