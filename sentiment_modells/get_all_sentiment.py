from sentiws import sentiment_sentiws
from spacy_sentiws_test import test_spacy_sentiws
from text_blob_sentiment import test_textblob
from train_test_dev_split_european_corpus import read_data
from vader_translated import sentiment_vader
from sklearn.metrics import classification_report, confusion_matrix

INPUT_PATH = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_dev_preprocessed.csv"


def get_all_sentiment_for_tweet(tweet_text, label=""):
    tweet_dict = {"text": tweet_text, "label": label}
    sentiment_dict = {
                  "sentiment_sentiws": sentiment_sentiws.compute_sentiment_label(tweet_dict),
                  "sentiment_spacy": test_spacy_sentiws.compute_sentiment_label(tweet_dict),
                  "sentiment_textblob": test_textblob.compute_sentiment_label(tweet_dict),
                  "sentiment_vader": sentiment_vader.compute_sentiment_label(tweet_dict)
                  }
    tweet_dict.update(sentiment_dict)
    return tweet_dict


def get_classification_reports():
    input_data = read_data(INPUT_PATH)
    tweets_with_sentiment = []
    for tweet in input_data:
        sentiment_dict = get_all_sentiment_for_tweet(tweet["text"], tweet["label"])
        tweets_with_sentiment.append(sentiment_dict)
    true_labels = [tweet["label"] for tweet in tweets_with_sentiment]
    for key in tweets_with_sentiment[0]:
        if key.endswith("_label"):
            print("Information for {} :".format(key))
            predicted_labels = [tweet[key] for tweet in tweets_with_sentiment]
            print(classification_report(true_labels, predicted_labels))
            conf_matrix = confusion_matrix(true_labels, predicted_labels)
            sums = ["sums"]
            for i in range(3):
                current_sum = sum([conf_matrix[j][i] for j in range(len(conf_matrix))])
                sums.append(current_sum)
            conf_matrix_string = " \n | ".join([" | ".join([str(i) for i in inner_list]+[str(sum(inner_list))]) for inner_list in conf_matrix])
            conf_matrix_string += " \n " + " | ".join([str(i) for i in sums])
            print("| neg | neut | pos | sum | \n " + conf_matrix_string)


# get_classification_reports()
print(get_all_sentiment_for_tweet("Das ist ein Test-Tweet."))
