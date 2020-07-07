# -*- coding: utf-8 -*-
"""Optimize label boundaries for Sentiment calculation with translated vaderSentiment."""
import json

from sentiment_models.train_test_dev_split_european_corpus import read_data
from sentiment_models.GerVADER.vaderSentimentGER \
    import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

ANALYZER = SentimentIntensityAnalyzer()

INPUT_PATH = "sentiment_models/DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed.csv"
VALUE_PATH = "sentiment_models/DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed_gervader_values.json"
BELOW_NEGATIVE = -0.33
ABOVE_POSITIVE = 0.46


def compute_sentiment_label(tweet):
    value = compute_sentiment(tweet)
    if value < BELOW_NEGATIVE:
        label = "neg"
    elif value > ABOVE_POSITIVE:
        label = "pos"
    else:
        label = "neut"
    tweet["vader_label"] = label
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
        tweet["gervader_value"] = compute_sentiment(tweet)
    with open(file, "w") as json_file:
        json.dump(input_data, json_file)


def read_data_with_values(file):
    with open(
            file,
            "r") as json_file:
        input_data = json.load(json_file)
    return input_data


def test_vader_translated_for_tweets():
    input_data = read_data_with_values(VALUE_PATH)
    right_guesses = 0
    for tweet in input_data:
        value = tweet["gervader_value"]
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


def optimize_label_boundaries(file, sentiment_key):
    input_data = read_data_with_values(file)
    label2values = {"pos": [], "neg": [], "neut": []}
    for tweet in input_data:
        value = tweet[sentiment_key]
        correct_label = tweet["label"]
        label2values[correct_label].append(round(value, 2))
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # ax.plot(sorted(label2values["pos"]), color="green")
    # ax.plot(sorted(label2values["neg"]), color="red")
    # ax.plot(sorted(label2values["neut"]), color="black")
    # plt.savefig("sentiment_vader_labels.png")
    # plt.show()
    # plt.hist(label2values["pos"], color="green", bins=int(len(label2values["pos"]) / 20))
    # plt.show()
    # plt.hist(label2values["neg"], color="red", bins=int(len(label2values["pos"]) / 20))
    # plt.show()
    # plt.hist(label2values["neut"], color="black", bins=int(len(label2values["pos"]) / 20))
    # plt.show()
    best_pos_boundary = 0
    best_neg_boundary = 0
    best_correct_amount = 0
    for i in range(0, 100):
        current_pos_boundary = i / 100
        for j in range(0, 100):
            current_neg_boundary = - j/100
            correct = len([x for x in label2values["pos"] if x > current_pos_boundary]) + \
                      len([x for x in label2values["neg"] if x < current_neg_boundary]) + \
                      len([x for x in label2values["neut"] if current_neg_boundary <= x <= current_pos_boundary])
            if correct > best_correct_amount:
                best_pos_boundary = current_pos_boundary
                best_neg_boundary = current_neg_boundary
                best_correct_amount = correct
    accuracy = best_correct_amount / len(input_data)
    print("The best boundaries were {}, {} with {} correct classifications and an accuracy of {:.4f}".
          format(best_neg_boundary, best_pos_boundary, best_correct_amount, accuracy))



def main():
    calculate_sentiws_vader_for_tweets(VALUE_PATH)
    accuracy = test_vader_translated_for_tweets()
    print("accuracy was {} ".format(accuracy))
    optimize_label_boundaries(VALUE_PATH, "gervader_value")


if __name__ == "__main__":
    main()
