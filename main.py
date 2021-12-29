
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask import Flask, render_template , request, jsonify, url_for
import os
from flask_bootstrap import Bootstrap
from test import predict, generateGraphs
import time
import re
import tweepy as tw
from datetime import date, timedelta
import pickle
import pandas as pd
import tweepy as tw
import pandas as pd
from textblob import TextBlob
import time

import stockPredictions
import twitterGetPredictions

from urllib.request import Request, urlopen
import pandas as pd
import json
import copy
from copy import deepcopy

from flask import Markup



#X_train = pickle.load(open("X_train_sample", 'rb')).head(3)
#loaded_model = pickle.load(open("hackutdLR", 'rb'))
#predictions = loaded_model.predict(X_train)


most_recent_id = ''
userInput = ""
companyList = [] # list of companies in the database input by user
# STFGX, GS, EOG, COF
tempList = []

OverallSentiment = []                   # Float: will be an overall sentiment score
HistoricalDataOverTwitterSentiment=[]   # String: will be a png address string
VolatilityScore = []                    # Float: basically the R^2 score
OverallRecommendation = []              # String: will be a reconmendation, either long, short or neither. Long is to buy the stock, Short is to borrow the stock, and neither is to ignore.
TweetsToDisplay = []                    # String: will be links to twitter posts we want to embed

BestRecommendation = ''
 
X_train = pickle.load(open("X_train_sample", 'rb')).head(len(companyList))
loaded_model = pickle.load(open("cvModel.pickle", 'rb'))

OverAnalysisScoresTime=[1,2,3] # Placeholder



# For this program, the argument will be a company to search tweets for and then we will do sentiment analysis

consumer_key = 'Viy4m1f54xwpqpRSXMI5QPn3W'
consumer_secret = 'wlMGrinrdyj76DPsYKOPcMUmZpFIXVkSW7l0bD3WGBLj8RT1DO'
access_token = '1454677316626305026-wkxe74jlt31OwrutMbpdxfrFQ02VNv'
access_token_secret = 'HSX2AZ51dBNv5s6m2CU0pcpQtPTePfjQXZjHrSAWQFxUX'
# consumer_key =  '2eNDubKY3DO8gBrLXgSTcPFOE'
# consumer_secret = 'Q2Boj27Uxb5KwnKWGsRNR8onwYLMXZM77rGm1lxdQaZzvRWm8i'
# access_token = '1177742606035386370-qk866epo3TYZwjsGgJTrBFft6eByW5'
# access_token_secret = 'y1eFOXqr3udNwQJ3BAuEyx6hamLwb9TjdWGYjCtMfs6ge'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

app = Flask(__name__, static_url_path='/static')
Bootstrap(app)
@app.route('/') 



def index():
    print("hello")
    return render_template("index.html",userInput = userInput,companyList=companyList, OverallSentiment=OverallSentiment, 
        HistoricalDataOverTwitterSentiment=HistoricalDataOverTwitterSentiment,VolatilityScore=VolatilityScore,
        OverallRecommendation=OverallRecommendation, BestRecommendation=BestRecommendation)

@app.route('/analyze', methods=['POST', 'GET'])
def analyze():
    # to do
    if request.method == 'GET':
        pass
    if request.method == 'POST':
        userInput = request.form['rawText']
    
    # clean the user input
    userInput = userInput.replace(" ", "")
    userInput = userInput.upper()
    companyList = userInput.split(",")
    companyList = list(companyList)
    
    companyList.sort()
    print(companyList)

    # reset the scores
    OverallSentiment = []                   
    HistoricalDataOverTwitterSentiment=[]   
    VolatilityScore = []                    
    OverallRecommendation = []
    TweetsToDisplay = []          
    OverallSentiment = []

    # establishing a dictionary of company tags and the relevant stock prediction attached to it
    predictions = {}
    stockDataForGraphing = {}
    stockDataPreds = {} # this will be a dictoinary with DataFrames as keys and will be input to the model
    
    newCompanyList = copy.deepcopy(companyList)
    bestCompanyRecommendation = ""
    bestCompanRecommendationProfit = -100000000
    for company in companyList:
        # Getting the dataframes for the data needed for stock predictions
        # ---------------------- twitter stuff here ----------------------
        # overallTwoWeekPositiveRateList = [] # looks like [0.5, 0.2, 0.5, 0.3] with size = num companies user searched for
        # perDayPositiveRateList = []  # looks like [[0.3, 0.23, 0.43, 0.2 ...], [0.334, 0.2, 0.5, 0.1 ...], [], []]  with size = num companies user serached for
        companyTweets = twitterGetPredictions.getTweetsForSpecificText("#" + company)
        overallTwoWeekPositiveRate, perDayPositiveRate = twitterGetPredictions.isPositiveForSpecificStock(companyTweets)
        # overallTwoWeekPositiveRate looks like 0.5
        # perDayPositiveRate looks like [0.2, 0.3, 0.2, 0.3, 0.2 ...]
        # overallTwoWeekPositiveRateList.append(overallTwoWeekPositiveRate)
        # perDayPositiveRateList.append(perDayPositiveRate)

        tempPred, stockDataForGraphingPerCompany = stockPredictions.stockPredictionDFReturn(company)
        if stockDataForGraphingPerCompany.empty:
            print("list", companyList, company)
            newCompanyList.remove(company)
            print("list", companyList)
            continue

        colors = []

        for x in perDayPositiveRate:
            if x == -1:
                colors.append("black")
            elif x >= 0.5:
                colors.append("green")
            else:
                colors.append("red")

        plt.plot(list(stockDataForGraphingPerCompany.index),stockDataForGraphingPerCompany["Adjusted Close"])
        print(list(stockDataForGraphingPerCompany.index))
        print(stockDataForGraphingPerCompany["Adjusted Close"])
        plt.scatter(list(stockDataForGraphingPerCompany.index),stockDataForGraphingPerCompany["Adjusted Close"], c=colors)
        title = company + " historical stock trends"
        plt.title(title)
        plt.xlabel('Adjusted Closing')
        plt.ylabel('Date')
        plt.xticks(rotation=45)

        pngname = "static/images/" + company + ".png"
        time.sleep(1)
        plt.savefig(pngname, bbox_inches='tight')
        time.sleep(1)

        plt.clf()

        stockDataForGraphing[company] = pngname
        tempPred = tempPred.drop(columns=['Tag', '10DayEMA', 'EMAvInitialValueDiff'])
        stockDataPreds[company] = tempPred
        '''
        looks like:
        Adjusted Close	Tag	    10DayEMA	trend	    EMAvInitialValueDiff	volatilityInLast10Days
    	119.110188	    IBM	    119.973188	Positive	-0.863001	            1.25627'''

        VolatilityScore.append(list(stockDataPreds[company].volatilityInLast10Days)[0])

        # ---------------------- twitter stuff here ----------------------
        stockDataPreds[company]['positivityRate'] = overallTwoWeekPositiveRate
        # convert categorical to integers
        stockDataPreds[company].trend = pd.Categorical(stockDataPreds[company].trend)
        stockDataPreds[company]['trend'] = stockDataPreds[company].trend.cat.codes
        

        OverallSentiment.append(overallTwoWeekPositiveRate)
        
        # model stuff
        modelPrediction = loaded_model.predict(stockDataPreds[company])[0] # looks like a float
        predictions[company] = modelPrediction

        initialStockValue = list(stockDataPreds[company]['Adjusted Close'])[0]

        predictionDifference = modelPrediction - initialStockValue
        if predictionDifference > bestCompanRecommendationProfit:
            bestCompanyRecommendationProfit = predictionDifference
            bestCompany = company

        if modelPrediction > initialStockValue:
            recommendation = Markup(f"Buy<br/>Most Recent Stock Price: {initialStockValue}<br/>Projected Stock Price In Two Weeks: {modelPrediction}")
        elif modelPrediction == initialStockValue:
            recommendation = Markup(f"Neutral<br/>Most Recent Stock Price: {initialStockValue}<br/>Projected Stock Price In Two Weeks: {modelPrediction}")
        else:
            recommendation = Markup(f"Don't Buy<br/>Most Recent Stock Price: {initialStockValue}<br/>Projected Stock Price In Two Weeks: {modelPrediction}")

        OverallRecommendation.append(recommendation)



    if bestCompanyRecommendationProfit < 0:
        bestCompany = "None of the companies should be bought!"

    # fill out the scores
    for company in newCompanyList:
        print(stockDataForGraphing[company])
        HistoricalDataOverTwitterSentiment.append(stockDataForGraphing[company])
        # OverallRecommendation.append("Short")

        # for tweets
        search_words = "#" + company
        date_since = date.today()
        tweets = []
        listOfTweets = []
        most_recent_id = ''
        while ((len(listOfTweets) <= 0) and (date.today() - date_since < timedelta(days=14))):
            tweets = tw.Cursor(api.search_tweets,
                            q=search_words,
                            lang="en",
                            since=date_since, until=(date_since + timedelta(days=1))).items(1)
            date_since = date_since - timedelta(days=1)
            listOfTweets = list(tweets)
        try:
            most_recent_id = listOfTweets[0].id
            TweetsToDisplay.append(f'https://twitter.com/noitatS_rehtaeW/status/{most_recent_id}')
        except:
            TweetsToDisplay.append('https://twitter.com/Official_Temoc/status/1445794843318386691')
        
    placeHolderText = userInput
    return render_template("analyze.html",
        placeHolderText=placeHolderText, 
        userInput = userInput,
        companyList=newCompanyList,
        OverallSentiment=OverallSentiment, 
        HistoricalDataOverTwitterSentiment=HistoricalDataOverTwitterSentiment,
        VolatilityScore=VolatilityScore,
        OverallRecommendation=OverallRecommendation,
        TweetsToDisplay=TweetsToDisplay,
        BestRecommendation=bestCompany)

if __name__=="__main__":
    app.run(debug=True)
