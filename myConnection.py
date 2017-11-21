from poloniex import Poloniex
from bittrex import Bittrex
from bitfinex_client import TradeClient
from bitfinex_client import Client
import os

def getPolConn():
    polCon = Poloniex(os.environ.get('POLI_KEY'),os.environ.get('POLI_SECKEY'))
    return polCon

def getBittConn():
    bittCon = Bittrex(os.environ.get('BITT_KEY'),os.environ.get('BITT_SECKEY'))
    return bittCon

def getBitfConnTrade():
    bitfConTrade = TradeClient(os.environ.get('BITF_KEY'),os.environ.get('BITF_SECKEY'))
    return bitfConTrade

def getBitfConnClient():
    bitfConClient = Client()
    return bitfConClient
