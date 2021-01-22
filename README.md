## Sentiment Analyzation of German Tweets

_A student project by Nina Kolmar and Maximilian Otte_

This is a reposetory for scarping data from twitter, based on tweepy and twitters API. With this reposetorey you can:

- Automatically scrape data from twitter under specific constraints for longer time periods than 7 days
- Analyse textual data with different natural language models
- Plot data information/ analyzation results in nice plots

**For a quick showcase see Tutorial_simple.ipynb**
**A Twitter developer account is needed if you want to scrape your own data!**

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

#### Results
Here are some example results from our analysis. It is important to note however, that all the graphs and conclusions are not universal results and are only valid based on the parameters of our search! Because of how we scraped the data, how people tweet etc. this data is not reflective of the overall population!

![Extremely Negative Amount Summed](https://github.com/I3lacx/Corona_Sentinent/blob/documentation/plots/Extremely%20Negative%20Amount%20Summed.png)

In this graph one can observe the amount of tweets that were classified as negative by our language model over the time between 01.03 and 30.06. There is not a very clear trend visible, related to corona related activities. Some Higher bars represent other political events, but most peaks are unrelated and difficult to pinpoint to a specific event. The slight increase over time can be misleading, but is likely to come from the bias in user data. As we scraped for users with recent activites, the bias in user selection is that they are currently active, irrelevant of their previous activity!

![Extremely Negative Percent](https://github.com/I3lacx/Corona_Sentinent/blob/documentation/plots/neg_perc_all.png)

This graph shows that no change is happening over time. Here each bar represents how much percent of a persons tweets were classified as very negative. This overall trend does not change over time. 

![Extremely Positive Percent](https://github.com/I3lacx/Corona_Sentinent/blob/documentation/plots/pos_perc_all.png)

This graph shows the percent of positively classified tweets from our language model in a given week. Here it can be observed that for certain events, in this case eastern, the model works very good. As a tweet like "Happy Eastern" or "Frohe Ostern" in german, is a positive tweet and can easily be observed in the data. However, no big other trends can be observed besides this one. 
