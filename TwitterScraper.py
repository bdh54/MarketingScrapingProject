import requests

import json

def loopThroughIds (dataFile, bearerToken):
  ##with open(dataFile, 'r') as file:
  with open(dataFile, 'r') as file:
        ids = file.readlines()
        print(len(ids))
  counter = 0
  for id in ids:
    url = f"https://api.twitter.com/2/tweets/{id}"
    header = (bearerToken) #header or some authenticator
    response = requests.get(url, header)
    tweet = json.loads(response.text)
    save(tweet, counter)
    counter += 1

def save(tweet, counter):
  filename = 'X.data.file' + str(int(counter / 100000))
  with open(filename, 'a') as fp:
        json.dump(tweet, fp, indent=4)
  

def main():
  bearerToken = "Bearer " + (str)(input("Please enter the bearer token for X: "))
  dataFile = input("Please enter the data file you want to parse: ")
  loopThroughIds(dataFile,bearerToken)

if __name__ == "__main__":
  main()
