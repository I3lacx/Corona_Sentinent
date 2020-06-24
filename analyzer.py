import numpy as np
import helper
import tweepy 
import time
from datetime import datetime
import matplotlib.pyplot as plt

class Analyzer:
	""" Analyzer class. Takes tweets/users and will return analyzations
	If possible, should NOT use the api by calling it
	"""
	def __init__(self, config, model=None):
		self.config = config
		self.model = model
	
	def analyze_timeline(self, timeline):
		""" timeline is an array with twitter objects """
		# TODO should be no different if timeline or just an array of tweets
		# TODO should the crawler do the looping before so that analyze only gets tweets?
		
		num_retweets = 0
		retweets_age = []
		num_replys = 0
		replys_age = []
		num_tweets = 0
		tweets_age = []
		hash_dict = {}
	
		for tweet in timeline:
			if helper.is_retweet(tweet):
				retweets_age.append(helper.days_until(tweet.created_at))
				num_retweets += 1
			elif helper.is_reply(tweet):
				replys_age.append(helper.days_until(tweet.created_at))
				num_replys += 1
			else: 
				num_tweets += 1
				tweets_age.append(helper.days_until(tweet.created_at))
				hash_dict = update_hash_dict(hash_dict, tweet.entities['hashtags'])
	
		out = {	
			"counts": {
			 	"retweets": num_retweets,
			 	"replys": num_replys,
			 	"tweets": num_tweets
			},
			"ages": {
				"retweets": retweets_age,
				"replys_age": replys_age,
				"tweets_age": tweets_age
			},
			"hash_dict": hash_dict
		}
		
		return out
	
	def analyze_sentiment(self, tweets, model=None):
		if model is None:
			model = self.model
		
		texts = [tweet.text for tweet in tweets]
		sentis = model.get_sentiment_labels_batch(texts)
		
		return sentis
	

def update_hash_dict(hash_dict, hashtags):
	for tag in hashtags:
		try:
			hash_dict[tag["text"]] += 1
		except KeyError as e:
			hash_dict[tag["text"]] = 1
	return hash_dict
			
		
		
		
		
