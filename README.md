## Sentiment Analyzation of German Tweets

_A student project by Nina Kolmar and Maximilian Otte_

The general idea of the code is to use crawler.py to crawl the data, analyzer to analyze the data, plotter to create plots and model.py to act as an interface between the our and pre implemented sentiment analyzers. To configurate what will be used in which way, a config dictionary with pre defined attributes is used and can be seen, for example, in data_exploration.ipynb. Example.py is an example on how our code can be used (The config file is outdated though).

All of the code regarding the models is stored in sentiment_models folder.

#### Data Scraping
In order to run the scan on the data every hour, we used the full_scan.py file. All of the specifications made can be found in there.


#### Data Analysation
We analyzed the data with the help of plot_user_based_sentiment.py. For this a folder
for the results need to be created and the path should be placed in config\["analyze_sentiment"]\["users_dir"]. 
Furthermore this direction needs to contain a file called "sentiment_analysis_overview.json" containing _{}_ . This file already exists on the analyzed data in saved_data/full_scan_both/resutls/all

#### Saved Data
All of saved data and analyzation results is found in the saved_data folder. In this full_scan_both folder, the resuls (The analyzation results), all the data from the tweets in tweets and all the scraped users in users can be found. The "0", "1" and "2" folders indicate the region that was used in the search. 

