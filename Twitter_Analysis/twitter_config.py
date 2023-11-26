# Import relevant libraries
import tweepy
import json
import os
from datetime import datetime, timedelta, timezone

# Function to load twitter_setup from a JSON file
def load_twitter_setup(file_name):
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading configuration file {file_name}: {e}")
        return None

# Helper function to generate the date range string
def generate_date_range_key():
    current_date = datetime.now(timezone.utc)
    seven_days_ago = current_date - timedelta(days=7)
    return f"{seven_days_ago.strftime('%Y-%m-%d')}_to_{current_date.strftime('%Y-%m-%d')}"

# Function to get ID of a specific twitter account.
def get_twitter_account_id(client, username):
    try:
        return client.get_user(username=username).data.id
    except tweepy.TweepyException as e:
        print(f"Error fetching user ID for {username}: {e}")
        return None

# Function to add or remove fields from tweets data
def process_tweets(tweets, base_tweet_url):

    processed_tweets = []

    for tweet in tweets:
        tweet_data = tweet.data

        # Add URL to the tweet
        tweet_data['url'] = f"{base_tweet_url}{tweet_data['id']}"
        # Remove 'edit_history_tweet_ids' field from the data
        tweet_data.pop('edit_history_tweet_ids', None)
        # Append the processed tweet to the list
        processed_tweets.append(tweet_data)
    
    return processed_tweets

# Function to save a list of tweets to a generic and year-specific JSON files
def save_tweets_to_json(tweets, search_criteria, base_tweet_url, base_directory):

    try:

        # Ensure the base directory exists
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)

        # Generate the date range key
        date_range_key = generate_date_range_key()

        # Process tweets to add tweet URLs and remove 'edit_history_tweet_ids'.
        processed_tweets = process_tweets(tweets, base_tweet_url)

        files = []
        tweets_by_year = {}

        # Construct the base filename and append it to the list
        base_file_name = os.path.join(base_directory, f"tweets_{search_criteria}.json")
        files.append(base_file_name)


        # Assuming the year is always the last 4 characters of the criteria
        potential_year = search_criteria[-4:]
        
        if not potential_year.isdigit():

            for tweet in processed_tweets:
                # Extract the year from the 'created_at' field
                created_year = datetime.fromisoformat(tweet['created_at'][:-1]).year  # Strip the 'Z' before conversion
                
                # Construct the year-specific filename and append it to the list
                year_file_name = os.path.join(base_directory, f"tweets_{created_year}_{search_criteria}.json")

                if year_file_name not in tweets_by_year:
                    files.append(year_file_name)
                    tweets_by_year[year_file_name] = [tweet]
                else:
                    existing_tweets = tweets_by_year[year_file_name]
                    existing_tweets.append(tweet)
                    tweets_by_year[year_file_name] = existing_tweets
        
        for file_name in files:
            # Check if the file exists, and determine the mode accordingly
            mode = 'r+' if os.path.isfile(file_name) else 'w'

            # Open the file in the determined mode
            with open(file_name, mode, encoding='utf-8') as file:

                # Initialize the list with existing data if exists
                existing_data = json.load(file) if mode == 'r+' else []
                # Initialize a dictionary to store the tweets
                modified_data = {}

                # Extend the existing data with all new tweets
                if file_name in tweets_by_year:
                    existing_data.extend(tweet for tweet in tweets_by_year[file_name])
                else:
                    existing_data.extend(tweet for tweet in processed_tweets)
                    
                modified_data[date_range_key] = existing_data

                if mode == 'r+':
                    # Reset the pointer if mode is 'r+'
                    file.seek(0)

                # Write the data to the file
                json.dump(modified_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error processing and saving tweets for {search_criteria}: {e}")

# Function to fetch relevant tweets
def search_tweets(client, query, include_retweets, max_results, tweet_fields):
    try:
        if not include_retweets:
            query += " -is:retweet"
        query += " lang:en"

        return client.search_recent_tweets(query=query, max_results=max_results, tweet_fields=tweet_fields)
    except tweepy.TweepyException as e:
        print(f"Error searching tweets for {query}: {e}")
        return None

if __name__ == "__main__":
    try:
        # Set up Tweepy client
        setup = load_twitter_setup('twitter_setup.json')
        
        if setup:
            client = tweepy.Client(**setup['twitter_credentials'])

            for criteria in setup['search_criteria']:
                response = search_tweets(client, criteria, setup['is_include_retweets'], setup['max_limit'], setup['tweet_fields'])
                if response and response.data:
                    save_tweets_to_json(response.data, criteria, setup['tweet_base_url'], setup['base_directory'])
                else:
                    print(f"No tweets found for {criteria}")
    except Exception as e:
        print(f"Error in main execution: {e}")