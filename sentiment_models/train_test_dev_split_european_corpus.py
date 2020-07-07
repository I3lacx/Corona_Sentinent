import csv
import random
from sentiment_models.dataset_recreation_european_corpus import save_tweets

DATA_INPUT = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_filtered_with_text.csv"
DATA_OUTPUT_PREFIX = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_"


def read_data(path):
    with open(path, "r") as infile:
        reader = csv.DictReader(infile)
        input_data = list(reader)
    return input_data


def shuffle_and_split(input_data):
    random.shuffle(input_data)
    train_end_index = round(0.8*len(input_data))
    dev_end_index = round(0.9*len(input_data))
    train_data = input_data[0:train_end_index]
    dev_data = input_data[train_end_index:dev_end_index]
    test_data = input_data[dev_end_index:]
    for name, data in [("train", train_data), ("dev", dev_data), ("test", test_data)]:
        filename = DATA_OUTPUT_PREFIX + name + ".csv"
        save_tweets(data, filename)


def main():
    input_data = read_data(DATA_INPUT)
    shuffle_and_split(input_data)


if __name__ == "__main__":
    main()
