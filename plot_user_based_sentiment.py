# Must have imports
import helper
from analyzer import Analyzer, group_tweets_by_calendar_week
from crawler import Crawler
from plotter import Plotter
from model import Vader, TrainedSentimentModel

# Extra imports
import datetime
import os
import json

config_dict = {
	"user_auth": False, # autheticate as user or application
    "search": {
        "location": "darmstadt", # based on helper.GEOCODES dictionary
        "radius": 100, # optional default to 100
        "query": ['der, die, das'], # query for searching (str array), either query or location has to be not empty
        "max_searches": 5000, # Default: 1000 max amount of searches
        "num_results": 5000, # number of results with defined filter options
        "rate_limit": True,  # Default True: to turn off rate limit prints
        "filter": { # Filter applies to search
            "not_reply": True, # Filters for not replies when true, does nothing when false
            "not_retweet": True, # Filters for not retweets when true, does nothing when false
            "until": datetime.datetime(2020, 3, 1), # None or datetime (e.g. datetime.datetime(2020, 5, 20))
        }
    },
	"get_user": { # Optional, only when querying for users
		"good_user": True, # mandatory
		"search_type": "recent_user", # 'recent_user', 'recent_retweeted_user'
		"num_users": 30, # mandatory
        "unique_ids": True, # If true will remember user ids in session
	},
    "analyze_sentiment": {
      "pos_boundary": 0.8, # boundary for classifying tweets as "extremely" positive
        "neg_boundary": 0.7 # boundary for classifying tweets as "extremely" negative
    },
	"plot": {
		"title": "Testing",
        "group_by": 3, # number of days of each group in the histogramm
        "end_date": datetime.datetime(2020,6,26), # last day included in the analysis
        "start_date": datetime.datetime(2020,3,1) # first day included in the analysis
	},
    # Full search not tested and should only be used with caution!
    "full_search": {
        "query": "#Corona lang:de", # the query used for full search
        "env_name": "dev", # your premium environment name
        "fromDate": "2020" + "01" + "15" + "1200", # Format: YYYYMMDDHHmm
        "toDate": "2020" + "06" + "01" + "1200"
    },
    # A full scan over 3 areas each hour, should run continuous
    "full_scan": {
        "active": True,
        "path": "saved_data/full_scan/",
        "locations": ["scan_1", "scan_2", "scan_3"], # All locations used by the scan
    }
}

config = helper.init_config(config_dict)
crawler = Crawler(config)
trained_model = TrainedSentimentModel()
analyzer = Analyzer(config, trained_model)
users_dir = "saved_data/user_timelines/"
user_filenames = [users_dir+filename for filename in os.listdir(users_dir) if os.path.isfile(users_dir+filename)]
user_tweets = [crawler.load_tweet(filename) for filename in user_filenames]
grouped_tweets = analyzer.analyze_and_plot_sentiment(user_tweets)
print("")
