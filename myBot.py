from BitmexBot import BitmexBot
import numpy as np
import time

client = BitmexBot()
contractsOnMarket = 0
bought = False
sold = False
HMA_1_val = input("Introdu HMA-ul mai mic: ")
HMA_2_val = input("Introdu HMA-ul mai mare(max 650): ")
directive_HMA_val = input("Introdu HMA-ul directiv(max 650): ")

while True:
    client.getClosePrices('5m')
    myContracts = client.getAvailableContracts()
    lastClose = client.lastClose
    HMA_1 = client.HMA(int(HMA_1_val))
    HMA_2 = client.HMA(int(HMA_2_val))
    directive_HMA = client.HMA(int(directive_HMA_val))


    #case 1
    if directive_HMA > HMA_1 and directive_HMA > HMA_2 and sold == True:

        client.Buy(contractsOnMarket)
        sold = False
        contractsOnMarket = 0
        print("SHORT CLOSED")

    elif directive_HMA < HMA_1 and directive_HMA < HMA_2 and bought == True:

        client.Sell(contractsOnMarket)
        bought = False
        contractsOnMarket = 0
        print("LONG CLOSED")


    #case 2
    if directive_HMA < HMA_1 and directive_HMA < HMA_2 and sold == False:

        client.Sell(myContracts)
        sold = True
        contractsOnMarket = myContracts
        print("SHORT OPENED WITH {}CONTRACTS".format(myContracts))

    elif directive_HMA > HMA_1 and directive_HMA < HMA_2 and sold == True:

        client.Buy(contractsOnMarket)
        sold = False
        contractsOnMarket = 0
        print("SHORT CLOSED")

    #case 3
    if directive_HMA > HMA_1 and directive_HMA > HMA_2 and bought == False:

        client.Buy(myContracts)
        bought = True
        contractsOnMarket = myContracts
        print("LONG OPENED WITH {}CONTRACTS".format(myContracts))

    elif directive_HMA < HMA_1 and directive_HMA > HMA_2 and bought == True:

        client.Sell(contractsOnMarket)
        bought = False
        contractsOnMarket = 0
        print("LONG CLOSED")


    if bought == sold == False:
        print("NO OPORTUNITY FOUND")
    elif sold == True:
        print("SHORT OPENED")
    elif bought == True:
        print("LONG OPENED")

    time.sleep(2)
