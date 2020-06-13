"""Optimize label boundaries for Sentiment calculat#rion with SentiWS and vaderSentiment."""
import json

from sentiment_models.vader_with_sentiws.lib_sentiment_sentiws import SentimentIntensityAnalyzerSentiWS
from sentiment_models.train_test_dev_split_european_corpus import read_data
from sentiment_models.vader_translated.sentiment_vader import optimize_label_boundaries

ANALYZER = SentimentIntensityAnalyzerSentiWS()
INPUT_PATH = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed.csv"
VALUE_PATH = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed_sentiws_values.json"
BELOW_NEGATIVE = -0.1
ABOVE_POSITIVE = 0.1


def compute_sentiment_label(tweet):
    value = compute_sentiment(tweet)
    if value < BELOW_NEGATIVE:
        label = "neg"
    elif value > ABOVE_POSITIVE:
        label = "pos"
    else:
        label = "neut"
    tweet["sentiws_label"] = label
    return value


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
        tweet["sentiws_value"] = compute_sentiment(tweet)
    with open(file, "w") as json_file:
        json.dump(input_data, json_file)


def test_sentiws_vader_for_tweets(file):
    with open(file,
              "r") as json_file:
        input_data = json.load(json_file)
    right_guesses = 0
    for tweet in input_data:
        value = tweet["sentiws_value"]
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
    optimize_label_boundaries(VALUE_PATH, "sentiws_value")


if __name__ == "__main__":
    main()
