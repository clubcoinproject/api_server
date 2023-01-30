from fastapi import FastAPI
import requests

app = FastAPI()


@app.get("/list/")
def getList():
    url = "https://api.coinpaprika.com/v1/tickers"

    headerDict = {}
    headerDict.setdefault('X-CoinAPI-Key', '45098E05-4005-4912-9893-1446614726B6')
    paramDict = {}
    paramDict.setdefault('quotes', 'KRW')

    datas = requests.get(url, headers=headerDict, params=paramDict).json()

    result = []

    for idx, data in enumerate(datas):
        if idx < 30:
            rank = data["rank"]
            name = data["name"]
            symbol = data["symbol"]
            price = data["quotes"]["KRW"]["price"]
            total_price = data["quotes"]["KRW"]["price"]
            change = data["quotes"]["KRW"]["percent_change_24h"]

            result.append({"rank": rank, "name": name, "symbol": symbol, "price": price,
                           "total_price": total_price, "change": change})
        else:
            break

    return result
