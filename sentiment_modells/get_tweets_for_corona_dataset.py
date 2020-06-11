import csv

import tweepy
from tweepy import TweepError
from keys import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET


def get_api_and_auth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def read_dataset():
    with open("DATA/corona_tweets_01.csv", "r") as infile:
        csv_reader = csv.DictReader(infile, delimiter=",")
        tweets = [row for row in csv_reader]
    return tweets


def get_text_for_tweets(api, tweets):
    deleted_tweets = []
    tweets_mit_text = []
    for tweet in tweets:
        try:
            fetched_tweet = api.get_status(tweet["tweet_id"], tweet_mode="extended")
            tweet["text"] = fetched_tweet.full_text.replace("\n", " ")
            tweets_mit_text.append(tweet)
        except TweepError as e:
            deleted_tweets.append(tweet)
    for tweet in deleted_tweets:
        tweets.remove(tweet)
    return tweets_mit_text


def write_dataset(tweets):
    with open("DATA/corona_tweets_01_with_text.csv", "w") as outfile:
        csv_writer = csv.DictWriter(outfile, fieldnames=tweets[0].keys())
        csv_writer.writeheader()
        for row in tweets:
            csv_writer.writerow(row)


def main():
    api = get_api_and_auth()
    tweets = read_dataset()
    tweets = get_text_for_tweets(api, tweets)
    write_dataset(tweets)


if __name__ == "__main__":
    main()
