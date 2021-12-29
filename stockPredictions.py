import pandas as pd
import numpy as np
from urllib.request import Request, urlopen
import json
from copy import deepcopy
import copy

def getMovingAverage(numbersList):
    averageList = []
    alpha = 0.9
    initialValue = numbersList[0]
    movingAverage = numbersList[0]
    averageList.append(movingAverage)
    for number in numbersList[1:]:
        movingAverage = alpha * movingAverage + (1-alpha) * number
        averageList.append(movingAverage)
    return movingAverage

def stockPredictionMath(dfRead2):
    df = dfRead2.rename(columns={"5. adjusted close": "Adjusted Close", "tag": "Tag"})

    df2 = {'Adjusted Close': df["Adjusted Close"][9], 'Tag': df.Tag[0]}
    df = df.append(df2, ignore_index = True)

    df["Adjusted Close"] = df["Adjusted Close"].astype("float")
    df['10DayEMA'] = getMovingAverage([df['Adjusted Close'].shift(x) for x in range(10)]) 

    df["trend"] = df.apply(lambda x: "Negative" if x['Adjusted Close'] > x['10DayEMA'] else "Positive" if x['Adjusted Close'] < x['10DayEMA'] else "None", axis=1)
    df["EMAvInitialValueDiff"] = df.apply(lambda x: x['Adjusted Close'] - x['10DayEMA'], axis=1)
    df['Last10DaysAdjustedCloseSum'] = df['Adjusted Close'].shift(1) + df['Adjusted Close'].shift(2) + df['Adjusted Close'].shift(3) + df['Adjusted Close'].shift(4) + df['Adjusted Close'].shift(5) + df['Adjusted Close'].shift(6) + df['Adjusted Close'].shift(7) + df['Adjusted Close'].shift(8) + df['Adjusted Close'].shift(9) + df['Adjusted Close'].shift(10)
    df['Last10DaysAdjustedCloseMean'] = df['Last10DaysAdjustedCloseSum'] / 10
    df['volatilityInLast10Days'] = np.sqrt(((df['Adjusted Close'].shift(1)-df['Last10DaysAdjustedCloseMean'])**2 + (df['Adjusted Close'].shift(2)-df['Last10DaysAdjustedCloseMean'])**2 + (df['Adjusted Close'].shift(3)-df['Last10DaysAdjustedCloseMean'])**2 + (df['Adjusted Close'].shift(4)-df['Last10DaysAdjustedCloseMean'])**2 + (df['Adjusted Close'].shift(5)-df['Last10DaysAdjustedCloseMean'])**2 + (df['Adjusted Close'].shift(6)-df['Last10DaysAdjustedCloseMean'])**2 + (df['Adjusted Close'].shift(7)-df['Last10DaysAdjustedCloseMean'])**2 + (df['Adjusted Close'].shift(8)-df['Last10DaysAdjustedCloseMean'])**2 + (df['Adjusted Close'].shift(9)-df['Last10DaysAdjustedCloseMean'])**2 + (df['Adjusted Close'].shift(10)-df['Last10DaysAdjustedCloseMean'])**2) / 10)
    # print(df)
    df = df.drop(columns = ["Last10DaysAdjustedCloseSum", "Last10DaysAdjustedCloseMean"])
    df = df.dropna()
    return(df)

def stockPredictionDFReturn(inputSymbol):
    split = inputSymbol.split("\r\n")
    inputSymbol = ','.join(split)
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={inputSymbol}&outputsize=11&datatype=json&apikey=NX1E5LZVHDZWVVBB'
    
    response = Request(url)
    response = urlopen(response)    

    data = json.loads(response.read())
    # data will become a dictionary with a key of 'Error Message' if symbol not found
    if "Error Message" in data.keys():
        emptyDf = pd.DataFrame([])
        return(emptyDf, emptyDf)
    try:
        df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient="index")
    except:
        emptyDf = pd.DataFrame([])
        return(emptyDf, emptyDf)
    # get only 2 weeks 
    df = df.iloc[0:10]
    # Probably want that index to be a DatetimeIndex
    df.index = pd.to_datetime(df.index)

    df['tag'] = inputSymbol 

    # To get a pandas df that just has adjusted close, select that column
    adj_close = df.loc[:, ['5. adjusted close', 'tag']] 

    dfRet = copy.deepcopy(adj_close)
    dfRet = dfRet.rename(columns={"5. adjusted close": "Adjusted Close", "tag": "Tag"})

    df = stockPredictionMath(adj_close)

    return(df, dfRet)