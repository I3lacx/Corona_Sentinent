# Must have imports
import math

import helper
from analyzer import Analyzer, group_tweets_by_calendar_week
from crawler import Crawler
from plotter import Plotter
from model import Vader, TrainedSentimentModel, TextBlob

# Extra imports
import datetime
import os
import json

SCAN_ID = "all"

config_dict = {
	"user_auth": False,  # autheticate as user or application
	"search": {
		"location": "darmstadt",  # based on helper.GEOCODES dictionary
		"radius": 100,  # optional default to 100
		"query": ['der, die, das'],  # query for searching (str array), either query or location has to be not empty
		"max_searches": 5000,  # Default: 1000 max amount of searches
		"num_results": 5000,  # number of results with defined filter options
		"rate_limit": True,  # Default True: to turn off rate limit prints
		"filter": {  # Filter applies to search
			"not_reply": True,  # Filters for not replies when true, does nothing when false
			"not_retweet": True,  # Filters for not retweets when true, does nothing when false
			"until": datetime.datetime(2020, 3, 1),  # None or datetime (e.g. datetime.datetime(2020, 5, 20))
		}
	},
	"get_user": {  # Optional, only when querying for users
		"good_user": True,  # mandatory
		"search_type": "recent_user",  # 'recent_user', 'recent_retweeted_user'
		"num_users": 30,  # mandatory
		"unique_ids": True,  # If true will remember user ids in session
	},
	"analyze_sentiment": {
		"pos_boundary": 0.8,  # boundary for classifying tweets as "extremely" positive
		"neg_boundary": 0.7,  # boundary for classifying tweets as "extremely" negative
		"users_dir": "saved_data/full_scan_both/results/{}/".format(SCAN_ID)  # there the sentiment analysis files are stored
	},
	"plot": {
		"title": "Testing",
		"group_by": 1,  # number of days of each group in the histogramm
		"end_date": datetime.datetime(2020, 6, 25, 23, 59),  # last day included in the analysis
		"start_date": datetime.datetime(2020, 6, 1)  # first day included in the analysis
	},
	# Full search not tested and should only be used with caution!
	"full_search": {
		"query": "#Corona lang:de",  # the query used for full search
		"env_name": "dev",  # your premium environment name
		"fromDate": "2020" + "01" + "15" + "1200",  # Format: YYYYMMDDHHmm
		"toDate": "2020" + "06" + "01" + "1200"
	},
	# A full scan over 3 areas each hour, should run continuous
	"full_scan": {
		"active": True,
		"path": "saved_data/full_scan/",
		"locations": ["scan_1", "scan_2", "scan_3"],  # All locations used by the scan
	}
}


def analyze_part(analysation_dicts, begin_id, end_id, user_filenames):
	user_filenames = user_filenames[begin_id: end_id]
	user_tweets = [crawler.load_tweet_for_analysation(filename) for filename in user_filenames]
	per_user_analysation = analyzer.analyze_sentiment_user_based(user_tweets)
	analysation_dicts += per_user_analysation
	print("Analyzed users {} to {}".format(begin_id, end_id - 1))
	return analysation_dicts


def change_config(config, group_by, begin_day, begin_month, end_day, end_month):
	config["plot"] = {
		"title": "Testing",
		"group_by": group_by,  # number of days of each group in the histogramm
		"end_date": datetime.datetime(2020, end_month, end_day, 23, 59),  # last day included in the analysis
		"start_date": datetime.datetime(2020, begin_month, begin_day)  # first day included in the analysis
	}
	return config


def reanalyze(analysation_dicts, config, group_by, start_day, start_month, end_day, end_month):
	analyzer.config = change_config(config, group_by, start_day, start_month, end_day, end_month)
	analysation = analyzer.summarize_user_sentiments(analysation_dicts)
	analyzer.plot_sentiment(analysation)



config = helper.init_config(config_dict)
crawler = Crawler(config)
trained_model = TrainedSentimentModel()
analyzer = Analyzer(config, trained_model)
analysation_dicts = []
if SCAN_ID == "all":
	all_user_ids = set()
	user_filenames = []
	for i in range(0, 3):
		users_dir = "saved_data/full_scan_both/tweets/{}/".format(i)
		current_user_ids = [user_id for user_id in sorted(os.listdir(users_dir)) if not user_id in all_user_ids]
		all_user_ids.update(current_user_ids)
		current_user_filenames = [users_dir + filename for filename in current_user_ids if
								  os.path.isfile(users_dir + filename)]
		user_filenames += current_user_filenames
else:
	users_dir = "saved_data/full_scan_both/tweets/{}/".format(SCAN_ID)
	user_filenames = [users_dir + filename for filename in sorted(os.listdir(users_dir)) if
					  os.path.isfile(users_dir + filename)]
nr_batches = math.ceil(len(user_filenames)/300)
for i in range(0, nr_batches):
	begin_id = i * 300
	end_id = min((i + 1) * 300, len(user_filenames))
	if begin_id >= end_id:
		break
	analysation_dicts = analyze_part(analysation_dicts, begin_id, end_id, user_filenames)
print("Summarizing the results...")
analysation = analyzer.summarize_user_sentiments(analysation_dicts)
analyzer.plot_sentiment(analysation)

print("Done.")
