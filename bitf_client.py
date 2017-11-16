from bitfinex_client import Client
import myConnection

client = Client()

symbols = client.symbols()
print(symbols)

symbol = 'btcusd'

#print(client.ticker(symbol))
#print(client.today(symbol))
#print(client.stats(symbol))

#parameters = {'limit_asks': 2, 'limit_bids': 2}

#print(client.lendbook('btc', parameters))
#print(client.order_book(symbol, parameters))

bitfConn = myConnection.getBitfConn()
print bitfConn

print bitfConn.balances()
