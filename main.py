from datetime import datetime
from os import path

import pandas as pd
import requests
from datetime import timedelta

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import absl.logging
from model_maker import make_model as make

app = FastAPI()

absl.logging.set_verbosity(absl.logging.ERROR)


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
    headerDict.setdefault('X-CoinAPI-Key', '13B4AF90-AE6C-48FE-B10E-9A0F9FB091EA')

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
    time_end = datetime.today()

    headerDict = {}
    # headerDict.setdefault('X-CoinAPI-Key', '45098E05-4005-4912-9893-1446614726B6')
    # headerDict.setdefault('X-CoinAPI-Key', '13B4AF90-AE6C-48FE-B10E-9A0F9FB091EA')
    # headerDict.setdefault('X-CoinAPI-Key', '9806E3B9-F8E5-4D92-B000-26700ADA8368')
    # headerDict.setdefault('X-CoinAPI-Key', 'E98F1738-D0A9-4C3E-88DB-B9241CD5E9DA')
    # headerDict.setdefault('X-CoinAPI-Key', '03F8F1A6-7114-468C-B36E-960B7CF98500')
    # headerDict.setdefault('X-CoinAPI-Key', 'FDE3DE5C-C457-4D77-9AAA-B8917A7AEC9D')
    # headerDict.setdefault('X-CoinAPI-Key', '810C44D6-21FA-48CA-9B60-6688B4FBE0D5')
    # headerDict.setdefault('X-CoinAPI-Key', '71ED414B-FC5C-42EE-8A36-3F207EE49E79')
    # headerDict.setdefault('X-CoinAPI-Key', '1321F196-5129-4580-875A-0BF9C1A0011B')
    # headerDict.setdefault('X-CoinAPI-Key', 'E6B4F9D8-64D7-4307-8F6A-BEC95B24ED7F')
    headerDict.setdefault('X-CoinAPI-Key', '766A8712-F5FE-4BAD-A0D3-EDBA432BD452')

    paramDict = {'period_id': '1DAY', 'time_start': '2018-01-01',
                 'time_end': time_end.strftime("%Y-%m-%d"), 'limit': '7500'}

    tomorrow = time_end + timedelta(days=1)

    df = get_df(symbol, paramDict, headerDict)

    max_num, min_num = 0, 0

    if not path.exists(f"./models/{symbol}_model"):
        max_num, min_num = make.getResult(symbol, df)

    result = make.getPred(symbol, df, max_num, min_num)
    result_dict = {'date': tomorrow.strftime("%Y-%m-%d"), 'pred': round(float(result[0]), 2)}

    return jsonable_encoder(result_dict)


def get_df(symbol, param, header):
    url = f"https://rest.coinapi.io/v1/exchangerate/{symbol}/KRW/history"

    requests_data = requests.get(url, params=param, headers=header).json()

    df = pd.DataFrame(requests_data).iloc[::-1]
    df = df.drop(['time_period_end', 'time_open', 'time_close'], axis=1)
    df.columns = ['date', 'open', 'high', 'low', 'close']
    df = df.round(2)
    df['date'] = pd.to_datetime(df['date']).dt.date

    return df


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
