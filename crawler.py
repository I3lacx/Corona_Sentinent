"""
Crawler should do all the calls to the API and return the objects directly
The main idea is that the crawler will get called once and with these objects in cash we can
analyze them as many times as we want without querying another time
"""
import helper
import tweepy 
import time
from datetime import datetime
import json
import numpy as np
import os


class Crawler:
	""" Crawler class. Using the tweepy api to get tweets specified in the configs """
	
	def __init__(self, config):
		""" Set configs to self values """
		self.config = config
		self.api = self.get_api()
		# Set this parameter during full scan
		self.unique_user_ids = set(())
		
	def check_config():
		""" Check some elements in the config """
		raise NotImplementedError
		
	def get_api(self):
		try:
			api = helper.get_api(self.config["user_auth"], self.config["auth_path"])
		except KeyError:
			api = helper.get_api(self.config["user_auth"])
		return api
	
	def get_users(self):
		""" returns users objects """
		if self.config["get_user"]["search_type"] == "recent_user":
			users = self.get_recent_users()
		elif self.config["get_user"]["search_type"] == "recent_retweeted_user":
			users = self.get_recent_retweeted_users()
		else:
			raise ValueError(f"Value: {self.config['get_user']['search_type']} not recognized")
		
		return users
	
	def get_user_from_id(self, user_id):
		""" id specifies the id or screen name of the user """
		user = self.api.get_user(user_id)
		return user
	
	def get_tweets(self):
		"""
		Callable from outside get tweets function
		Will return tweet objects for num_resuts and specific settings
		"""
		iterator = self._get_tweet_iterator()
		res_tweets, _ = self._get_from_iterator(iterator)
		
		return res_tweets
	
	def _get_full_search_iterator(self):
		""" get full search iterator 
		NOT TESTED!
		"""
		opts = self.config["full_search"]
		iterator = tweepy.Cursor(craw.api.search_full_archive,
					query=opts["query"], 
					fromDate=opts["fromDate"], 
					toDate=opts["toDate"],
					environment_name=opts["env_name"])
		return iterator
	
	def _get_tweet_iterator(self, geocode=None):
		"""
		Main connection to tweepy
		Returns tweets ITERATOR from tweepy Cursor search with specified settings
		from self.config
		Note: Does NOT do a request! Only when iterating over tweets, it will do the requests
		"""
		
		if geocode is None:
			geocode=self.config["search"]["geocode"]
		
		tweets = tweepy.Cursor(self.api.search, q=self.config["search"]["query"],
							 geocode=geocode).items(self.config["search"]["max_searches"])
		return tweets
	
	def _get_from_iterator(self, iterator):
		""" should be used interally only
		given an iteratior will search through tweets with filtering and stuff	
		return code 1 for number of results reached, -1 for search reached end point e.g. (time)
		"""
		return_code = 0
		
		res_tweets = []
		num_results = 0
		checked_tweets = 0
		for tweet in iterator:
			checked_tweets += 1
			if self.check_tweet(tweet) == 1:
				num_results += 1
				res_tweets.append(tweet)
				if num_results == self.config["search"]["num_results"]:
					# print("Number of results reached")
					return_code = 1
					break
			elif self.check_tweet(tweet) == -1:
				# print("Search reached end point")
				return_code = -1
				break
			
		self.rate_limit(checked_tweets)
		return res_tweets, return_code
	
	def check_tweet(self, tweet):
		"""
		Checks tweet object for settings specified in filter
		return codes:
		0 -> Not fitting for filter config
		1 -> fitting all filter configs
		-1 -> Not fitting and search should stop
		"""
		if self.config["search"]["filter"]["until"]:
			if tweet.created_at < self.config["search"]["filter"]["until"]:
				return -1
				
		if self.config["search"]["filter"]["not_reply"]:
			if helper.is_reply(tweet):
				return 0
				
		if self.config["search"]["filter"]["not_retweet"]:
			if helper.is_retweet(tweet):
				return 0
		
		return 1
	
	def get_recent_users(self, geocode=None):
		""" Looks for recent tweets given a query and a geocode
		returns the user objects of these users
		user_ids is optional input array if you don't want to add these user ids.
		"""
		users = []
		
		user_ids = self.unique_user_ids		
		
		num_users = self.config["get_user"]["num_users"]
		num_results = 0
		
		tweets_iter = self._get_tweet_iterator(geocode)
		for tweet in tweets_iter:
			current_user = tweet.user
			if not current_user.id in user_ids:
				if self.is_good_user(current_user.id):
					users.append(current_user)
					user_ids.add(current_user.id)
					num_results += 1
					if num_results == num_users:
						break
	
		if self.config["get_user"]["unique_ids"]:
			self.unique_user_ids.update(user_ids)
			
		self.rate_limit()
		return users

	def get_recent_retweeted_users(self):
		""" Looks for recent tweets, checks if it's a retweed, if yes, then will return the users objects
		that have been retweeted 
		"""
		# TODO unique users only
		user_ids = []
		num_users = self.config["get_user"]["num_queries"]
		num_results = 0
		num_checked_tweets = 0
		
		for tweet in self._get_tweet_iterator():
			num_checked_tweets += 1
			if helper.is_retweet(tweet):
				user_ids.append(tweet.retweeted_status.user)
				num_results += 1
				if num_results == num_users:
					break
					
		self.rate_limit(num_checked_tweets)
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
			last_action = status
			if not helper.is_retweet(status) and not helper.is_reply(status):
				days_until.append(helper.days_until(status.created_at))
		
		# His last 100 actions were within the last 3 days (too much activity)
		if helper.hours_until(last_action.created_at) < (24*3) :
			# print("Cond 1:", helper.hours_until(last_action.created_at))
			return False

		# Not enough recent activity in own tweeting
		if len(days_until) > 0 and days_until[0] > 7:
			# print("Cond 2")
			return False
			
		return True
	
	def rate_limit(self, num_checked_tweets=None):
		""" 
		Prints rate limit informations to the specific request (if active in configs)
		Should be called by every function after calling the api
		"""
		if not self.config["search"]["rate_limit"]:
			return
		
		if num_checked_tweets:
			print("Checked Tweets:", num_checked_tweets)

		head = self.api.last_response.headers	
		print("remaining requests:", head['x-rate-limit-remaining'])
		
		# TODO I don't know how I can get that 15 not hardcoded
		print("tweets remaining: ~", int(head['x-rate-limit-remaining']) * 15)
		
		reset = int(head['x-rate-limit-reset'])
		time_until = reset - time.time()
		print("reset at:", datetime.fromtimestamp(reset))
		print(f"reset in: {int(time_until // 60):02d}:{int(time_until % 60):02d}")
	
	def compare_users_and_tweets(self):
		""" Looks at the user ids and compares them to saved tweets """
		self.unique_user_ids = self.load_user_list()
		
		# get tweet filenames:
		scanned_tweets = []
		for i in range(3):
			path = self.config["full_scan"]["path"] + "tweets/" + str(i) + "/"
			tweets = os.listdir(path)
			scanned_tweets += tweets
		
		print("Scanned Tweets:", len(scanned_tweets))
		unique_list = set(scanned_tweets)
		print("Unique Tweets:", len(unique_list))
		print("Unique user_ids:", len(self.unique_user_ids))
		print("XOR:", len(self.unique_user_ids ^ unique_list))
		print("user - tweets:", len(self.unique_user_ids - unique_list))
		print("tweets - user:", len(unique_list - self.unique_user_ids))
	
	def _get_timeline_iterator(self, user):
		""" Returns timeline (tweepy iterator) of user object"""
		timeline = tweepy.Cursor(self.api.user_timeline, id=user.id_str).items(self.config["search"]["max_searches"])
		return timeline

	def get_timeline(self, user):
		""" Seraches through timeline of one user and returns tweet objects (applies search options) """
		iterator = self._get_timeline_iterator(user)
		res_tweets, return_code = self._get_from_iterator(iterator)
		
		return res_tweets

	def get_full_timeline_until(self, user):
		""" Searches through a full timeline and returns no tweets if it was not able to search the whole timeline """
		iterator = self._get_timeline_iterator(user)
		res_tweets, return_code = self._get_from_iterator(iterator)
		if return_code == -1:
			# analyzed all tweets until specified time
			return res_tweets
		else:
			return []
		
	
	def get_timeline_tweets_from_user_list(self, users):
		"""Returns a nestedlist, where each element of the outer list contains a list with all tweets of the user"""
		all_tweets = [self.get_timeline(user) for user in users]
		return all_tweets
		
		
	def save_tweets(self, tweets, file_name, configs=True):
		""" Takes list of tweet objects and saves to file"""
		# TODO check if path exists and create new if needed
		
		# Checks path and returns if file is already existing:
		
		if os.path.isfile(file_name):
			print("File already existing, exiting...")
			return 
			
		with open(file_name, "w") as f:
			for tweet in tweets:
				json.dump(tweet._json, f)
				f.write('\n')
		
		if configs:
			# saves extra file without .json with infos about it:
			with open(file_name[:-5], "w") as f:
				f.write(datetime.datetime.now())
				f.write('\n')
				f.write(str(self.config))
		

	def load_tweet(self, file_name, is_dict=False):
		""" Loads tweet from json file and uses api to convert back to object 
		:param api: api for conversion, is not needed if is_dict is true
		:param is_dict: True -> will return dictionary instead of Tweet object,
						 should be faster, may be useful for a lot of tweets
		:return: Tweet Object or Dict (if is_dict is true)"""
		
		tweets = []
		
		with open(file_name) as f:
			for line in f:
				tweet = json.loads(line)			
				if not is_dict:
					tweet = tweepy.models.Status.parse(self.api, tweet)
				tweets.append(tweet)
				
		return tweets
	
	def full_scan(self):
		""" Do a full scan over all different locations: """
		# Load old user_ids 
		self.unique_user_ids = self.load_user_list()
		
		# Scan for users
		print("Scanning for Users...")
		users_list = []
		for location in self.config["full_scan"]["locations"]:
			geocode = helper.geocode_from_location(location)
			users_list.append(self.get_recent_users(geocode=geocode))
		
		print(np.shape(users_list))
	
		print("Saving new User List")
		# Append new users to saved list
		self.save_user_list(users_list)
		
		
		# Scan and save tweets of these users
		for idx, users in enumerate(users_list):
			print("\nScanning and saving tweets:", idx)
			for u_idx, user in enumerate(users):
				print(f"{u_idx}-", end="")
				path = self.config["full_scan"]["path"] + "tweets/" + str(idx) + "/" + user.id_str
				tweets = self.get_timeline(user)
				self.save_tweets(tweets, path, configs=False)
		

		
	def save_user_list(self, new_users_list):
		""" 3 dim array users, only filled with new users to avoid overwriting the whole thing """
		path = self.config["full_scan"]["path"] + "users/"
		for i in range(len(self.config["full_scan"]["locations"])):
			path_sp = path + "users_" + str(i)
			with open(path_sp, "a") as f:
				for user in new_users_list[i]:
					f.write(user.id_str + "\n")
		
		
	def load_user_list(self):
		""" Returns set """
		path = self.config["full_scan"]["path"] + "users/"
		unique_ids = set(())
		for i in range(len(self.config["full_scan"]["locations"])):
			path_sp = path + "users_" + str(i)
			with open(path_sp, "r") as f:
				user_ids = f.readlines()
			# Set operation to fuse both sets
			unique_ids.update(set([x.strip() for x in user_ids]))
		return unique_ids

	def load_tweet_for_analysation(self, filename):
		tweets = self.load_tweet(filename)
		reduced_tweets = [ReducedStatus(t.user.id_str, t.created_at, t.text) for t in tweets]
		return reduced_tweets


class ReducedUser(object):
	def __init__(self, user_id):
		self.id_str = user_id


class ReducedStatus():
	def __init__(self, user_id, created_at, text):
		self.user = ReducedUser(user_id)
		self.created_at = created_at
		self.text = text
		
		
		
		
		
		
		
		
		
		
		
	
	

		
