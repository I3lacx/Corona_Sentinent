import numpy as np
import matplotlib.pyplot as plt
from model import TrainedSentimentModel
from sentiment_models.train_test_dev_split_european_corpus import read_data
INPUT_PATH = "sentiment_models/DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed.csv"


if __name__ == "__main__":
    input_data = read_data(INPUT_PATH)
    tweet_texts = [tweet["text"] for tweet in input_data]
    model = TrainedSentimentModel()
    prob_distributions = model.do_prediction(tweet_texts)
    boundary = 0
    precisions = {"pos": [], "neg": []}
    classified_amounts = {"pos": [], "neg": []}
    boundaries = []
    amount_non_neutral_tweets = sum(1 for tweet in input_data if not tweet["label"] == "neut")
    for boundary in range(33, 100):
        boundary = boundary/100
        correctly_classified = {"pos": 0, "neg": 0}
        wrongly_classified = {"pos": 0, "neg": 0}
        for i, tweet in enumerate(input_data):
            row = [val.item() for val in prob_distributions[i]]
            label = "neg" if row[0] > boundary else "pos" if row[2] > boundary else "neut"
            # label = "pos" if row[2] > boundary else "neg" if row[0] > boundary else "neut"
            if not label == "neut":
                if label == tweet["label"]:
                    correctly_classified[label] += 1
                else:
                    wrongly_classified[label] += 1
        amount_classified = {"pos": 0, "neg": 0}
        precision = {"pos": 0, "neg": 0}
        for label in ["pos", "neg"]:
            amount_classified[label] = (correctly_classified[label] + wrongly_classified[label])
            if amount_classified[label] == 0:
                precisions[label].append(0)
                classified_amounts[label].append(0)
            else:
                precision[label] = correctly_classified[label] / amount_classified[label]
                precisions[label].append(precision[label])
                classified_amounts[label].append(amount_classified[label]/amount_non_neutral_tweets)
        boundaries.append(boundary)
        # print("boundary {:.2f}: precision = {:.4f}, amount classified = {}".format(precision_pos_neg, boundary,
        #                                                                              amount_classified))
    # part below partially taken from https://matplotlib.org/gallery/api/two_scales.html
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('boundary')
    ax1.set_ylabel('precision', color="black")
    ax1.plot(boundaries, precisions["pos"], color="green")
    ax1.plot(boundaries, precisions["neg"], color="red")
    ax1.tick_params(axis='y', labelcolor="black")
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('percentage of pos/neg tweets classified as non-neutral', color="grey")
    ax2.plot(boundaries, classified_amounts["pos"], color="lightgreen")
    ax2.plot(boundaries, classified_amounts["neg"], color="lightcoral")
    ax2.tick_params(axis='y', labelcolor="grey")
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
