import json
import matplotlib.pyplot as plt
import geopandas as gpd
from collections import Counter
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Define the path to the JSON file
file_path = "/Users/alexkim/MarketingScrapingProject/senators_production_geo_map_stage2_senators/tweet_batch_1716173464.json"

# Load the JSON data
with open(file_path, 'r') as file:
    tweets = json.load(file)

# Extract locations
locations = [tweet['location'] for tweet in tweets if tweet.get('location') and tweet['location'] != 'N/A']

# Count the most common locations
location_counts = Counter(locations)

# Print some basic statistics
print("Total tweets:", len(tweets))
print("\nMost common locations:")
for location, count in location_counts.most_common(5):
    print(f"{location}: {count} tweets")

# Most active users
usernames = [tweet['username'] for tweet in tweets if tweet.get('username')]
most_active_users = Counter(usernames).most_common(5)
print("\nMost active users:")
for username, count in most_active_users:
    print(f"{username}: {count} tweets")

# Most common hashtags
hashtags = []
for tweet in tweets:
    entities = tweet.get('full_tweet_data', {}).get('entities', {})
    for hashtag in entities.get('hashtags', []):
        hashtags.append(hashtag['tag'])

most_common_hashtags = Counter(hashtags).most_common(5)
print("\nMost common hashtags:")
for hashtag, count in most_common_hashtags:
    print(f"#{hashtag}: {count} times")

# Initialize geolocator
geolocator = Nominatim(user_agent="tweet_visualizer")

def get_coordinates(location):
    try:
        # Geocode the location to get latitude and longitude
        geo = geolocator.geocode(location, timeout=10)
        if geo:
            return (geo.longitude, geo.latitude)
    except GeocoderTimedOut:
        print(f"Geocoding timed out for location: {location}")
    return None

# Map locations to their coordinates
coordinates = {}
for location in location_counts:
    coord = get_coordinates(location)
    if coord:
        coordinates[location] = coord

# Load the shapefile
world = gpd.read_file("/Users/alexkim/MarketingScrapingProject/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")

# Plotting the world map with all country outlines
fig, ax = plt.subplots(1, 1, figsize=(15, 10))

# Plot the base map of all countries
world.boundary.plot(ax=ax, linewidth=1)

# Plot the locations
for location, count in location_counts.items():
    if location in coordinates:
        lon, lat = coordinates[location]
        ax.scatter(lon, lat, s=count/100, color='red', alpha=0.6, edgecolor='k')

ax.set_title("Geographic Distribution of Tweets")
plt.show()
