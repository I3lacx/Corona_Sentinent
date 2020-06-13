import json

import spacy
from numpy import mean
from spacy_sentiws import spaCySentiWS
from train_test_dev_split_european_corpus import read_data
from vader_translated.sentiment_vader import read_data_with_values, optimize_label_boundaries

nlp = spacy.load('de_core_news_sm')
sentiws = spaCySentiWS(sentiws_path='DATA/SentiWS')
nlp.add_pipe(sentiws)
INPUT_PATH = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed.csv"
VALUE_PATH = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed_spacy_sentiws_values.json"
BELOW_NEGATIVE = -0.37
ABOVE_POSITIVE = 0.13


def compute_sentiment_label(tweet):
    value = compute_sentiment(tweet)
    if value < BELOW_NEGATIVE:
        label = "neg"
    elif value > ABOVE_POSITIVE:
        label = "pos"
    else:
        label = "neut"
    tweet["spacy_label"] = label
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
    values = [token._.sentiws for token in nlp(plaintext) if token._.sentiws is not None]
    if len(values) == 0:
        value = 0
    else:
        value = mean(values)
    # compute polarity-scores
    return value


def calculate_sentiws_vader_for_tweets(file):
    input_data = read_data(INPUT_PATH)
    for tweet in input_data:
        tweet["sentiws_value"] = compute_sentiment(tweet)
    with open(file, "w") as json_file:
        json.dump(input_data, json_file)


def test_sentiws_vader_for_tweets(file):
    input_data = read_data_with_values(file)
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
    # calculate_sentiws_vader_for_tweets(VALUE_PATH)
    accuracy = test_sentiws_vader_for_tweets(VALUE_PATH)
    print("accuracy was {} ".format(accuracy))
    # optimize_label_boundaries(VALUE_PATH, "sentiws_value")


if __name__ == "__main__":
    main()
