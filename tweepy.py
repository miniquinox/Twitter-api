import tweepy
import json

def load_credentials(file_name):
    with open(file_name, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    credentials = load_credentials('credentials.json')

    # Set up Tweepy client
    client = tweepy.Client(
        bearer_token=credentials['bearer_token'],
        consumer_key=credentials['consumer_key'],
        consumer_secret=credentials['consumer_secret'],
        access_token=credentials['access_token'],
        access_token_secret=credentials['access_token_secret']
    )

    # Example usage of the client
    # You can use the client to interact with the Twitter API