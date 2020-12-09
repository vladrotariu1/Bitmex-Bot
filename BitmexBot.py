import bitmex
import pandas as pd
import numpy as np
import csv

from keys_testnet import public as test_PK
from keys_testnet import secret as test_SK
from keys import public_key as PK
from keys import secret_key as SK


class BitmexBot:

    #constructor
    def __init__(self):
        testOrReal = input("Te conectezi la BitMEX test sau real?(scrie 't' sau 'r'): ")
        if testOrReal == 'r':
            self.client = bitmex.bitmex(test=False, api_key=PK, api_secret=SK)
            print("CONNECTED")
        elif testOrReal == 't':
            self.client = bitmex.bitmex(test=True, api_key=test_PK, api_secret=test_SK)
            print("CONNECTED")


    #set close price and get the last 900 candles in an array
    def getClosePrices(self, binSize):
        raw_candles = self.client.Trade.Trade_getBucketed(binSize=binSize, symbol='ETH', count=900, reverse=True).result()
        self.lastClose = raw_candles[0][0]['close']
        self.candles = []

        for i in range(0, 900):
            self.candles.append(raw_candles[0][900 - 1 - i]['close'])


    #set WMA
    def WMA(self, series=None, period=1):
        if series is None:
            gauss_sum = period*(period+1)
            gauss_sum /= 2
            WMA_vals = []
            aux = 0

            for i in range(0, period - 2):
                WMA_vals.append(0)

            for i in range(period - 1, len(self.candles)):
                n = period
                sum = 0

                while n >= 1:
                    sum += self.candles[aux + n-1] * n
                    n -= 1

                sum /= gauss_sum
                WMA_vals.append(sum)
                aux += 1

            WMA = pd.Series(WMA_vals)

            for i in range(0, period - 2):
                WMA[i] = np.nan

            return WMA
        else:
            gauss_sum = period*(period+1)
            gauss_sum /= 2
            WMA_vals = []
            aux = 0

            for i in range(0, period - 2):
                WMA_vals.append(0)

            for i in range(period - 1, len(series)):
                n = period
                sum = 0

                while n >= 1:
                    sum += series[aux + n-1] * n
                    n -= 1

                sum /= gauss_sum
                WMA_vals.append(sum)
                aux += 1

            WMA = pd.Series(WMA_vals)

            for i in range(0, period - 2):
                WMA[i] = np.nan

            return WMA

    #set HMA
    def HMA(self, period):
        first_WMA = 2 * self.WMA(period=int(period / 2))
        second_WMA = self.WMA(period=period)
        result_WMA = first_WMA - second_WMA

        HMA = self.WMA(series=result_WMA, period=int(np.sqrt(period)))
        return HMA[len(HMA) - 1]


    """

    Order functions

    """
    def Buy(self, qty):
        #buy crypto
        order = self.client.Order.Order_new(symbol="ETH", orderQty=qty, ordType="Market").result()
        self.registerOrder(order[0])


    def Sell(self, qty):
        #sell crypto
        order = self.client.Order.Order_new(symbol="ETH", orderQty=-1*qty, ordType="Market").result()
        self.registerOrder(order[0])


    def Buy_Stop(self, qty):
        #stop market order
        lastBuy = self.client.OrderBook.OrderBook_getL2(symbol = "ETH", depth = 1).result()[0][1]['price']
        stopPrice = np.floor(lastBuy*0.995)
        self.client.Order.Order_new(symbol="ETH", orderQty=qty, ordType="Market").result()
        self.client.Order.Order_new(symbol="ETH", orderQty=-1*qty, stopPx = stopPrice).result()


    def Sell_Stopself(self, qty):
        #stop market order
        lastSell = self.client.OrderBook.OrderBook_getL2(symbol = "ETH", depth = 1).result()[0][0]['price']
        stopPrice = np.floor(lastSell*1.005)
        self.client.Order.Order_new(symbol="ETH", orderQty=-1*qty, ordType="Market").result()
        self.client.Order.Order_new(symbol="ETH", orderQty=qty, stopPx = stopPrice).result()

    #Contracts available to use
    def getAvailableContracts(self):
        #lastBuy = self.client.OrderBook.OrderBook_getL2(symbol = "XBT", depth = 1).result()[0][1]['price']
        account = self.client.User.User_getWallet().result()[0]['amount']/10000
        return np.floor(account * lastBuy * 0.97)

    #write orders in file
    def registerOrder(self, order):
        with open('orders.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow([order['transactTime'], order['price'], order['side']])

    #Last buy price
    def lastBuy(self):
        lastBuy = self.client.OrderBook.OrderBook_getL2(symbol = "ETH", depth = 1).result()[0][1]['price']
        return lastBuy

    #Last sell price
    def lastSell(self):
        lastBuy = self.client.OrderBook.OrderBook_getL2(symbol = "ETH", depth = 1).result()[0][0]['price']
        return lastBuy
