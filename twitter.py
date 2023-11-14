# THIS WORKS

import tweepy

consumer_key         = "Clv613899drC0uSPpaMNcQYEP"
consumer_secret      = "RCElHgHfytB7UIHtr9XLnP8V5KikBwqw09zUCMh1okhUQ1LUzs"
bearer_token    = "AAAAAAAAAAAAAAAAAAAAADvsqgEAAAAA63r2%2BiFLoCvbJu%2BGgZkn15hRpug%3DrVhaivZFcTXjbHKGDutN2Q109vvtm1TrlEaAjlYFOBZfFmamTs"
access_token    = "706530790591430656-CqShCARbcxp7BFUx7zKYW4SXc5JeQM5"
access_token_secret   = "ePlprSO2s10u4YIhsXA69wiw9rJ2hmpfwnaFHdyOaw8Wx"

# You can authenticate as your app with just your bearer token
client = tweepy.Client(bearer_token=bearer_token)

# You can provide the consumer key and secret with the access token and access
# token secret to authenticate as a user
client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)