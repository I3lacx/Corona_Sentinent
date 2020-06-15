"""
Example query on how to use and call the analyzer
"""
import helper
from analyzer import Analyzer
from crawler import Crawler
from plotter import Plotter
import model

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
	"location": "darmstadt",	# based on helper.GEOCODES dictionary
	"radius": 100, # optional default to 100
	"query": ['corona'],
	"max_searches": 100,
	"num_results": 100,
	"rate_limit": True,
	"return_iteratior": False,
	"plot": {
		"title": "Testing",
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


