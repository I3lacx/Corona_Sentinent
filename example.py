"""
Example query on how to use and call the analyzer
"""
import helper
from analyzer import Analyzer
from crawler import Crawler
from plotter import Plotter
import model

# TODO get it to work!

config = {
	"user_auth": False, # autheticate as user or application
	"auth_path": "/home/maxi/Documents/UNI/Ethics/Project/repo/Corona_Sentinent/", # path to auth
    "search": {
        "location": "darmstadt", # based on helper.GEOCODES dictionary
        "radius": 100, # optional default to 100
        "query": ['die', 'der', 'das'], # query for searching (str array), either query or location has to be not empty
        "max_searches": 5000, # Default: 1000 max amount of searches 
        "num_results": 5000, # number of results with defined filter options
        "rate_limit": False,  # Default True: to turn off rate limit prints
        "filter": { # Filter applies to search
            "not_reply": True, # Filters for not replies when true, does nothing when false
            "not_retweet": True, # Filters for not retweets when true, does nothing when false
            "until": datetime.datetime(2020, 3, 1), # None or datetime (e.g. datetime.datetime(2020, 5, 20))
        }
    },
	"get_user": { # Optional, only when querying for users
		"good_user": True, # mandatory
		"search_type": "recent_user", # 'recent_user', 'recent_retweeted_user'
		"num_users": 40, # mandatory
        "unique_ids": True, # If true will remember user ids in session
	},
	"plot": {
		"title": "Testing",
	},
    # Full search not fully tested and should only be used with caution!
    # As there is only limited amount of requests!
    "full_search": {
        "query": "#Corona lang:de", # the query used for full search
        "env_name": "dev", # your premium environment name
        "fromDate": "2020" + "01" + "15" + "1200", # Format: YYYYMMDDHHmm
        "toDate": "2020" + "06" + "01" + "1200"
    },
    # A full scan over 3 areas each hour, should run continuous
    "full_scan": {
        "active": False,
        "path": "/home/maxi/Documents/UNI/Ethics/Project/repo/Corona_Sentinent/saved_data/full_scan/",
        "locations": ["scan_1", "scan_2", "scan_3"], # All locations used by the scan
    }
}


config = helper.init_config(config)

modl = TextBlob()
craw = Crawler(config)
anal = Analyzer(config, modl)
plot = Plotter(config)

users = craw.get_users()
timeline = craw.get_timeline(users[0])

tweets = craw.get_tweets()
sentis = anal.analyze_sentiment(timeline)
plot.simple_hist(sentis)

exit()


dicts = anal.analyze_timeline(timeline)
plot.plot_dict(dicts["counts"])


