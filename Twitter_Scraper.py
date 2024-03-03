import requests
import json
import os

def create_sorted_ids_file(data_file):
    with open(data_file, 'r') as file:
        ids = file.readlines()
    
    sorted_ids = sorted(ids, key=lambda x: int(x.strip()), reverse=True)
    
    dir_path = os.path.dirname(data_file)
    sorted_file_path = os.path.join(dir_path, 'sorted_ids.txt')
    
    with open(sorted_file_path, 'w') as file:
        for id_ in sorted_ids:
            file.write(f"{id_}")
    
    return sorted_file_path

def loop_through_ids(data_file_path, bearer_token):
    with open(data_file_path, 'r') as file:
        ids = file.readlines()
        print(len(ids))
    
    counter = 0
    for id_ in ids:
        id_ = id_.strip()  # Remove newline characters
        url = f"https://api.twitter.com/2/tweets/{id_}"
        headers = {"Authorization": bearer_token}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            tweet = json.loads(response.text)
            save_tweet_data(tweet, counter)
            counter += 1
        else:
            print(f"Failed to fetch tweet ID {id_}: HTTP {response.status_code}")

def save_tweet_data(tweet, counter):
    filename = 'X.data.file' + str(int(counter / 100000))
    with open(filename, 'a') as fp:
        json.dump(tweet, fp, indent=4)

def main():
    bearer_token = "Bearer " + input("Please enter the bearer token for X: ")
    data_file_path = input("Please enter the data file path you want to parse: ")
    loop_through_ids(data_file_path, bearer_token)

if __name__ == "__main__":
    main()
