from .kucoin_api.Kucoin import *
from .coingecko.util import coinGeckoList
from .data_parsing import * 
from .postgres_db.bizThreads import *

import json

commonTickerList = ["ONE"]

# Some ticker/coin name are just that fucking bad
def addTickerToBlackList(ticker):
    query = "INSERT INTO blackListTicker (ticker) VALUES ('%s') ON CONFLICT (ticker) DO NOTHING"%(ticker)
    db.update_rows(query)

def getBlickList():
    query = "SELECT * FROM blackListTicker"
    results = db.select_rows(query)
    return results

def generateCurrenciesList():
    # calling kucoin api to get all coins
    # currenciesResponse = getCurrencies()
    blackList = getBlickList()
    geckoCoinList = coinGeckoList()
    coins = []
    # Looping through coins to get ticker and name
    for row in geckoCoinList:
        ticker = row["symbol"].upper()
        name = row["name"].upper()
        commonTicker = False
        # If ticker is in blackList mark as so
        if ticker in commonTickerList:
            commonTicker = True
        if ticker not in blackList:
            coin = {"aka":[ticker], 'name':name, "commonTicker" : commonTicker, "coinGeckoId":row["id"]}
            coins.append(coin)


    # save all coins in json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(coins, f, ensure_ascii=False, indent=4)
    

generateCurrenciesList()