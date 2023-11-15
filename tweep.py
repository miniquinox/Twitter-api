## need to install wordcloud and tweepy library
import tweepy
import matplotlib.pyplot as plt 
import config
auth = tweepy.Client(bearer_token= config.bearer_token)
import json
from tweepy import Client

def save_tweets_to_json(tweets, file_name):
    """ Saves a list of tweet data to a JSON file."""
    # Convert each Tweet object into a dictionary
    tweets_data = []
    for tweet in tweets:
        
        tweet_dict = {
            'id': tweet.id,
            'text': tweet.text
        }
        tweets_data.append(tweet_dict)
    
    # Write the list of dictionaries to a JSON file
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(tweets_data, f, ensure_ascii=False, indent=4)

# Usage example
# Initialize your Tweepy client
response = tweepy.Client(bearer_token='your-bearer-token')

# Fetch tweets using the client
query = '#INFORMS2023'
tweets = response.search_recent_tweets(query=query, max_results=10).data

# Save the tweets to a JSON file
save_tweets_to_json(tweets, 'tweets_data.json')
