# Twitter Data Analysis Project

This project uses the APIFY API to interact with the X platform to fetch recent (daily, weekly or monthly) tweets based on certain search criteria and perform sentiment analysis on them.

[Click Here](https://console.apify.com/actors/heLL6fUofdPgRXZie/input) to access the APIFY Actor in use.

## Main Files

Below are the main files and their purposes:

- `apify_config.py`: This is the main script used for fetching tweets. It uses the APIFY API to search for tweets that match the given search criteria and stores the results.

- `apify_setup.json`: Configuration file required by `apify_config.py`. It contains APIFY API and Actor credentials and search parameters. You need to replace the placeholder values with your actual APIFY API keys and tokens.

- `TWEET_ARCHIEVE/`: The directory where `apify_config.py` will store the fetched tweets. The script will create new JSON files or append to existing ones based on the date range of the tweets.

## APIFY API Configuration Guide

Create a apify_setup.json in your project's root to store APIFY API credentials and search parameters.

apify_setup.json Template: Replace placeholders with your credentials and search preferences.

```json
{
    "search_keywords": ["SEARCH_TERM_1", "SEARCH_TERM_2", "LIST GOES ON.."],
    "max_limit": NUMBER_OF_TWEETS_TO_FETCH,
    "frequency": "<RECENCY>",
    "tweet_fields": {"author_id": "<CORRESPONDING_FIELD>",
                     "created_at": "<CORRESPONDING_FIELD>",
                     "text":"<CORRESPONDING_FIELD>",
                     "tweet_id": "<CORRESPONDING_FIELD>",
                     "public_metrics" : {
                        "retweet_count": "<CORRESPONDING_FIELD>",
                        "reply_count": "<CORRESPONDING_FIELD>",
                        "quote_count": "<CORRESPONDING_FIELD>",
                        "bookmark_count": "<CORRESPONDING_FIELD>"},
                     "url": "<CORRESPONDING_FIELD>"
                    },
    "created_at_format": "%a %b %d %H:%M:%S +0000 %Y",
    "api_token": "<YOUR_ACCESS_TOKEN>",
    "actor_id" : "<APIDY_ACTOR_ID>",
    "base_directory": "TWEET_ARCHIEVE"
}
```

## Setup Instructions

1. Ensure that `apify_setup.json` is filled with your Apify API credentials and search parameters:

   - `api_token`
   - `actor_id`

2. Define your search criteria in `apify_setup.json` under the `search_keywords` key. Example search terms:

   - Hashtags (e.g., `#INFORMS2023`)
   - Mentions (e.g., `@INFORMS`)

3. Set the `max_limit` to the number of tweets you want to fetch.

4. Set `frequency` to either `daily` (goes back by a day), `weekly`(goes back by a 7 days) or `monthly` (goes back by 30 days). This basically sets the start date to the number of days you wanna go back, asssuming the current date as the default end date.

4. The `tweet_fields` define which data points you want to retrieve for each tweet, such as `author_id`, `public_metrics`, and `created_at`.

5. Run `apify_setup.py` to fetch and store tweets.

## `apify_setup.json` Default Setup

Ensure to replace the api_token.
```json
{
    "search_keywords": [
        "@INFORMS",
        "#INFORMS2023"
    ],
    "max_limit": 600,
    "frequency": "weekly",
    "tweet_fields": {"author_id": "user_id_str",
                     "created_at": "created_at",
                     "text": "full_text",
                     "tweet_id": "id_str",
                     "public_metrics" : {
                        "retweet_count": "retweet_count",
                        "reply_count": "reply_count",
                        "quote_count": "quote_count",
                        "bookmark_count": "bookmark_count"},
                     "url": "url"
                    },
    "created_at_format": "%a %b %d %H:%M:%S +0000 %Y",
    "api_token": "<YOUR_ACCESS_TOKEN>",
    "actor_id" : "heLL6fUofdPgRXZie",
    "base_directory": "TWEET_ARCHIEVE"
}
```

## Additional Information

- The project includes a `.gitignore` file to exclude unnecessary files from the Git repository. By default, it contains `apify_setup.json`.
- The codebase consists of two main files: `apify_code.py`, which contains the complete code for extraction and sending automated emails, and `apify_config.py`, which includes the code for extraction and segregation of tweets.
- Future cohorts or individuals working on this project next year or in the future need to integrate both code files and work on the algorithm to improve tweet segregation.