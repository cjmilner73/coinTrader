import psycopg2
import initDB
from myConnection import getConn
import dbMod

polCon =  getConn()


polBal = polCon.returnBalances()

dbMod.insertBalances('balances',polBal)




 
