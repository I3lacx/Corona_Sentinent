## Sentiment Analyzation of German Tweets

_A student project by Nina Kolmar and Maximilian Otte_

This is a reposetory for scarping data from twitter, based on tweepy and twitters API. With this reposetorey you can:

- Automatically scrape data from twitter under specific constraints for longer time periods than 7 days
- Analyse textual data with different natural language models
- Plot data information/ analyzation results in nice plots

#### Code Structure

The general idea of the code is to use crawler.py to crawl the data, analyzer to analyze the data, plotter to create plots and model.py to act as an interface between our implemented sentiment analyzers, which is specialized in german tweets. To configurate what will be used in which way, a config dictionary with pre-defined attributes is used. One example for this is data_exploration.ipynb.
Example.py is an example on how our code can be used and includes a more indepth tutorial of the code. (The config file is outdated though).

All of the code regarding the different sentiment models is stored in sentiment_models folder.

#### Data Scraping
In order to run the scan on the data every hour, we used the full_scan.py file. All of the specifications made can be found in there, with additional information.


#### Data Analysation
We analyzed the data with the help of plot_user_based_sentiment.py. For this a folder for the results need to be created and the path should be placed in config\["analyze_sentiment"]\["users_dir"]. 
Furthermore this direction needs to contain a file called "sentiment_analysis_overview.json" containing _{}_ . This file already exists on the analyzed data in saved_data/full_scan_both/resutls/all

#### Saved Data
All of saved data and analyzation results is found in the saved_data folder. In this full_scan_both folder, the resuls (The analyzation results), all the data from the tweets in tweets and all the scraped users in users can be found. The "0", "1" and "2" folders indicate the region that was used in the search. 

#### Ethical Information
TODO: Data scraping is not optimal, good to know before interpreting the resutls!