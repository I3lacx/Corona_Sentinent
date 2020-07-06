import math
import statistics

import numpy as np
import helper
import tweepy
import time
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from model import TrainedSentimentModel
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

	def analyze_and_plot_sentiment(self, users_tweets):
		analysation = self._analyze_sentiment_user_based(users_tweets)
		only_extremely_pos_dict = {week: info["extremely_pos_percentage"] for week, info in analysation.items()}
		only_extremely_neg_dict = {week: info["extremely_neg_percentage"] for week, info in analysation.items()}
		config = self.config.copy()
		config["plot"]["title"] = "Percentage extremely positive classified"
		plot = Plotter(config)
		plot.plot_dict(only_extremely_pos_dict)
		config["plot"]["title"] = "Perrcentage extremely negative classified"
		plot = Plotter(config)
		plot.plot_dict(only_extremely_neg_dict)

	def _group_tweets(self, tweets):
		day_group_dict = self._get_day_group_dict()
		tweets_grouped = {value: [] for value in day_group_dict.values()}
		start_date = self.config["plot"]["start_date"]
		end_date = self.config["plot"]["end_date"]
		for tweet in tweets:
			tweet_creation_time = tweet.created_at
			if start_date <= tweet_creation_time <= end_date:
				tweet_date = tweet_creation_time.strftime("%d.%m")
				group = day_group_dict[tweet_date]
				tweets_grouped[group].append(tweet)
		return tweets_grouped

	def _get_day_group_dict(self):
		start_date = self.config["plot"]["start_date"]
		end_date = self.config["plot"]["end_date"]
		nr_days_per_group = self.config["plot"]["group_by"]
		nr_days_between_start_end = (end_date - start_date).days
		all_days_between = [end_date - timedelta(days=x) for x in reversed(range(0, nr_days_between_start_end+1))]
		days_grouped = [all_days_between[x:x + nr_days_per_group] for x in range(0, len(all_days_between),
                                                                                 nr_days_per_group)]
		date_id_dict = {}
		for day_group in days_grouped:
			group_id = day_group[0].strftime("%d.%m")
			for day in day_group:
				day_string = day.strftime("%d.%m")
				date_id_dict[day_string] = group_id
		return date_id_dict

	def _analyze_sentiment_user_based(self, users_tweets):
		pos_boundary = self.config["analyze_sentiment"]["pos_boundary"]
		neg_boundary = self.config["analyze_sentiment"]["neg_boundary"]
		user_analysations = []
		for user_tweets in users_tweets:
			current_user_analysation = self._get_single_user_sentiment_analysis(user_tweets, pos_boundary, neg_boundary)
			user_analysations.append(current_user_analysation)
		overall_analysation = {group_id: {"tweets": tweets} for group_id, tweets in user_analysations[0].items()}
		for group_id in user_analysations[0]:
			overall_analysation[group_id]["extremely_pos_percentage"] = \
				statistics.mean((user_dict[group_id]["extremely_pos_percentage"] for user_dict in user_analysations))
			overall_analysation[group_id]["extremely_neg_percentage"] = \
				statistics.mean((user_dict[group_id]["extremely_neg_percentage"] for user_dict in user_analysations))
		return overall_analysation


	def _get_single_user_sentiment_analysis(self, users_tweets, pos_boundary, neg_boundary):
		grouped_tweets = self._group_tweets(users_tweets)
		analysation_dict = {group_id: {"tweets": tweets} for group_id, tweets in grouped_tweets.items()}
		for group_id, tweets in grouped_tweets.items():
			if len(tweets) == 0:
				analysation_dict[group_id]["extremely_pos_percentage"] = 0
				analysation_dict[group_id]["extremely_neg_percentage"] = 0
			else:
				extreme_sentiments = self.analyze_extreme_sentiment(tweets, pos_boundary, neg_boundary)
				overall_amount = len(extreme_sentiments)
				extremely_pos_amount = sum(1 for sent in extreme_sentiments if sent == "pos")
				extremely_neg_amount = sum(1 for sent in extreme_sentiments if sent == "neg")
				extremely_pos_percentage = extremely_pos_amount / overall_amount * 100
				extremely_neg_percentage = extremely_neg_amount / overall_amount * 100
				analysation_dict[group_id]["extremely_pos_percentage"] = extremely_pos_percentage
				analysation_dict[group_id]["extremely_neg_percentage"] = extremely_neg_percentage
		return analysation_dict

	def analyze_extreme_sentiment(self, tweets, pos_boundary, neg_boundary):
		tweet_texts = [tweet.text for tweet in tweets]
		if isinstance(self.model, TrainedSentimentModel):
			return self.model.get_label_for_clear_cases(tweet_texts, pos_boundary, neg_boundary)
		raise NotImplementedError


def group_tweets_by_calendar_week(tweets, start_date):
	"""
	Returns a dictionary with calendar weeks (as ints) as keys.
	"""
	first_calendar_week = int(start_date.strftime("%W"))
	current_calendar_week = int(datetime.now().strftime("%W"))
	calendar_week_grouped_tweets = {str(kw): [] for kw in range(first_calendar_week, current_calendar_week + 1)}
	for tweet in tweets:
		if (tweet.created_at - start_date).days > 0:
			tweet_calendar_week = tweet.created_at.strftime("%W")
			tweet_calendar_week = tweet_calendar_week[1:] if tweet_calendar_week.startswith(
				"0") else tweet_calendar_week
			calendar_week_grouped_tweets[tweet_calendar_week].append(tweet)
	return calendar_week_grouped_tweets


def update_hash_dict(hash_dict, hashtags):
	for tag in hashtags:
		try:
			hash_dict[tag["text"]] += 1
		except KeyError as e:
			hash_dict[tag["text"]] = 1
	return hash_dict
