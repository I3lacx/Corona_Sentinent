"""
Helper function to load keys and extra functionality
Add functions here that may be used for different use cases and 
are useful as an extern function
"""

import tweepy
import time
from datetime import date

# Constants
GEO_DARMSTADT = "49.8728,8.6511"
GEO_FRANKFURT = "50.110924,8.682127"
GEO_NEWYORK = "40.712776,-74.005974"
GEO_HANNOVER = "52.3756631,9.7338833"


def load_keys(path):
	""" 
	Loads and returns Key, Secret
	Expected file format:
	key
	secret
	
	No comma, no "", just new line at the end
	"""
	
	with open(path) as f:
		# Read lines and exclude \n from file
		key = f.readline()[0:-1]
		secret = f.readline()[0:-1]
		
	return key, secret


def get_api(user_auth = False, app_path="app_auth", user_path="user_auth",):
	""" 
	Loads Application and user (if user_auth) keys from paths
	:app_apth: path for Application keys
	:user_path: path for User keys
	:returns: tweepy API 
	"""
	
	# Loads Application (Consumer) Keys
	application_key, application_secret_key = load_keys(app_path)

	# OAuth 2 Application (Consumer) Only Authentication 
	auth = tweepy.OAuthHandler(application_key, application_secret_key)
	
	if user_auth:
		# Loads User Keys
		user_token, user_token_secret = load_keys(user_path)
		
		# 0Auth 1 Application User Authentication
		auth.set_access_token(user_token, user_token_secret)

	api = tweepy.API(auth)
	return api


def days_until(date):
	""" Converts date of form: ..... into number of days from 01.01.2020 until this date (int)"""
	# TODO maybe set fixed date?
	# or atleast save today time in graph
	today = date.today()
	delta = today - date
	return delta.days
	
if __name__ == "__main__":
	# For testing
	get_api(False)
