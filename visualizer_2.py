import json
import matplotlib.pyplot as plt
import geopandas as gpd

# Define the paths to the JSON files
original_file_path = "/Users/alexkim/MarketingScrapingProject/senators_production_geo_map_stage2_senators/tweet_batch_1716173464.json"
geolocated_file_path = "/Users/alexkim/MarketingScrapingProject/tweet_batch_1716173464_geolocated.json"

# Function to safely load JSON data
def load_json_safely(file_path):
    tweets = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # Remove any leading/trailing whitespace
            if not line:
                continue  # Skip empty lines
            try:
                tweet = json.loads(line)
                tweets.append(tweet)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                continue
    return tweets

# Load the original and geolocated JSON data
original_tweets = load_json_safely(original_file_path)
geolocated_tweets = load_json_safely(geolocated_file_path)

# Extract coordinates from the original tweets (those with a 'location')
confirmed_coordinates = []
for tweet in original_tweets:
    if isinstance(tweet, dict):  # Ensure tweet is a dictionary
        if 'location' in tweet and tweet['location'] != 'N/A':
            if 'entities' in tweet['full_tweet_data'] and 'urls' in tweet['full_tweet_data']['entities']:
                # Assuming 'lon' and 'lat' are stored in a specific way
                lon = tweet['full_tweet_data']['entities']['urls'][0].get('lon', None)
                lat = tweet['full_tweet_data']['entities']['urls'][0].get('lat', None)
                if lon and lat:
                    confirmed_coordinates.append((lon, lat))

# Extract coordinates from the geolocated tweets (those with an 'estimated_location')
estimated_coordinates = []
for tweet in geolocated_tweets:
    if isinstance(tweet, dict):  # Ensure tweet is a dictionary
        if 'estimated_location' in tweet:
            lon = tweet['estimated_location'].get('lon', None)
            lat = tweet['estimated_location'].get('lat', None)
            if lon and lat:
                estimated_coordinates.append((lon, lat))

# Load the shapefile
world = gpd.read_file("/Users/alexkim/MarketingScrapingProject/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")

# Plotting the world map with all country outlines
fig, ax = plt.subplots(1, 1, figsize=(15, 10))

# Plot the base map of all countries
world.boundary.plot(ax=ax, linewidth=1)

# Plot the confirmed locations (red dots)
for lon, lat in confirmed_coordinates:
    ax.scatter(lon, lat, s=10, color='red', alpha=0.6, edgecolor='k')

# Plot the estimated locations (green dots)
for lon, lat in estimated_coordinates:
    ax.scatter(lon, lat, s=10, color='green', alpha=0.6, edgecolor='k')

ax.set_title("Geographic Distribution of Tweets with Estimated Locations")
plt.show()
