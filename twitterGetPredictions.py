import os
import tweepy as tw
import pandas as pd
from textblob import TextBlob
from datetime import date, timedelta

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

def getTweetsForSpecificText(search_word):
    search_words = search_word

    date_since = date.today()

    listOfTweets = []
    while(date.today() - date_since < timedelta(days=10)):
        tweets = tw.Cursor(api.search_tweets,
                        q=search_words,
                        lang="en",
                        since=date_since, until=(date_since + timedelta(days=1))).items(3)
        date_since = date_since - timedelta(days=1)

        listOfTweets.append(tweets)
    return listOfTweets

def getPolarity(text):
    return TextBlob(text).subjectivity

def getSentiment(text):
    return TextBlob(text).sentiment

def getSubjectivity(text):
    return TextBlob(text).subjectivity

def isPositiveForSpecificStock(tweets):
    count = 0
    perDayTotalPolarity = 0
    positiveRateList = []
    overallPositiveRate = 0
    perDayCount = 0

    for tweetList in tweets:
        perDayTotalPolarity = 0
        perDayCount = 0
        for tweet in tweetList:
            perDayCount +=1
            text = tweet.text
            polarity = getPolarity(text)
            perDayTotalPolarity += polarity
            overallPositiveRate += polarity
            count+=1
        try:
            positiveRateList.append(perDayTotalPolarity / perDayCount)
        except:
            positiveRateList.append(-1)

    if count == 0:
        return -1, positiveRateList
    overallPositiveRate = overallPositiveRate / count
    return overallPositiveRate, positiveRateList