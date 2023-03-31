import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
from keras.layers import Dense
from keras.layers import LSTM
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler


def load_dataset(df):
    raw_data = df

    print('Number of rows and columns:', raw_data.shape)

    raw_data['date'] = pd.to_datetime(raw_data['date'], format='%Y-%m-%d')
    raw_data['close'] = raw_data['close'].apply(lambda x: float(str(x).replace(',', '')))
    raw_data['open'] = raw_data['open'].apply(lambda x: float(str(x).replace(',', '')))
    raw_data['high'] = raw_data['high'].apply(lambda x: float(str(x).replace(',', '')))
    raw_data['low'] = raw_data['low'].apply(lambda x: float(str(x).replace(',', '')))

    # 모델 정확성을 위한 normalize 처리
    number_data = raw_data.iloc[:, 1:5]

    nMax = np.max(number_data)[-1]
    nMin = np.min(number_data)[-1]

    print('1', nMax, nMin)

    scaler = MinMaxScaler()
    scaler.fit(number_data)
    raw_data.iloc[:, 1:5] = scaler.transform(number_data)


    # 2번째 인자 31은 30일간 데이터를 모델이 볼 것이라는 뜻이고, 3번쨰 인자 4는 모델이 보고 판단할 인자의 갯수다.
    array_data = np.zeros(shape=(raw_data.shape[0] - 1, 31, 4))
    for i in range(raw_data.shape[0] - 31):
        for j in range(31):
            if i - j < 0:
                continue
            array_data[i][j] = raw_data.iloc[i - j, 1:5]

    print(raw_data.sample(5))
    test_size = 365

    training_set = array_data[test_size:]
    test_set = array_data[31:test_size]
    test_set_dates = raw_data['date'].iloc[31:test_size]

    training_set_x = training_set[:, :-1, :-1]
    training_set_y = training_set[:, -1, -1]

    test_set_x = test_set[:, :-1, :-1]
    test_set_y = test_set[:, :1, -1]

    print(training_set_x.shape)
    print(training_set_y.shape)
    return (
        (training_set_x, training_set_y), (test_set_x, test_set_y), test_set_dates, nMax, nMin)


# 목표: 최근 30일의 데이터를 보고 다음날의 종가 가격 예측을 시도
def define_model():
    model = Sequential()

    # 첫 LSTM 레이어 유닛 갯수가 30인 이유는 최근 30일을 모델의 입력값으로 줄 예정이기 때문
    model.add(LSTM(30, return_sequences=True, input_shape=(30, 3)))
    model.add(LSTM(128, return_sequences=False))
    # 출력값은 다음날 종가 가격 하나뿐이니 유닛 카운트가 1이어야 함
    model.add(Dense(1, activation='linear'))

    model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])

    model.summary()

    return model


def getResult(symbol, df):
    tf.random.set_seed(128)  # 값이 달라지는걸 막기 위한 시드 고정

    ((training_set_x, training_set_y), (test_set_x, test_set_y), test_set_dates, max_num, min_num) = load_dataset(df)
    model = define_model()
    model.fit(x=training_set_x, y=training_set_y, validation_split=0.1, batch_size=100, epochs=50, )

    model.save(f'./models/{symbol}_model')

    print("2", max_num, min_num)

    return max_num, min_num


def getPred(symbol, df, max_num, min_num):
    tf.random.set_seed(128)

    ((training_set_x, training_set_y), (test_set_x, test_set_y), test_set_dates, nMax, nMin) = load_dataset(df)

    model = tf.keras.models.load_model(f'./models/{symbol}_model')

    pred = model.predict(test_set_x)

    result = pred * (max_num + min_num) - min_num

    print('3', max_num, min_num)

    return result[-1]
