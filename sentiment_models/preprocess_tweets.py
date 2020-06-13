import csv
import re
import emoji
from sentiment_models.DATA.emoticon2emoji import emoticon2emoji
from sentiment_models.dataset_recreation_european_corpus import save_tweets

INPUT_FILE = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_train.csv"
OUTPUT_FILE = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_train_preprocessed.csv"


def read_input(input_file):
    with open(input_file, "r") as csv_input:
        reader = csv.DictReader(csv_input, delimiter=",")
        input_list = list(reader)
    return input_list


def replace_urls(tweet):
    """Replace all urls with <URL>."""
    tweet = ' '.join(re.sub("(\w+:\/\/\S+)", "<URL>", tweet).split())
    return tweet


def replace_emojis(tweet):
    """Replace emoticons with emojis and then with the corresponding text"""
    tweet = tweet.split()
    tweet = " ".join([emoticon2emoji[token] if token in emoticon2emoji else token for token in tweet])
    tweet = emoji.demojize(tweet)
    return tweet


def replace_mentions(tweet):
    """Replace all username with <@USER>."""
    tweet = ' '.join(re.sub("(@[A-Za-z0-9_]+)", "<@USER>", tweet).split())
    return tweet


def replace_all(tweet_text):
    """Replace emojis, emoticons, mentions and urls in the tweet_text."""
    tweet_text = replace_emojis(tweet_text)
    tweet_text = replace_mentions(tweet_text)
    tweet_text = replace_urls(tweet_text)
    return tweet_text


def main():
    input_list = read_input(INPUT_FILE)
    for tweet in input_list:
        tweet["text"] = replace_all(tweet["text"].lower())
    save_tweets(input_list, OUTPUT_FILE)


if __name__ == "__main__":
    main()
