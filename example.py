"""
Example query on how to use and call the analyzer
"""


from analyzer import Crawler


config = {
"user_auth": False,
"get_user": {
	"good_user": True, # mandatory
	"search_type": "recent_user", # 'recent_user', 'recent_retweeted_user'
	"num_users": 5 # mandatory
	# optional max_seraches different from tweets?
},

# TODO location from a list to select
# Create query call subgroup or so
"location": "49.8728,8.6511,100km",
"query": ['corona'],
"max_searches": 100,
"num_results": 10,
"rate_limit": True,
"return_iteratior": False
}

obj = Crawler(config)

tweets = obj.get_tweets()
users = obj.get_users()
for tweet in tweets:
	print(tweet.text)
