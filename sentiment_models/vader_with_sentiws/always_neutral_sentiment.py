"""Compute Sentiment with SentiWS and vaderSentiment."""
import json

from sentiws.lib_sentiment_sentiws import SentimentIntensityAnalyzer
from train_test_dev_split_european_corpus import read_data
from vader_translated.sentiment_vader import optimize_label_boundaries

ANALYZER = SentimentIntensityAnalyzer()
INPUT_PATH = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed.csv"
VALUE_PATH = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed_neutral_values.json"
BELOW_NEGATIVE = -0.1
ABOVE_POSITIVE = 0.1


def compute_sentiment(tweet):
    """Calculate the sentiment of the given argument.

     Modify the arguments and add the entry "sentiment_vader"

    Arguments:
        tweet: tweet-dict

    Returns:
        values (list): value that has been calculated

    Raises:
        TypeError, if content of argument is not of type
                       Classes.Argument

    """

    plaintext = tweet["text"]
    # save plaintext
    values = ANALYZER.polarity_scores(plaintext)
    value = values["compound"]
    # compute polarity-scores
    return value


def calculate_sentiws_vader_for_tweets(file):
    input_data = read_data(INPUT_PATH)
    for tweet in input_data:
        tweet["neutral_value"] = 0
    with open(file, "w") as json_file:
        json.dump(input_data, json_file)


def test_sentiws_vader_for_tweets(file):
    with open(file,
              "r") as json_file:
        input_data = json.load(json_file)
    right_guesses = 0
    for tweet in input_data:
        value = tweet["neutral_value"]
        if value < BELOW_NEGATIVE:
            label = "neg"
        elif value > ABOVE_POSITIVE:
            label = "pos"
        else:
            label = "neut"

        if label == tweet["label"]:
            right_guesses += 1
    accuracy = right_guesses / len(input_data)
    return accuracy


def main():
    calculate_sentiws_vader_for_tweets(VALUE_PATH)
    accuracy = test_sentiws_vader_for_tweets(VALUE_PATH)
    print("accuracy was {} ".format(accuracy))
    # optimize_label_boundaries(VALUE_PATH, "sentiws_value")


if __name__ == "__main__":
    main()
