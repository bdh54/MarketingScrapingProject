import requests
import json
import os
import pandas as pd
import time

def create_sorted_ids_file(data_file):
    """
    Reads tweet IDs from a CSV file, sorts them, and writes them to a new file.
    """
    # Read IDs from the CSV file into a DataFrame
    df = pd.read_csv(data_file, header=None, names=['ID'])
    
    # Sort the DataFrame by ID in descending order
    df_sorted = df.sort_values(by='ID', ascending=False)
    
    # Construct the path for the new sorted CSV file
    dir_path = os.path.dirname(data_file)
    sorted_file_path = os.path.join(dir_path, 'sorted_ids.csv')
    
    # Write the sorted IDs to the new CSV file, without the index or header
    df_sorted.to_csv(sorted_file_path, index=False, header=False)
    
    return sorted_file_path

def get_rate_limit_reset_time(headers):
    """
    Extract rate limit reset time from response headers.
    """
    if 'x-rate-limit-reset' in headers:
        return int(headers['x-rate-limit-reset'])
    return time.time() + 900  # Default to 15 minutes if header is missing

def wait_for_rate_limit(reset_time):
    """
    Pauses execution until the rate limit reset time.
    """
    sleep_duration = max(reset_time - time.time(), 0) + 10  # Adding a buffer
    print(f"Rate limit exceeded. Waiting for {sleep_duration} seconds.")
    time.sleep(sleep_duration)

def loop_through_ids(data_file_path, bearer_token, limit=None):
    # Simplified fields for demonstration
    tweet_fields = "id,text,author_id,created_at,public_metrics"

    df = pd.read_csv(data_file_path, header=None)
    ids = df[0].tolist()
    print(f"Total IDs: {len(ids)}")

    processed_counter = 0
    for id_ in ids[:limit]:  # Limit the number of IDs to process if specified
        url = f"https://api.twitter.com/2/tweets/{id_}?tweet.fields={tweet_fields}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tweet = response.json()
            save_tweet_data(tweet, processed_counter)
            processed_counter += 1
            print(f"Processed {processed_counter}/{len(ids)} tweets.")
        elif response.status_code == 429:
            wait_for_rate_limit(get_rate_limit_reset_time(response.headers))
        else:
            print(f"Failed to fetch tweet ID {id_}: HTTP {response.status_code}.")

def save_tweet_data(tweet, counter):
    """
    Saves the tweet data to a JSON file.
    """
    filename = f'tweet_data_{int(counter / 100)}.json'
    with open(filename, 'a') as fp:
        json.dump(tweet, fp, indent=4)
        fp.write('\n')

def main():
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "BREARER_TOKEN_HERE")
    data_file_path = "FILE_PATH_HERE" 
    
    test_run = input("Do you want to perform a test run? (yes/no): ").lower() == 'yes'
    limit = None
    if test_run:
        try:
            limit = int(input("How many tweets for the test run?: "))
        except ValueError:
            print("Invalid number. Exiting...")
            return

    sorted_data_file = create_sorted_ids_file(data_file_path)
    loop_through_ids(sorted_data_file, bearer_token, limit)

if __name__ == "__main__":
    main()

