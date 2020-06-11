"""
Example query on how to use and call the analyzer
"""
import helper
from analyzer import Analyzer
from crawler import Crawler
from plotter import Plotter

config = {
	"user_auth": False,
	"get_user": {
		"good_user": False, # mandatory
		"search_type": "recent_user", # 'recent_user', 'recent_retweeted_user'
		"num_users": 5, # mandatory
		# optional max_seraches different from tweets?
		"max_timeline_searches": 100
	},

	# TODO location from a list to select
	# Create query 'call' subgroup or so
	"location": helper.get_location(helper.GEOCODES["darmstadt"]),
	"query": ['corona'],
	"max_searches": 100,
	"num_results": 10,
	"rate_limit": True,
	"return_iteratior": False,
	"plot": {
		"title": "Testing",
	}
}

craw = Crawler(config)
anal = Analyzer(config)
plot = Plotter(config)

tweets = craw.get_tweets()
users = craw.get_users()
timeline = craw.get_timeline(users[0])
dicts = anal.analyze_timeline(timeline)
plot.plot_dict(dicts["counts"])


