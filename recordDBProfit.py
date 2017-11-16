import psycopg2
from config import config
import sys

period=sys.argv[1]

conn = None

# read the connection parameters
params = config()

def insertTestRun(period, profit):

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    try:
        command= "INSERT INTO TEST_RUN (period, profit) VALUES ('" + str(period) + "', " + str(profit) + ")"
        cur.execute(command)
	conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print "End of error detection"
    finally:
        if conn is not None:
            conn.close()

def selectProfit():

    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    query = "select sum(profit) from history"

    cur.execute(query)
    rows = cur.fetchall()

    conn.close()

    return rows

thisProfit = selectProfit()

p = thisProfit[0][0]

if p is not None:
    insertTestRun(period, p)
