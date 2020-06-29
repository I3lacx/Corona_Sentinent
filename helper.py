"""
Helper function to load keys and extra functionality
Add functions here that may be used for different use cases and 
are useful as an extern function
"""

import tweepy
import time
import datetime
import json

# TODO (possible extensions)
# plots say location name instead of geocode
# 	by: in configs say location name and will be interly converted to geocode
# 	or: transform geocode to name by checking with constants

"""
latitude,longitude,distance,fillcolor,linewidth,linecolor
Area to scan:
50.79234746151547,9.286462046949623,200.39917980930625
52.608896331013604,10.736657359449623,222.3408738021322
48.94326100903298,10.538903453199623,145.68010936710823
"""
# Constants
GEOCODES = {
	"darmstadt": "49.8728,8.6511",
	"frakfurt": "50.110924,8.682127",
	"new_york": "40.712776,-74.005974",
	"hannover": "52.3756631,9.7338833",
	"scan_1": "50.792347461,9.2864620469,200km",
	"scan_2": "52.6088963310,10.7366573594,222km",
	"scan_3": "48.943261009,10.5389034531,145km"
}


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


def get_api(user_auth = False, app_path="app_auth", user_path="user_auth"):
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

	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
	return api


def days_until(date):
	""" Converts date of form: ..... into number of days from 01.01.2020 until this date (int)"""
	# TODO maybe set fixed date?
	# or atleast save today time in graph
	today = datetime.datetime.now()
	delta = today - date
	return delta.days


def hours_until(date):
	now = datetime.datetime.now()
	delta = now - date
	hours = delta.seconds//3600 + delta.days * 24
	return hours

def geocode_from_location(location, radius=100):
	""" place is input from constants defined above """
	if location == "":
		return ""
	
	try:
		location_geo = GEOCODES[location]
	except KeyError:
		raise KeyError(f"Location: {location} not found in GEOCODES dict")
	
	if "scan" in location:
		geocode = location_geo
	else:
		geocode = location_geo + f",{radius}km"
	
	return geocode


def config_to_txt(config):
	""" Turns the config to readable text. Will be divided into seperate keys in a dict """
	# TODO add number searches based on the type of search
	query = f"q={config['search']['query']}, \
	 location={config['search']['location']} \
	 (r={config['search']['radius']})"
	txt_dict = {
		"query": query
	}
	return txt_dict


def set_default(dicti, key, value):
	""" Checks if key is already defined, if not will set to value"""
	try:
		dicti[key]
	except KeyError:
		dicti[key] = value
	

def init_config(config):
	""" Adds additional information to config dictionary """
	# TODO check dictionary for problems here (mandatorys not set)
	
	# Set defaults if not defined
	set_default(config["search"], "radius", 100)
	set_default(config["search"], "max_searches", 1000)
	set_default(config["search"], "rate_limit", True)
	
	config["search"]["geocode"] = geocode_from_location(config["search"]["location"], config["search"]["radius"])
	
	return config


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
	if tweet.in_reply_to_status_id:
		return True
	else:
		return False

def save_user(user, file_name=None):
	""" Takes user object and saves it to file, with user_name as file_name"""
	if file_name is None:
		file_name = "saved_data/users/" + str(user.name)
		
	with open(file_name, "w") as f:
		json.dump(user._json, f)


if __name__ == "__main__":
	# For testing
	get_api(False)






























