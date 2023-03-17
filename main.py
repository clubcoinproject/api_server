from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
from fastapi.encoders import jsonable_encoder

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
                price = round(data["quotes"]["KRW"]["price"], 2)
                total_price = round(data["quotes"]["KRW"]["market_cap"], 2)
                change = round(data["quotes"]["KRW"]["percent_change_24h"], 2)

                body = {"rank": rank, "name": name, "symbol": symbol, "price": price,
                        "total_price": total_price, "change": change}

                jsonData.append(body)
            else:
                break

    else:
        jsonData.append({})

    final = {"state": status_code, "body": jsonData}

    return final


def getDetail(symbol):
    url = f"https://rest.coinapi.io/v1/exchangerate/{symbol}/KRW/history"

    paramDict = {}
    paramDict.setdefault('period_id', '1DAY')

    headerDict = {}
    headerDict.setdefault('X-CoinAPI-Key', '45098E05-4005-4912-9893-1446614726B6')

    requests_data = requests.get(url, params=paramDict, headers=headerDict)

    jsonData = []
    status_code = requests_data.status_code

    if status_code == 200:
        for idx, data in enumerate(requests_data.json()):
            if idx < 30:
                date = data['time_period_start'][:10]
                price = round(data['rate_close'], 2)

                body = {"date": date, "price": price}

                jsonData.append(body)
            else:
                break

    else:
        jsonData.append({})

    final = {"state": status_code, "body": jsonData}

    return final


def getForcasting(symbol):
    url = f"https://rest.coinapi.io/v1/exchangerate/{symbol}/KRW/history"

    time_end = datetime.today().strftime("%Y-%m-%d")
    paramDict = {'period_id': '1DAY', 'time_start': '2015-01-01', 'time_end': time_end, 'limit': '2500'}

    headerDict = {}
    headerDict.setdefault('X-CoinAPI-Key', '45098E05-4005-4912-9893-1446614726B6')

    requests_data = requests.get(url, params=paramDict, headers=headerDict).json()
    jsonable_encoder(requests_data)

    return jsonable_encoder(requests_data)


@app.get("/list/")
def work():
    data = getList()

    return data


@app.get("/detail")
def detail(symbol):
    data = getDetail(symbol)

    return data


@app.get("/forcasting")
def forcasting(symbol):
    return getForcasting(symbol)
