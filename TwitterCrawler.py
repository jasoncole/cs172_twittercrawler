from os import dup
import tweepy
import sys
import json
import unittest
import time
import math
import requests
import re
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from tweepy import OAuthHandler
from tweepy import Stream
# -*- coding: utf-8 -*-


def getHTMLdocument(url):

    # request for HTML document of given url
    response = requests.get(url)

    # response will be provided in JSON format
    return response.text

api_key = 'uNhmWjr1QK116aztmecCIMsjN'
api_secret = 'VfSxTSauYGxiJUln4fBQ0Kv5iV7i5VvlYNUEVb9BO9DdZmjSUu'
access_token = '772860187686219776-CjW9keqEBipBm9SKeJQIKP2gHiDBk7f'
access_secret = 'Tg5EZhwmjpIJAQk8yE4SoknSBgzCUPDA1o1jsvcYmKw8u'

try:
    auth = tweepy.OAuthHandler(api_key, api_secret)
    #auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
except Exception as e:
    if(e == 420 or e == 401):
        wait = 100
        print("waiting for ", wait, " seconds")
        time.sleep(wait)
        print("continuing")


dupDictionary = {}
maxTweets = 2000000
# input any starting seed (singular user_ID)
followerCrawlQueue = [sys.argv[1]]
print("Starting User_ID Seed is ", sys.argv[1])
tweetCounter = 0
followerCounter = 0
fileCounter = 0
cntFlg = False

# ONLY USE TO RESUME AT LATEST USER ID IF UNKNOWN SYSTEM ERROR
# insert the value of "next: <ID>" that is printed to your terminal
emergencyResume = []  # KEEP EMPTY UNLESS USING

# opens html file
dirPath = "TwitterCrawlerData"
dirPath += str(fileCounter)
dirPath += '.html'
f = open(dirPath, 'a')

while tweetCounter < maxTweets or cntFlg == True:

    # prints to terminal for updates
    print("File ", fileCounter, ": ", (f.tell()/10485760), "%")

    if(fileCounter >= 200):  # executes when 2gb worth of 10mb files have been filled
        print("completed 2g of tweet data")
        cntFlg = True  # stops the while loop and exits
    tmpcnt = 0

    for user in api.get_follower_ids(user_id=followerCrawlQueue[0])[:50]:

        # checks for dups before adding it to followercrawlqueue array
        dupDictionary[user] = dupDictionary.get(user, 0) + 1
        if dupDictionary[user] > 1:
            continue

        # skips protected/banned/users that dont tweet
        if len(api.lookup_users(user_id={followerCrawlQueue[0]})) == 0:
            continue

        # adds the active user ID to the crawl list
        followerCrawlQueue.append(user)
        followerCounter += 1

    # ONLY RUNS IF EMERGENCYRESUME IS POPULATED (to resume where you left off incase of unknown error)
    if len(emergencyResume) == 1:
        if followerCrawlQueue[0] != emergencyResume:
            followerCrawlQueue.pop(0)
            continue
        else:
            emergencyResume.pop(0)
            print("***RESUMING WHERE LAST STOPPED***")

        # crawl followerCrawlQueue[0]
    try:
        # crawls only the most recent 100 tweets of each user ID
        for status in tweepy.Cursor(api.user_timeline, user_id=followerCrawlQueue[0]).items(100):
            outputStr = ""  # empty string variable to add each line of data
            tweetCounter += 1

            # get current user_ID's twitter username
            outputStr += str(("UserName: " +
                             str(status.user.name)).encode('ascii', 'ignore'))[2:-1]

            # get current user_ID's twitter handle (their @)
            outputStr += str((" ScreenName: " +
                              str(status.user.screen_name)).encode('ascii', 'ignore'))[2:-1]

            # get current user_ID's ID
            outputStr += str((" ID: " +
                              str(status.user.id)).encode('ascii', 'ignore'))[2:-1]

            # get current tweet's date and time created
            outputStr += str((" DateTweeted: " +
                              str(status.created_at)).encode('ascii', 'ignore'))[2:-1]

            # get current tweet's location if available (can be turned off)
            outputStr += str((" Location: " +
                              str(status.user.location)).encode('ascii', 'ignore'))[2:-1]

            # get current tweet's coordinates if available (can be turned off)
            outputStr += str((" Coordinates: " +
                              str(status.coordinates)).encode('ascii', 'ignore'))[2:-1]

            # get current tweet's favorites count
            outputStr += str((" Favorites: " +
                              str(status.favorite_count)).encode('ascii', 'ignore'))[2:-1]

            # get current tweet's retweet count
            outputStr += str((" Retweets: " +
                              str(status.retweet_count)).encode('ascii', 'ignore'))[2:-1]

            # get current tweet's text (the actual tweet)
            outputStr += str((" Text: " + str(status.text)
                              ).encode('ascii', 'ignore'))[2:-1]
            outputStr += str(" URL: ")
            try:
                # gets the url in the tweet IF there is a url
                outputStr += str(status.entities["urls"][0]["expanded_url"])
                urltoScrape = str(status.entities["urls"][0]["expanded_url"])

                # url -> html doc using beautifulSoup library
                html_document = getHTMLdocument(urltoScrape)
                soup = BeautifulSoup(html_document, 'html.parser')

                # gets title of html document of link IF a title is available
                outputStr += " Title: "
                if len(str(soup.head.title.text)) == 0:
                    outputStr += "none"
                    outputStr += "\n"
                    f.write(outputStr)
                    continue
                else:
                    outputStr += str(soup.head.title.text)
            except:
                outputStr += "none"
                outputStr += "\n"
                f.write(outputStr)
                continue

            outputStr += "\n"
            # writes to the .html file
            f.write(outputStr)

            if(f.tell() >= 10485760):  # checks if the current file is greater than 10mb
                print("End of File ", fileCounter)
                f.close()
                fileCounter += 1
                dirPath = "TwitterCrawlerData"
                dirPath += str(fileCounter)
                dirPath += '.html'
                f = open(dirPath, 'a')  # opens next file
    except Exception as e:
        if(e == 401):
            pass
    print("next: ", followerCrawlQueue[1])
    followerCrawlQueue.pop(0)

f.close()
