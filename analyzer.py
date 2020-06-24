import numpy as np
import helper
import tweepy 
import time
from datetime import datetime
import matplotlib.pyplot as plt

from plotter import Plotter


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
	
	def analyze_sentiment(self, tweets, polarity=True):
		# TODO add usefull preprocessing and stuff
		# preprocessing is done within the get_polarity method
		sentiments = []
		for tweet in tweets:
			if polarity:
				sentiments.append(self.model.get_polarity(tweet.text))
			else:
				sentiments.append(self.model.get_sentiment_label(tweet.text))
		return sentiments

	def analyze_sentiment_by_weeks(self, tweets, sentiment_pos_limit, sentiment_neg_limit):
		"""Return a dictionary with week-numbers (as strings) as keys and another dictionary (with keys "tweets",
		"extremely_pos_percentage" and "extremely_neg_percentage) as values."""
		start_date = self.config["search"]["filter"]["until"]
		tweets_grouped_by_week = group_tweets_by_calendar_week(tweets, start_date)
		analysation_by_week = {kw: {"tweets": tweets} for kw, tweets in tweets_grouped_by_week.items()}

		for week, tweets_per_week in tweets_grouped_by_week.items():
			sentiments = self.analyze_sentiment(tweets_per_week)
			extremely_pos_amount = sum(1 for sentiment in sentiments if sentiment > sentiment_pos_limit)
			extremely_neg_amount = sum(1 for sentiment in sentiments if sentiment < sentiment_neg_limit)
			overall_amount = len(sentiments)
			if overall_amount == 0:
				analysation_by_week[week]["extremely_pos_percentage"] = 0
				analysation_by_week[week]["extremely_neg_percentage"] = 0
			else:
				extremely_pos_percentage = extremely_pos_amount / overall_amount * 100
				extremely_neg_percentage = extremely_neg_amount / overall_amount * 100
				analysation_by_week[week]["extremely_pos_percentage"] = extremely_pos_percentage
				analysation_by_week[week]["extremely_neg_percentage"] = extremely_neg_percentage
		return analysation_by_week

	def analyze_and_plot_sentiment_per_week(self, tweets, sentiment_pos_limit, sentiment_neg_limit):
		"""Make plots of the percentage of extemely positive and negative classified tweets
		sentiment_pos/neg_limit are the boundaries for classifying the tweets as pos/neg
		"""
		analysation_by_week = self.analyze_sentiment_by_weeks(tweets, sentiment_pos_limit, sentiment_neg_limit)
		only_extremely_pos_dict = {week: info["extremely_pos_percentage"] for week, info in analysation_by_week.items()}
		only_extremely_neg_dict = {week: info["extremely_neg_percentage"] for week, info in analysation_by_week.items()}
		config = self.config.copy()
		config["plot"]["title"] = "Percentage extremely positive classified"
		plot = Plotter(config)
		plot.plot_dict(only_extremely_pos_dict)
		config["plot"]["title"] = "Perrcentage extremely negative classified"
		plot = Plotter(config)
		plot.plot_dict(only_extremely_neg_dict)


def group_tweets_by_calendar_week(tweets, start_date):
	"""
	Returns a dictionary with calendar weeks (as ints) as keys.
	"""
	first_calendar_week = int(start_date.strftime("%W"))
	current_calendar_week = int(datetime.now().strftime("%W"))
	calendar_week_grouped_tweets = {str(kw): [] for kw in range(first_calendar_week, current_calendar_week+1)}
	for tweet in tweets:
		if (tweet.created_at - start_date).days > 0:
			tweet_calendar_week = tweet.created_at.strftime("%W")
			tweet_calendar_week = tweet_calendar_week[1:] if tweet_calendar_week.startswith("0") else tweet_calendar_week
			calendar_week_grouped_tweets[tweet_calendar_week].append(tweet)
	return calendar_week_grouped_tweets
	

def update_hash_dict(hash_dict, hashtags):
	for tag in hashtags:
		try:
			hash_dict[tag["text"]] += 1
		except KeyError as e:
			hash_dict[tag["text"]] = 1
	return hash_dict
			
		
		
		
		
