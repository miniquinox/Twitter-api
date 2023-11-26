# Twitter Data Analysis Project

This project uses the Tweeter API to interact with the X platform to fetch recent tweets based on certain search criteria and perform sentiment analysis on them.

Twitter Developer Portal: https://developer.twitter.com/en/portal/dashboard

## Main Files

Below are the main files and their purposes:

- `twitter_config.py`: This is the main script used for fetching recent tweets. It uses the Twitter API to search for tweets that match the given search criteria and stores the results.

- `twitter_setup.json`: Configuration file required by `twitter_config.py`. It contains Twitter API credentials and search parameters. You need to replace the placeholder values with your actual Twitter API keys and tokens.

- `analysis_config.json`: User input file for sentiment analysis. It defines the parameters for the analysis, such as keywords, types, and relevant years for the tweets to be analyzed.

- `INFORMS_TWEETS/`: The directory where `twitter_config.py` will store the fetched tweets. The script will create new JSON files or append to existing ones based on the date range of the tweets.

## Twitter API Configuration Guide

Create a twitter_setup.json in your project's root to store Twitter API credentials and search parameters.

twitter_setup.json Template: Replace placeholders with your credentials and search preferences.

```json
{
    "search_criteria": ["SEARCH_TERM_1", "SEARCH_TERM_2", "LIST GOES ON.."],
    "max_limit": NUMBER_OF_TWEETS_TO_FETCH,
    "is_include_retweets": true or false,
    "tweet_fields": ["FIELD 1", "FIELD 2", "FIELD 3", "LIST GOES ON.."],
    "twitter_credentials": {
      "bearer_token": "<YOUR_BEARER_TOKEN>",
      "consumer_key": "<YOUR_CONSUMER_KEY>",
      "consumer_secret": "<YOUR_CONSUMER_SECRET>",
      "access_token": "<YOUR_ACCESS_TOKEN>",
      "access_token_secret": "<YOUR_ACCESS_TOKEN_SECRET>"
    },
    "tweet_base_url": "<TWEET_BASE_URL>",
    "base_directory": "<DIRECTORY_TO_TWEETS_STORAGE>"
}
```

## Setup Instructions

1. Ensure that `twitter_setup.json` is filled with your Twitter API credentials and search parameters:

   - `bearer_token`
   - `consumer_key`
   - `consumer_secret`
   - `access_token`
   - `access_token_secret`

2. Define your search criteria in `twitter_setup.json` under the `search_criteria` key. Example search terms:

   - Hashtags (e.g., `#INFORMS2023`)
   - Mentions (e.g., `@INFORMS`)

3. Set the `max_limit` for the number of tweets to fetch and specify if you want to include retweets.

4. The `tweet_fields` define which data points you want to retrieve for each tweet, such as `author_id`, `public_metrics`, and `created_at`.

5. The `tweet_base_url` is used to construct the URL for each tweet.

6. Run `twitter_config.py` to fetch and store tweets.

7. Use `analysis_config.json` to configure sentiment analysis, defining keywords, event types, and date ranges.

## Additional Information

- The project includes a `.gitignore` file to exclude unnecessary files from your Git repository.
