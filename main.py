from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

origin = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origin)


def getList():
    url = "https://api.coinpaprika.com/v1/tickers"

    paramDict = {}
    paramDict.setdefault('quotes', 'KRW')

    requests_data = requests.get(url, params=paramDict)

    jsonData = []
    status_code = requests_data.status_code

    if status_code == 200:
        for idx, data in enumerate(requests_data.json()):
            if idx < 30:
                rank = data["rank"]
                name = data["name"]
                symbol = data["symbol"]
                price = data["quotes"]["KRW"]["price"]
                total_price = data["quotes"]["KRW"]["price"]
                change = data["quotes"]["KRW"]["percent_change_24h"]

                body = {"rank": rank, "name": name, "symbol": symbol, "price": price,
                        "total_price": total_price, "change": change}

                jsonData.append(body)
            else:
                break

    else:
        jsonData.append({})

    final = {"state": status_code, "body": jsonData}

    return final


@app.get("/list/")
def work():
    data = getList()

    return data
