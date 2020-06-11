"""
Crawler should do all the calls to the API and return the objects directly
The main idea is that the crawler will get called once and with these objects in cash we can
analyze them as many times as we want without querying another time
"""
import helper
import tweepy 
import time
from datetime import datetime


class Crawler:
	""" Crawler class. Using the tweepy api to get tweets specified in the configs """
	
	def __init__(self, config):
		""" Set configs to self values """
		self.config = config
		self.api = self.get_api()
		
	def check_config():
		""" Check some elements in the config """
		raise NotImplementedError
		
	
	def get_api(self):
		return helper.get_api(self.config["user_auth"])
	
	def get_users(self):
		""" returns users objects """
		if self.config["get_user"]["search_type"] == "recent_user":
			users = self.get_recent_users()
		elif self.config["get_user"]["search_type"] == "recent_retweeted_user":
			users = self.get_recent_retweeted_users()
		else:
			raise ValueError(f"Value: {self.config['get_user']['search_type']} not recognized")
		
		if self.config["get_user"]["good_user"]:
			users = self.filter_good_users(users)
		return users
		
	def get_tweet_iterator(self):
		"""
		Main connection to tweepy
		Returns tweets ITERATOR from tweepy Cursor search with specified settings
		from self.config
		Note: Does NOT do a request! Only when iterating over tweets, it will do the requests
		"""
		tweets = tweepy.Cursor(self.api.search, q=self.config["query"],
							 geocode=self.config["geocode"]).items(self.config["max_searches"])
		return tweets
	
	def get_tweets(self):
		"""
		Callable from outside get tweets function
		Will return tweet objects for num_resuts and specific settings
		"""
		tweets_iter = self.get_tweet_iterator()
		
		res_tweets = []
		num_results = 0
		for tweet in tweets_iter:
			if self.check_tweet(tweet):
				num_results += 1
				res_tweets.append(tweet)
				if num_results == self.config["num_results"]:
					break
			
		self.rate_limit()
			
		return res_tweets
	
	def check_tweet(self, tweet):
		"""
		Checks tweet object for settings specified in configs
		returns true if tweet fits the settings
		"""
		# TODO implement
		return True
	
	def get_recent_users(self):
		""" Looks for recent tweets given a query and a geocode
		returns the user objects of these users"""
		users = []

		num_users = self.config["get_user"]["num_users"]
		num_results = 0
		
		tweets_iter = self.get_tweet_iterator()
		for tweet in tweets_iter:
			users.append(tweet.user)
			num_results += 1
			if num_results == num_users:
				break
	
		return users


	def get_recent_retweeted_users(self):
		""" Looks for recent tweets, checks if it's a retweed, if yes, then will return the users objects
		that have been retweeted 
		"""
		user_ids = []
		num_users = self.config["get_user"]["num_queries"]
		num_results = 0
		
		for tweet in self.get_tweet_iterator():
			if helper.is_retweet(tweet):
				user_ids.append(tweet.retweeted_status.user)
				num_results += 1
				if num_results == num_users:
					break
					
		self.rate_limit()
		return user_ids
	
	def filter_good_users(self, users):
		""" Takes a list of user objects and returns only the 'good' user objects """
		# TODO make good user filtering part of get users, such that number of users actually fits
		good_users = []
		for user in users:
			if self.is_good_user(user.id_str):
				good_users.append(user)
		return good_users
		
	def is_good_user(self, user_id, num_searches=100):
		""" Returns true if given user_id is 'good'
		A good user posted under 5 times today and the (recent post is not more than 14 days ago)
		Post is not a retweet or comment
		:param num_searches: default 100, if a person did 100 retweets and the 101 action is a post, 
							 this will not see the user as good. Higher number for more accuracy,
							 but longer runtime and more queries 
		"""
		days_until = []
		for status in tweepy.Cursor(self.api.user_timeline, id=user_id).items(num_searches):
			if not helper.is_retweet(status) and not helper.is_reply(status):
				days_until.append(helper.days_until(status.created_at))
				
		if len(days_until) == 0:
			return False
		if len(days_until) > 5 and np.amax(days_until[0:5]) < 1:
			return False
		if len(days_until) > 0 and days_until[0] > 14:
			return False
		return True
	
	def rate_limit(self):
		""" 
		Prints rate limit informations to the specific request (if active in configs)
		Should be called by every function after calling the api
		"""
		if not self.config["rate_limit"]:
			return
			
		head = self.api.last_response.headers
		print("remaining requests:", head['x-rate-limit-remaining'])
		
		# TODO different mutliply factor for different heads
		print("tweets remaining: ~", int(head['x-rate-limit-remaining']) * 15)
		
		reset = int(head['x-rate-limit-reset'])
		time_until = reset - time.time()
		print("reset at:", datetime.fromtimestamp(reset))
		print(f"reset in: {int(time_until // 60):02d}:{int(time_until % 60):02d}")
	
	def get_timeline_iterator(self, user):
		""" Returns timeline (tweepy iterator) of user object"""
		timeline = tweepy.Cursor(self.api.user_timeline, id=user.id_str).items(self.config["get_user"]["max_timeline_searches"])
		return timeline

	def get_timeline(self, user):
		""" Seraches through timeline of one user and returns tweet objects """
		# TODO filter searches by some configs in timeline
		tweets = []
		
		for tweet in self.get_timeline_iterator(user):
			tweets.append(tweet)
		
		self.rate_limit()
		
		return tweets
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
	
	

		
