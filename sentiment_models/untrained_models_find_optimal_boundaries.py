import matplotlib.pyplot as plt
from model import GerVADER, SpacySentiWS, TextBlob, VaderSentiWS, Vader
from sentiment_models.train_test_dev_split_european_corpus import read_data
INPUT_PATH = "sentiment_models/DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed.csv"

models = [GerVADER(), SpacySentiWS(), TextBlob(), VaderSentiWS(), Vader()]

if __name__ == "__main__":
    input_data = read_data(INPUT_PATH)
    tweet_texts = [tweet["text"] for tweet in input_data]
    for model in models:
        boundary = 0
        precisions = {"pos": [], "neg": []}
        classified_amounts = {"pos": [], "neg": []}
        boundaries = []
        amount_non_neutral_tweets = sum(1 for tweet in input_data if not tweet["label"] == "neut")
        polarities = model.get_polarity(tweet_texts)
        for boundary in range(0, 100):
            boundary = boundary / 100
            correctly_classified = {"pos": 0, "neg": 0}
            wrongly_classified = {"pos": 0, "neg": 0}
            for current_polarity, tweet in zip(polarities, input_data):
                label = "neg" if current_polarity < - boundary else "pos" if current_polarity > boundary else "neut"
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
                    classified_amounts[label].append(amount_classified[label] / amount_non_neutral_tweets)
            boundaries.append(boundary)
        # part below partially taken from https://matplotlib.org/gallery/api/two_scales.html
        fig, ax1 = plt.subplots()
        ax1.set_title(model.name)
        ax1.set_xlabel('boundary')
        ax1.set_ylabel('precision', color="black")
        ax1.plot(boundaries, precisions["pos"], color="darkgreen")
        ax1.plot(boundaries, precisions["neg"], color="darkred")
        ax1.tick_params(axis='y', labelcolor="black")
        ax2 = ax1.twinx()
        color = 'tab:blue'
        ax2.set_ylabel('percentage of pos/neg tweets classified as non-neutral', color="grey")
        ax2.plot(boundaries, classified_amounts["pos"], color="lightgreen")
        ax2.plot(boundaries, classified_amounts["neg"], color="lightcoral")
        ax2.tick_params(axis='y', labelcolor="grey")
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()
