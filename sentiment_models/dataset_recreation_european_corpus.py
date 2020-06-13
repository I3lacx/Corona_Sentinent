import csv
import math

from tweepy import TweepError

from sentiment_models.get_tweets_for_corona_dataset import get_api_and_auth

DATA_INPUT = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment.csv"
DATA_OUTPUT = "DATA/European_twitter_sentiment_german/German_Twitter_sentiment_filtered_with_text.csv"

# keys of input data as variables for more efficient coding
TweetID = "TweetID"
HandLabel = "HandLabel"
AnnotatorID = "AnnotatorID"
Neutral = "Neutral"
Positive = "Positive"
Negative = "Negative"
annotator_ids = "annotator_ids"

pos = "pos"
neg = "neg"
neut = "neut"


def get_text_for_tweets(api, tweets):
    deleted_tweets = []
    tweets_mit_text = []
    for i in range(math.ceil(len(tweets)/100+1)):
        # try:
        currently_deleted_tweets = []
        last_id = min((i+1)*100, len(tweets))
        current_tweets = tweets[i*100:last_id]
        current_tweet_ids = [tweet["tweet_id"] for tweet in current_tweets]
        if not len(current_tweet_ids) == 0:
            tweet_texts = api.statuses_lookup(current_tweet_ids, map_=True, tweet_mode="extended")
            tweet_text_dict = {tweet.id_str: tweet.full_text.replace("\n", " ") for tweet in tweet_texts if
                               hasattr(tweet, "full_text")}
            for j in range(len(current_tweets)):
                current_tweet_id = current_tweets[j]["tweet_id"]
                if not current_tweet_id in tweet_text_dict:
                    deleted_tweets.append(current_tweets[j])
                    currently_deleted_tweets.append(current_tweets[j])
                else:
                    current_tweets[j]["text"] = tweet_text_dict[current_tweet_id]
            current_valid_tweets = [tweet for tweet in current_tweets if not tweet in currently_deleted_tweets]
            tweets_mit_text += current_tweets
            save_tweets_partially(current_valid_tweets, DATA_OUTPUT)
        #     fetched_tweet = api.get_status(tweet["tweet_id"], tweet_mode="extended")
        #     tweet["text"] = fetched_tweet.full_text.replace("\n", " ")
        #     tweets_mit_text.append(tweet)
        # except TweepError:
        #     deleted_tweets.append(tweet)
    for tweet in deleted_tweets:
        tweets_mit_text.remove(tweet)
    return tweets_mit_text


def read_file(data_path):
    """
    Read the csv-file downloaded from https://www.clarin.si/repository/xmlui/handle/11356/1054 into a list of dicts
    :param data_path: path to the csv-file
    :return: list of dicts (keys: "TweetID", "HandLabel", "AnnotatorID")
    """
    with open(data_path, "r") as infile:
        csv_reader = csv.DictReader(infile, delimiter=",")
        input_data = list(csv_reader)
    return input_data


def count_labels(raw_input_data):
    """
    Count how often which label is given for the tweets
    :param raw_input_data: list of dicts (keys: "TweetID", "HandLabel", "AnnotatorID")
    :return: dict (keys: tweet-ids) of dicts (keys: "Positive"(int), "Negative"(int), "Neutral"(int), "annotator_ids")
    """
    tweet_dict = {}
    tweets_for_calculating_inter_annotator_agreement = 0
    for tweet in raw_input_data:
        current_tweet_id = tweet[TweetID]
        if not current_tweet_id in tweet_dict:
            tweet_dict[current_tweet_id] = {Positive: 0, Neutral: 0, Negative: 0, annotator_ids: []}
        if not tweet[AnnotatorID] in tweet_dict[current_tweet_id][annotator_ids]:
            tweet_dict[current_tweet_id][tweet[HandLabel]] += 1
            tweet_dict[current_tweet_id][annotator_ids] += [tweet[AnnotatorID]]
        else:
            tweets_for_calculating_inter_annotator_agreement += 1
    print("tweets_for_calculating_inter_annotator_agreement {}".format(tweets_for_calculating_inter_annotator_agreement))
    return tweet_dict


def filter_tweets(unfiltered_tweet_dict):
    """
    Filter Tweets where at least two third of the annotators decided for the same label.
    :param unfiltered_tweet_dict: dict (keys: tweet-ids) of dicts (keys: "Positive"(int), "Negative"(int), "Neutral"(int), "annotator_ids")
    :return: dict (keys: tweet-ids, values: label ("pos", "neut", "neg"))
    """
    filtered_tweet_dict = {}
    amount_of_tweets_labeled_once = 0
    for tweet_id, tweet in unfiltered_tweet_dict.items():
        overall_count = tweet[Positive] + tweet[Neutral] + tweet[Negative]
        two_third_of_overall = overall_count*2/3
        count_tuples = [(pos, tweet[Positive]), (neut, tweet[Neutral]), (neg, tweet[Negative])]
        label = next((tup[0] for tup in count_tuples if tup[1] >= two_third_of_overall), None)
        if label:
            if two_third_of_overall < 1:
                amount_of_tweets_labeled_once += 1
            filtered_tweet_dict[tweet_id] = label
    print("Amount of tweets annotated only once: {} (at the moment they are included)".format(
        amount_of_tweets_labeled_once))
    #  find out if there are any tweets annotated by more than two annotators (there are none)
    #  any(i for i in [len(tweet["annotator_ids"]) for tweet in unfiltered_tweet_dict.values()] if i  > 2)
    #  find out how many tweets were annotated by at least two annotators (4 539 of 97 948)
    #  len(unfiltered_tweet_dict)-amount_of_tweets_labeled_once
    #  find out how many of those tweets were labelled consistently by the two annotators (2 254 of 4 539):
    #  len(filtered_tweet_dict)-amount_of_tweets_labeled_once
    return filtered_tweet_dict


def read_and_filter_input(data_path):
    """
    Read and filter the input data
    :param data_path: path to the csv-file
    :return: dict (keys: tweet-ids, values: label ("pos", "neut", "neg"))
    """
    raw_input_data = read_file(data_path)
    unfiltered_tweet_dict = count_labels(raw_input_data)
    filtered_tweets = filter_tweets(unfiltered_tweet_dict)
    tweets_with_text = get_tweet_texts(filtered_tweets)
    return tweets_with_text


def get_tweet_texts(filtered_tweets):
    """
    Get tweet texts for the already filtered tweets
    :param filtered_tweets: list of dicts (keys: "tweet_id", "label", "text")
    :return:
    """
    filtered_tweets = {tweet_id: filtered_tweets[tweet_id] for tweet_id in list(filtered_tweets)[50000:]}
    api = get_api_and_auth()
    tweet_ids = [{"tweet_id": tweet_id, "label": filtered_tweets[tweet_id]} for tweet_id in filtered_tweets]
    tweets_with_text = get_text_for_tweets(api, tweet_ids)
    return tweets_with_text


def save_tweets(tweets, outfile_path):
    """
    Save the tweets in the outfile
    :param tweets: list of dicts (keys: "tweet_id", "label", "text")
    :param outfile_path: path for saving the tweets
    """
    with open(outfile_path, "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=tweets[0].keys())
        writer.writeheader()
        for row in tweets:
            writer.writerow(row)


def save_tweets_partially(tweets, outfile_path):
    """
    Save the tweets in the outfile
    :param tweets: list of dicts (keys: "tweet_id", "label", "text")
    :param outfile_path: path for saving the tweets
    """
    with open(outfile_path, "a") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=tweets[0].keys())
        for row in tweets:
            writer.writerow(row)


def main():
    tweets = read_and_filter_input(DATA_INPUT)
    # save_tweets(tweets, DATA_OUTPUT)
    print(tweets[:50])


if __name__ == "__main__":
    main()
