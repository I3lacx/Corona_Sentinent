import numpy as np
import helper
import tweepy 
import time
from datetime import datetime
import matplotlib.pyplot as plt


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
		""" returns users """
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
							 geocode=self.config["location"]).items(self.config["max_searches"])
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
			
		if self.config["rate_limit"]:
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
		""" Looks for recent tweets given a query and a location and returns user ids of these users"""
		user_ids = []

		num_users = self.config["get_user"]["num_users"]
		num_results = 0
		
		for tweet in self.get_tweet_iterator():
			user_ids.append(tweet.user.id_str)
			num_results += 1
			if num_results == num_users:
				break
		
		if self.config["rate_limit"]:
			self.rate_limit()
		return user_ids


	def get_recent_retweeted_users(self):
		""" Looks for recent tweets, checks if it's a retweed, if yes, then will return ids of the users
		that have been retweeted 
		Note: Will likely return less users than num_queries!
		"""
		user_ids = []
		num_users = self.config["get_user"]["num_queries"]
		num_results = 0
		
		for tweet in self.get_tweet_iterator():
			if is_retweet(tweet):
				user_ids.append(tweet.retweeted_status.user.id_str)
				num_results += 1
				if num_results == num_users:
					break
		return user_ids
	
	def filter_good_users(self, users):
		""" Takes a list of users and returns only the 'good' users """
		# TODO make good user filtering part of get users, such that number of users actually fits
		good_users = []
		for user_id in users:
			if self.is_good_user(user_id):
				good_users.append(user_id)
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
			if not is_retweet(status) and not is_reply(status):
				days_until.append(helper.days_until(status.created_at))
				
		if len(days_until) == 0:
			return False
		if len(days_until) > 5 and np.amax(days_until[0:5]) < 1:
			return False
		if len(days_until) > 0 and days_until[0] > 14:
			return False
		return True
		
	def rate_limit(self):
		""" Prints rate limit informations to the specific request """
		head = self.api.last_response.headers
		print("remaining requests:", head['x-rate-limit-remaining'])
		
		# TODO different mutliply factor for different heads
		print("tweets remaining: ~", int(head['x-rate-limit-remaining']) * 15)
		
		reset = int(head['x-rate-limit-reset'])
		time_until = reset - time.time()
		print("reset at:", datetime.fromtimestamp(reset))
		print(f"reset in: {int(time_until // 60):02d}:{int(time_until % 60):02d}")
	

def is_retweet(tweet):
	"""Takes tweet and returns true if tweet is retweet"""
	try:
		# Maybe there is a way without throwing an error
		tweet.retweeted_status
		return True
	except:
		# Add actual exception here not for all
		return False


def is_reply(tweet):
	"""Takes tweet and returns true if tweet is reply"""
	try:
		# Maybe there is a way without throwing an error
		if tweet.in_reply_to_status_id:
			return True
	except:
		# Add actual exception here not for all
		return False
		
class Analyzer:
	""" Analyzer class. Takes tweets/users and will return analyzations"""
	def __init__(self):
		pass
		
		
		
		
		
