## !pip3 install apify_client

# Import necessary libraries
import json
import os
import logging
from apify_client import ApifyClient
from datetime import datetime, timedelta

# Function to load apify_setup from a JSON file
def load_apify_setup(file_name):
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading configuration file {file_name}: {e}")
        return None

# Function to check whether tweets contain search keywords
def contains_keyword(text, search_keyword):
    if search_keyword.lower() in text.lower():
        return True
    return False

# Function to fetch relevant tweets
def run_actor(client, setup):
    try:
        # Get the current date
        current_date = datetime.now()

        # Initiate the datetime variable
        since_date = datetime.now()

        if setup["frequency"] == 'daily':
            # Go back by a day
            since_date = current_date - timedelta(days=1)
        elif setup["frequency"] == 'weekly':
            # Go back by a week
            since_date = current_date - timedelta(weeks=1)
        elif setup["frequency"] == 'monthly':
            # Go back by a month
            since_date = current_date - timedelta(days=30)

        # Prepare the Actor input
        run_input = {
            "searchTerms": setup["search_keywords"],
            "searchMode": "live",
            "maxTweets": setup["max_limit"],
            "addUserInfo": True,
            "scrapeTweetReplies": False,
            "sinceDate": since_date.strftime("%Y-%m-%d"),
            "untilDate": current_date.strftime("%Y-%m-%d")
        }

        return client.actor(setup['actor_id']).call(run_input=run_input)
    except Exception as e:
        print(f"Error searching tweets: {e}")
        return None

# Function to group tweets by week based on their creation date.
def group_tweets_by_week(tweets, search_keyword, tweet_fields, created_at_format):
    """
    Groups tweets by week based on their creation date.

    Args:
        tweets (list): List of tweets to be grouped.
        search_keyword (str): The keyword to filter tweets.
        tweet_fields (dict): Dictionary containing tweet field mappings.
        created_at_format (str): The format of the 'created_at' field in tweets.

    Returns:
        dict: A dictionary where keys are week ranges and values are lists of tweets.
              Tweets within each week group are sorted by their creation date (latest first).
              The dictionary is sorted by the start date of each week group (latest first).
    """
    try:
        tweets_by_week = {}
        seen_ids = set()  # Set to keep track of encountered tweet IDs 

        for tweet in tweets:
            if contains_keyword(tweet[tweet_fields["text"]], search_keyword):
                tweet_id = tweet[tweet_fields["tweet_id"]]
                # Skip if tweet ID is already encountered
                if tweet_id in seen_ids:
                    continue

                seen_ids.add(tweet_id)
                created_at = datetime.strptime(tweet[tweet_fields["created_at"]], created_at_format)
                # Calculate the start and end of the week for the tweet
                start_of_week = created_at - timedelta(days=created_at.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                week_key = f"{start_of_week.strftime('%Y-%m-%d')}_to_{end_of_week.strftime('%Y-%m-%d')}"

                # Initialize an empty list for the week if not exists
                if week_key not in tweets_by_week:
                    tweets_by_week[week_key] = []
                
                # Dictionary to store processed tweet fields
                tweet_json = {}

                for key, value in tweet_fields.items():
                    if key == "public_metrics":
                        
                        public_metrics_json = {} # Dictionary to store public metrics

                        for item_key, item_value in tweet_fields[key].items():
                            # Get public metric value from tweet
                            public_metrics_json[item_key] = tweet.get(item_value, "")

                        tweet_json[key] = public_metrics_json # Assign public metrics to tweet JSON
                    elif key == 'created_at':
                        tweet_json[key] = created_at.strftime('%Y-%m-%dT%H:%M:%S.000Z') # Format tweet creation date
                    else:
                        tweet_json[key] = tweet.get(value, "") # Get tweet field value from tweet

                # Append processed tweet to the corresponding week group
                tweets_by_week[week_key].append(tweet_json)

        if tweets_by_week:
            # Sort tweets within each week group by their creation date (latest first)
            for week_key in tweets_by_week:
                tweets_by_week[week_key] = sorted(tweets_by_week[week_key], key=lambda x: x["created_at"], reverse=True)
            
            # Sort the groups by the start date of the week (latest first)
            tweets_by_week = dict(sorted(tweets_by_week.items(), key=lambda x: datetime.strptime(x[0][:10], '%Y-%m-%d'), reverse=True))
        
        return tweets_by_week
    except Exception as e:
        logging.error(f"Error organising {search_keyword} tweets: {e}")
        return None

# Function to save a list of tweets to a generic and year-specific JSON files
def organise_tweets_to_json(tweets, setup):
    try:
        search_keywords = setup["search_keywords"]
        tweet_fields = setup["tweet_fields"]
        created_at_format = setup["created_at_format"]
        base_directory = setup["base_directory"]
        count = 0

        # Ensure the base directory exists
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)

        for keyword in search_keywords:
            tweets_by_week = group_tweets_by_week(tweets, keyword, tweet_fields, created_at_format)

            if tweets_by_week:
                # Write grouped and sorted tweets to a JSON file
                output_file = os.path.join(base_directory, f"tweets_{keyword}.json")

                # Check if the file exists, and determine the mode accordingly
                mode = 'r+' if os.path.isfile(output_file) else 'w'

                # Open the file in the determined mode
                with open(output_file, mode, encoding='utf-8') as file:

                    # Initialize the list with existing data if exists
                    existing_data = json.load(file) if mode == 'r+' else {}
                    # Initialize a dictionary to store the tweets
                    all_data = {**tweets_by_week, **existing_data}

                    if mode == 'r+':
                        # Reset the pointer if mode is 'r+'
                        file.seek(0)

                    # Write the data to the file
                    json.dump(all_data, file, ensure_ascii=False, indent=4)
                    logging.info(f"{keyword} tweets saved to {output_file}.")
                    count += 1
            else:
                logging.warning(f"No tweets found for {keyword}.")

        return count > 0
    except Exception as e:
        logging.error(f"Error processing and saving tweets: {e}")
        return False

def main():
    try:
        # Set up Apify client
        setup = load_apify_setup("apify_setup.json")
        if not setup:
            logging.error("Error loading the set up.")
            return

        # Initialize the ApifyClient with the API token
        client = ApifyClient(setup["api_token"])
        if not client:
            logging.error("Error initializing ApifyClient.")
            return

        # Run the Actor and wait for it to finish
        run = run_actor(client, setup)
        if not run:
            logging.error("Error running the actor.")
            return

        response_generator = client.dataset(run["defaultDatasetId"]).iterate_items()
        if not response_generator:
            logging.warning("Empty response.")
            return

        tweets = list(response_generator)
        if not tweets:
            logging.warning("No tweets found.")
            return

        # Process the tweets if the list is not empty
        is_success = organise_tweets_to_json(tweets, setup)
        if is_success:
            logging.info("Request Executed Successfully!")

    except Exception as e:
        logging.error(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()