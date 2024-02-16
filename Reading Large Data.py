import tweepy
import pandas as pd

# Twitter API credentials
api_key = "YOUR_API_KEY"
api_secret_key = "YOUR_API_SECRET_KEY"
access_token = "YOUR_ACCESS_TOKEN"
access_token_secret = "YOUR_ACCESS_TOKEN_SECRET"

# Authenticate with the Twitter API
auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Function to fetch tweets by user account and return a list of dictionaries
def fetch_tweets(user_account):
    tweets = api.user_timeline(screen_name=user_account, count=10)  # Adjust count as needed
    tweets_data = []
    for tweet in tweets:
        tweets_data.append({
            'tweet_id': tweet.id_str,
            'text': tweet.text,
            'created_at': tweet.created_at,
            'user': tweet.user.screen_name,
            # Add more metadata as needed
        })
    return tweets_data

# Example: Fetch tweets for a single user account
user_accounts = ['user_account_1', 'user_account_2']  # Replace with actual user accounts
all_tweets = []
for account in user_accounts:
    all_tweets.extend(fetch_tweets(account))

# Create DataFrame
df_tweets = pd.DataFrame(all_tweets)

# Save DataFrame to CSV
df_tweets.to_csv('/mnt/data/tweets_data.csv', index=False)
